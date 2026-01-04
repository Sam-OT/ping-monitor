"""
Ping service module for executing ping commands and calculating statistics.
"""
import subprocess
import platform
import re
import statistics
import time
import threading
import random
from typing import List, Dict, Callable, Optional


class PingResult:
    """Container for ping test results and statistics."""

    def __init__(self, server_name: str, ip: str, latencies: List[float]):
        self.server_name = server_name
        self.ip = ip
        self.latencies = latencies
        self.successful_pings = len(latencies)

    @property
    def mean(self) -> Optional[float]:
        """Calculate mean latency in milliseconds."""
        return statistics.mean(self.latencies) if self.latencies else None

    @property
    def min(self) -> Optional[float]:
        """Get minimum latency in milliseconds."""
        return min(self.latencies) if self.latencies else None

    @property
    def max(self) -> Optional[float]:
        """Get maximum latency in milliseconds."""
        return max(self.latencies) if self.latencies else None

    @property
    def std_dev(self) -> Optional[float]:
        """Calculate standard deviation of latencies."""
        return statistics.stdev(self.latencies) if len(self.latencies) > 1 else 0.0

    def __str__(self):
        """String representation for batch results."""
        if self.mean is not None:
            # Format to match Results pane display
            display_name = self.server_name[:24] if len(self.server_name) > 24 else self.server_name
            mean_str = f"{self.mean:.0f}ms"
            min_str = f"{self.min:.0f}ms"
            max_str = f"{self.max:.0f}ms"
            std_str = f"{self.std_dev:.1f}ms"
            return f"{display_name:<25} {mean_str:<12} {min_str:<12} {max_str:<12} {std_str:<12}"
        return f"{self.server_name:<25} {'Failed':<12}"


class PingService:
    """Service for executing ping commands and gathering statistics."""

    def __init__(self):
        self.system = platform.system()

    def ping_once(self, ip: str) -> Optional[float]:
        """
        Execute a single ping to an IP address.

        Args:
            ip: IP address or hostname to ping

        Returns:
            Latency in milliseconds, or None if ping failed
        """
        try:
            # Platform-specific ping command
            if self.system == "Windows":
                # Windows: ping -n 1 -w 5000 IP
                # CREATE_NO_WINDOW prevents console window from appearing
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "5000", ip],
                    capture_output=True,
                    text=True,
                    timeout=6,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                # Parse output: "time=XXms" or "time<1ms"
                match = re.search(r'time[=<](\d+)ms', result.stdout, re.IGNORECASE)
                if match:
                    return float(match.group(1))
                # Alternative format: "Average = XXms"
                match = re.search(r'Average\s*=\s*(\d+)ms', result.stdout, re.IGNORECASE)
                if match:
                    return float(match.group(1))
            else:
                # Linux/Mac: ping -c 1 -W 5 IP
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "5", ip],
                    capture_output=True,
                    text=True,
                    timeout=6
                )
                # Parse output: "time=XX.X ms"
                match = re.search(r'time=(\d+\.?\d*)\s*ms', result.stdout)
                if match:
                    return float(match.group(1))

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        return None

    def ping_continuous(
        self,
        server_name: str,
        ip: str,
        target_ping_count: int,
        progress_callback: Optional[Callable[[float, int, int], None]] = None,
        cancel_event: Optional[threading.Event] = None,
        server_index: int = 0
    ) -> PingResult:
        """
        Ping an IP address a specified number of times.

        Args:
            server_name: Name of the server being pinged
            ip: IP address to ping
            target_ping_count: Number of pings to perform
            progress_callback: Optional callback(latency, current, total) called after each ping
            cancel_event: Optional threading.Event to signal cancellation
            server_index: Index for calculating staggered start offset (0.1s per index)

        Returns:
            PingResult object with statistics
        """
        # Add fixed offset (0.1 seconds per server index) to stagger pings across servers
        offset_seconds = server_index * 0.1
        time.sleep(offset_seconds)

        # Check cancellation before starting
        if cancel_event and cancel_event.is_set():
            return PingResult(server_name, ip, [])

        latencies = []
        start_time = time.time()

        # Ping exactly target_ping_count times
        for ping_number in range(1, target_ping_count + 1):
            # Check if cancellation was requested
            if cancel_event and cancel_event.is_set():
                break

            latency = self.ping_once(ip)

            if latency is not None:
                latencies.append(latency)

            # Call progress callback
            if progress_callback:
                progress_callback(latency, ping_number, target_ping_count)

            # Wait for the rest of the second (to maintain ~1 ping/second)
            # Only sleep if not the last ping
            if ping_number < target_ping_count:
                elapsed = time.time() - start_time
                next_ping_time = ping_number  # Should ping at 1s, 2s, 3s intervals
                time_to_wait = next_ping_time - elapsed

                if time_to_wait > 0:
                    # Check if we should cancel during sleep
                    if cancel_event:
                        # Sleep in small increments to be responsive to cancellation
                        sleep_remaining = time_to_wait
                        while sleep_remaining > 0 and not cancel_event.is_set():
                            time.sleep(min(0.1, sleep_remaining))
                            sleep_remaining -= 0.1
                    else:
                        time.sleep(time_to_wait)

        return PingResult(server_name, ip, latencies)

    def validate_ip(self, ip: str) -> bool:
        """
        Validate an IP address or hostname by attempting to ping it.

        Args:
            ip: IP address or hostname to validate

        Returns:
            True if the IP is valid and reachable, False otherwise
        """
        # First check basic format (simple validation)
        if not ip or not ip.strip():
            return False

        # Try to ping it once
        result = self.ping_once(ip)
        return result is not None

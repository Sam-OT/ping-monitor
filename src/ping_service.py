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
                # Windows: ping -n 1 -w 1000 IP
                # CREATE_NO_WINDOW prevents console window from appearing
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", ip],
                    capture_output=True,
                    text=True,
                    timeout=2,
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
                # Linux/Mac: ping -c 1 -W 1 IP
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip],
                    capture_output=True,
                    text=True,
                    timeout=2
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
        duration_seconds: int,
        progress_callback: Optional[Callable[[float, int, int], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> PingResult:
        """
        Ping an IP address continuously for a specified duration.

        Args:
            server_name: Name of the server being pinged
            ip: IP address to ping
            duration_seconds: How long to ping (in seconds)
            progress_callback: Optional callback(latency, current, total) called after each ping
            cancel_event: Optional threading.Event to signal cancellation

        Returns:
            PingResult object with statistics
        """
        # Add random offset (0-0.9 seconds) to stagger pings across servers
        initial_offset = random.uniform(0, 0.9)
        time.sleep(initial_offset)

        latencies = []
        start_time = time.time()

        # Ping once per second for the specified duration
        ping_count = 0
        while time.time() - start_time < duration_seconds:
            # Check if cancellation was requested
            if cancel_event and cancel_event.is_set():
                break
            latency = self.ping_once(ip)

            if latency is not None:
                latencies.append(latency)

            ping_count += 1

            # Call progress callback with ping count
            if progress_callback:
                progress_callback(latency, ping_count, duration_seconds)

            # Wait for the rest of the second
            elapsed = time.time() - start_time
            next_ping_time = ping_count  # Should ping at 1s, 2s, 3s, etc.
            if next_ping_time > elapsed:
                time.sleep(next_ping_time - elapsed)

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

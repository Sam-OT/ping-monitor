"""
Ping service module for executing ping commands and calculating statistics.
"""
import subprocess
import platform
import re
import statistics
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
            return f"{self.server_name}: {self.mean:.2f}ms"
        return f"{self.server_name}: Failed"


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
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", ip],
                    capture_output=True,
                    text=True,
                    timeout=2
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
        progress_callback: Optional[Callable[[float, int, int], None]] = None
    ) -> PingResult:
        """
        Ping an IP address continuously for a specified duration.

        Args:
            server_name: Name of the server being pinged
            ip: IP address to ping
            duration_seconds: How long to ping (in seconds)
            progress_callback: Optional callback(latency, current, total) called after each ping

        Returns:
            PingResult object with statistics
        """
        latencies = []

        # Ping approximately once per second
        for i in range(duration_seconds):
            latency = self.ping_once(ip)

            if latency is not None:
                latencies.append(latency)

            # Call progress callback if provided
            if progress_callback:
                progress_callback(latency, i + 1, duration_seconds)

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

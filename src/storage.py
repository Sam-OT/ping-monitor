"""
Storage module for managing server configurations and results.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class Server:
    """Represents a server with a name and IP address."""

    def __init__(self, name: str, ip: str):
        self.name = name
        self.ip = ip

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {"name": self.name, "ip": self.ip}

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'Server':
        """Create Server from dictionary."""
        return Server(data["name"], data["ip"])

    def __eq__(self, other):
        """Check equality based on name."""
        if isinstance(other, Server):
            return self.name == other.name
        return False

    def __hash__(self):
        """Hash based on name for set operations."""
        return hash(self.name)


class Storage:
    """Manages persistent storage of server configurations and results."""

    def __init__(self, base_dir: str = None):
        """
        Initialize storage manager.

        Args:
            base_dir: Base directory for data and results. Defaults to project root.
        """
        if base_dir is None:
            # Use the directory containing the src folder
            base_dir = Path(__file__).parent.parent

        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.results_dir = self.base_dir / "results"
        self.config_file = self.data_dir / "servers.json"

        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

    def load_servers(self) -> List[Server]:
        """
        Load server configurations from JSON file.

        Returns:
            List of Server objects (sorted alphabetically by name)
        """
        if not self.config_file.exists():
            # Return default servers if no config exists
            return self._create_default_config()

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                servers = [Server.from_dict(s) for s in data.get("servers", [])]
                # Always return sorted list
                return sorted(servers, key=lambda s: s.name.lower())
        except (json.JSONDecodeError, KeyError, IOError):
            # If file is corrupted, create default config
            return self._create_default_config()

    def save_servers(self, servers: List[Server]) -> bool:
        """
        Save server configurations to JSON file.

        Args:
            servers: List of Server objects to save

        Returns:
            True if save was successful, False otherwise
        """
        try:
            data = {
                "servers": [s.to_dict() for s in servers],
                "last_modified": datetime.now().isoformat()
            }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except IOError:
            return False

    def add_server(self, servers: List[Server], name: str, ip: str) -> tuple[List[Server], bool, str]:
        """
        Add a new server to the list.

        Args:
            servers: Current list of servers
            name: Server name
            ip: Server IP address

        Returns:
            Tuple of (updated server list, success bool, error message)
        """
        # Check for duplicate name
        if any(s.name == name for s in servers):
            return servers, False, f"Server name '{name}' already exists"

        # Add new server
        new_server = Server(name, ip)
        updated_servers = servers + [new_server]

        # Save to file
        if self.save_servers(updated_servers):
            return updated_servers, True, ""
        else:
            return servers, False, "Failed to save configuration"

    def remove_server(self, servers: List[Server], name: str) -> tuple[List[Server], bool]:
        """
        Remove a server from the list.

        Args:
            servers: Current list of servers
            name: Name of server to remove

        Returns:
            Tuple of (updated server list, success bool)
        """
        updated_servers = [s for s in servers if s.name != name]

        if self.save_servers(updated_servers):
            return updated_servers, True
        else:
            return servers, False

    def sort_servers(self, servers: List[Server]) -> List[Server]:
        """
        Sort servers alphabetically by name.

        Args:
            servers: List of servers to sort

        Returns:
            Sorted list of servers
        """
        sorted_servers = sorted(servers, key=lambda s: s.name.lower())
        self.save_servers(sorted_servers)
        return sorted_servers

    def save_batch_results(self, results: List[str], timestamp: str = None) -> tuple[bool, str]:
        """
        Save batch ping results to a timestamped file.

        Args:
            results: List of result strings (one per server)
            timestamp: Optional timestamp string. If None, current time is used.

        Returns:
            Tuple of (success bool, file path)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"ping_results_{timestamp}.txt"
        filepath = self.results_dir / filename

        try:
            with open(filepath, 'w') as f:
                f.write(f"Ping Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                # Add header matching Results pane format
                f.write(f"{'Server':<25} {'Mean':<12} {'Min':<12} {'Max':<12} {'Std Dev':<12}\n")
                f.write("-" * 80 + "\n")
                for result in results:
                    f.write(result + "\n")

            return True, str(filepath)
        except IOError:
            return False, ""

    def _create_default_config(self) -> List[Server]:
        """
        Create default server configuration.

        Returns:
            List of default servers
        """
        default_servers = [
            Server("Google DNS", "8.8.8.8"),
            Server("Cloudflare DNS", "1.1.1.1"),
        ]

        self.save_servers(default_servers)
        return default_servers

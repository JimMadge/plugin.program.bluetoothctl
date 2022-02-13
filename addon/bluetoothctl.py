from __future__ import annotations
import subprocess
from .logging import loginfo, logerror


class Bluetoothctl:
    """Interact with the 'bluetoothctl' utility"""

    def __init__(self) -> None:
        self.executable = '/usr/bin/bluetoothctl'
        self.scan_timeout = 5

    def scan(self) -> None:
        """
        Scan for available devices

        Returns: A CompletedProcess instance

        Raises:
            CalledProcessError: If bluetoothctl returns a non-zero exit code
        """
        command = [
            self.executable, '--timeout', str(self.scan_timeout), 'scan', 'on'
        ]

        return subprocess.run(command, capture_output=True, encoding='utf8',
                              check=True)

    def get_devices(self) -> dict[str, str]:
        """Create Dict of available devices"""
        command = [self.executable, 'devices']

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
        except subprocess.CalledProcessError:
            return {}

        return self.parse_devices_list(stdout)

    def get_paired_devices(self) -> dict[str, str]:
        """Create Dict of paired devices"""
        command = [self.executable, 'paired-devices']

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
        except subprocess.CalledProcessError:
            return {}

        return self.parse_devices_list(stdout)

    @staticmethod
    def parse_devices_list(stdout: str) -> dict[str, str]:
        """
        Construct a dictionary of friendly_name: device_address from
        bluetoothctl stdout
        """
        # The stdout of 'bluetoothctl devices' is in the format
        # Device <device_address> <friendly_name>
        devices = {
            item[2]: item[1] for item in
            (line.split() for line in stdout.splitlines())
        }

        return devices

    def connect(self, address: str) -> str:
        """Connect to a device"""
        command = [self.executable, 'connect', address]

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
            loginfo(stdout)
            return stdout
        except subprocess.CalledProcessError as e:
            logerror(e.output)
            return str(e.output)

    def disconnect(self, address: str) -> str:
        """Disconnect from a device"""
        command = [self.executable, 'disconnect', address]

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
            loginfo(stdout)
            return stdout
        except subprocess.CalledProcessError as e:
            logerror(e.output)
            return str(e.output)

    def pair(self, address: str) -> str:
        """Pair with a device (non-interactive"""
        command = [self.executable, 'pair', address]

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
            loginfo(stdout)
            return stdout
        except subprocess.CalledProcessError as e:
            logerror(e.output)
            return str(e.output)

    def remove(self, address: str) -> str:
        """Remove device (revoke pairing)"""
        command = [self.executable, 'remove', address]

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
            loginfo(stdout)
            return stdout
        except subprocess.CalledProcessError as e:
            logerror(e.output)
            return str(e.output)

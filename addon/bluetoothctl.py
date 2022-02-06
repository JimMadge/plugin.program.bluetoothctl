import subprocess
from .logging import loginfo, logerror


class Bluetoothctl:
    """Interact with the 'bluetoothctl' utility"""

    def __init__(self) -> None:
        self.executable = '/usr/bin/bluetoothctl'
        self.scan_timeout = 5

    def scan(self) -> None:
        """Scan for available devices"""
        command = [
            self.executable, '--timeout', str(self.scan_timeout), 'scan', 'on'
        ]

        subprocess.run(command, check=True)

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

    def connect(self, address: str) -> None:
        """Connect to a device"""
        command = ['connect', address]

        try:
            stdout = subprocess.check_output(command, encoding='utf8')
            loginfo(stdout)
        except subprocess.CalledProcessError:
            logerror(stdout)
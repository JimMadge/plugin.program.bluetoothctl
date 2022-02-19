from __future__ import annotations
from typing import Any
import subprocess
from subprocess import CompletedProcess


class Bluetoothctl:
    """Interact with the 'bluetoothctl' utility"""
    _run_args = {
        'capture_output': True,
        'encoding': 'utf8',
    }  # type: dict[str, Any]

    def __init__(self) -> None:
        self.executable = '/usr/bin/bluetoothctl'
        self.scan_timeout = 5

    def scan(self) -> CompletedProcess[str]:
        """
        Scan for available devices

        Returns: A CompletedProcess instance
        """
        command = [self.executable, '--timeout', str(self.scan_timeout),
                   'scan', 'on']
        return subprocess.run(command, **self._run_args)

    def get_devices(self) -> dict[str, str]:
        """
        List available devices

        Returns: Dict of available device

        Raises:
            CalledProcessError: if bluetoothctl has a non-zero exit status
        """
        command = [self.executable, 'devices']

        process = subprocess.run(command, check=True, **self._run_args)
        return self.parse_devices_list(process.stdout)

    def get_paired_devices(self) -> dict[str, str]:
        """
        List paired devices

        Returns: Dict of available device

        Raises:
            CalledProcessError: if bluetoothctl has a non-zero exit status
        """
        command = [self.executable, 'paired-devices']

        process = subprocess.run(command, check=True, **self._run_args)
        return self.parse_devices_list(process.stdout)

    @staticmethod
    def parse_devices_list(stdout: str) -> dict[str, str]:
        """
        Identify devices from bluetoothctl `devices` or `paired-devices` output

        Returns: Dict of friendly_name: device_address
        """
        # The stdout of 'bluetoothctl devices' is in the format
        # Device <device_address> <friendly_name>
        devices = {
            item[2]: item[1] for item in
            (line.split() for line in stdout.splitlines())
        }

        return devices

    def connect(self, address: str) -> CompletedProcess[str]:
        """
        Connect to a device

        Returns: A CompletedProcess instance
        """
        command = [self.executable, 'connect', address]
        return subprocess.run(command, **self._run_args)

    def disconnect(self, address: str) -> CompletedProcess[str]:
        """
        Disconnect from a device

        Returns: A CompletedProcess instance
        """
        command = [self.executable, 'disconnect', address]
        return subprocess.run(command, **self._run_args)

    def pair(self, address: str) -> CompletedProcess[str]:
        """
        Pair with a device (non-interactive)

        Returns: A CompletedProcess instance
        """
        command = [self.executable, 'pair', address]
        return subprocess.run(command, **self._run_args)

    def remove(self, address: str) -> CompletedProcess[str]:
        """
        Remove device (revoke pairing)

        Returns: A CompletedProcess instance
        """
        command = [self.executable, 'remove', address]
        return subprocess.run(command, **self._run_args)

    def trust(self, address: str) -> CompletedProcess[str]:
        """
        Trust a device

        Returns: A CompletedProcess instance
        """
        command = [self.executable, 'trust', address]
        return subprocess.run(command, **self._run_args)

    def untrust(self, address: str) -> CompletedProcess[str]:
        """
        Revoke trust in a device

        Returns: A CompletedProcess instance
        """
        command = [self.executable, 'untrust', address]
        return subprocess.run(command, **self._run_args)

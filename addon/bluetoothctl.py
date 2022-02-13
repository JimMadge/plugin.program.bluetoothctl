from __future__ import annotations
from typing import Any
import subprocess
from subprocess import CompletedProcess
from .logging import loginfo, logerror


class Bluetoothctl:
    """Interact with the 'bluetoothctl' utility"""
    _run_args = {
        'capture_output': True,
        'encoding': 'utf8',
        'check': True
    }  # type: dict[str, Any]

    def __init__(self) -> None:
        self.executable = '/usr/bin/bluetoothctl'
        self.scan_timeout = 5

    def scan(self) -> CompletedProcess[str]:
        """
        Scan for available devices

        Returns: A CompletedProcess instance

        Raises:
            CalledProcessError: If bluetoothctl returns a non-zero exit code
        """
        command = [
            self.executable, '--timeout', str(self.scan_timeout), 'scan', 'on'
        ]

        return subprocess.run(command, **self._run_args)

    def get_devices(self) -> dict[str, str]:
        """
        List available devices

        Returns: Dict of available device

        Raises:
            CalledProcessError: If bluetoothctl returns a non-zero exit code
        """
        command = [self.executable, 'devices']

        process = subprocess.run(command, **self._run_args)
        return self.parse_devices_list(process.stdout)

    def get_paired_devices(self) -> dict[str, str]:
        """
        List paired devices

        Returns: Dict of available device

        Raises:
            CalledProcessError: If bluetoothctl returns a non-zero exit code
        """
        command = [self.executable, 'paired-devices']

        process = subprocess.run(command, **self._run_args)
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

        Raises:
            CalledProcessError: If bluetoothctl returns a non-zero exit code
        """
        command = [self.executable, 'connect', address]

        return subprocess.run(command, **self._run_args)

    def disconnect(self, address: str) -> CompletedProcess[str]:
        """
        Disconnect from a device

        Returns: A CompletedProcess instance

        Raises:
            CalledProcessError: If bluetoothctl returns a non-zero exit code
        """
        command = [self.executable, 'disconnect', address]

        return subprocess.run(command, **self._run_args)

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

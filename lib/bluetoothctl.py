import subprocess


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

    def devices(self) -> dict[str, str]:
        """Create Dict of available devices"""
        command = [self.executable, 'devices']

        try:
            result = subprocess.run(command, check=True, capture_output=True,
                                    encoding='utf8')
        except subprocess.CalledProcessError:
            return {}

        return dict(
            (item[2], item[1]) for item in
            (line.split() for line in result.stdout.splitlines())
        )

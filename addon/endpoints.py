from __future__ import annotations
import urllib.parse


class Endpoints:
    def __init__(self, base_url: str):
        """
        Object which constructs endpoints for the various modes of the plugin.

        Args:
            base_url: The FQDN on the plugin
        """
        self.base_url = base_url

    def build_url(self, query: dict[str, str]) -> str:
        """
        Construct a url to recall this script with a set of arguments encoded
        in the query string.

        Args:
            query: Dict of arguments
        """
        return ''.join([self.base_url, '?', urllib.parse.urlencode(query)])

    def build_url_device(self, device: str, address: str, paired: bool) -> str:
        """
        Construct a url for the connect entry point.

        Args:
            device: Name of device
            address: Address of device
            paired: Whether the device is paired
        """
        return self.build_url(
            {'mode': 'device', 'device': device, 'address': address,
             'paired': str(paired)}
        )

    def build_url_connect(self, device: str, address: str) -> str:
        """
        Construct a url for the connect entry point.

        Args:
            device: Name of device
            address: Address of device
        """
        return self.build_url(
            {'mode': 'connect', 'device': device, 'address': address}
        )

    def build_url_disconnect(self, device: str, address: str) -> str:
        """
        Construct a url for the disconnect entry point.

        Args:
            device: Name of device
            address: Address of device
        """
        return self.build_url(
            {'mode': 'disconnect', 'device': device, 'address': address}
        )

    def build_url_pair(self, device: str, address: str) -> str:
        """
        Construct a url for the pair entry point.

        Args:
            device: Name of device
            address: Address of device
        """
        return self.build_url(
            {'mode': 'pair', 'device': device, 'address': address}
        )

    def build_url_remove(self, device: str, address: str) -> str:
        """
        Construct a url for the remove entry point.

        Args:
            device: Name of device
            address: Address of device
        """
        return self.build_url(
            {'mode': 'remove', 'device': device, 'address': address}
        )

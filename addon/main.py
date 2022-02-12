from collections.abc import Generator
from contextlib import contextmanager
import urllib.parse
import xbmc  # type: ignore
import xbmcaddon  # type: ignore
import xbmcgui  # type: ignore
import xbmcplugin  # type: ignore
from addon.bluetoothctl import Bluetoothctl
from addon.logging import loginfo


@contextmanager
def busy_dialog() -> Generator[None, None, None]:
    """
    Display a busy dialog box
    """
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


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


def main(base_url: str, addon_handle: str, args: dict[str, str]):
    # Create endpoint generating object
    endpoints = Endpoints(base_url)

    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')

    # Get 'mode' argument, default to None
    mode = args.get('mode', None)

    if mode is None:
        # Initial entry point
        url = endpoints.build_url({'mode': 'available_devices'})
        li = xbmcgui.ListItem('Available Devices')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        url = endpoints.build_url({'mode': 'paired_devices'})
        li = xbmcgui.ListItem('Paired Devices')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'available_devices':
        # Available devices entry point
        bt = Bluetoothctl()
        with busy_dialog():
            bt.scan()
            devices = bt.get_devices()

        for device, address in devices.items():
            loginfo(f'listing device {device}')
            li = xbmcgui.ListItem(device)
            li.addContextMenuItems([
                ('Pair',
                 f'RunPlugin({endpoints.build_url_pair(device, address)})'),
                ('Connect',
                 f'RunPlugin({endpoints.build_url_connect(device, address)})'),
                ('Disconnect',
                 f'RunPlugin({endpoints.build_url_disconnect(device, address)})')
            ])
            xbmcplugin.addDirectoryItem(
                handle=addon_handle,
                url=endpoints.build_url_pair(device, address),
                listitem=li
            )

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'paired_devices':
        # Paired devices entry point
        bt = Bluetoothctl()
        with busy_dialog():
            devices = bt.get_paired_devices()

        for device, address in devices.items():
            loginfo(f'listing device {device}')
            li = xbmcgui.ListItem(device)
            li.addContextMenuItems([
                ('Connect',
                 f'RunPlugin({endpoints.build_url_connect(device, address)})'),
                ('Disconnect',
                 f'RunPlugin({endpoints.build_url_disconnect(device, address)})'),
                ('Un-pair',
                 f'RunPlugin({endpoints.build_url_remove(device, address)})')
            ])
            xbmcplugin.addDirectoryItem(
                handle=addon_handle,
                url=endpoints.build_url_connect(device, address),
                listitem=li
            )

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'connect':
        # Connect entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting connection to {device} {address}')
        message = bt.connect(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

    elif mode[0] == 'disconnect':
        # Disconnect entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting to disconnect from {device} {address}')
        message = bt.disconnect(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

    elif mode[0] == 'pair':
        # Pair entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting to pair with {device} {address}')
        message = bt.pair(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

    elif mode[0] == 'remove':
        # Remove entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting to remove {device} {address}')
        message = bt.remove(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

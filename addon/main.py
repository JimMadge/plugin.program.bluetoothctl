from subprocess import CalledProcessError
import xbmc  # type: ignore
import xbmcaddon  # type: ignore
import xbmcgui  # type: ignore
import xbmcplugin  # type: ignore
from .bluetoothctl import Bluetoothctl
from .busy_dialog import busy_dialog
from .endpoints import Endpoints
from .logging import logerror, logdebug, loginfo


def main(base_url: str, addon_handle: str, args: dict[str, str]) -> None:
    # Create endpoint generating object
    endpoints = Endpoints(base_url)

    # Create bluetoothctl object
    bt = Bluetoothctl()

    # Get addon name
    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')

    # Get 'mode' argument, default to None
    mode = args.get('mode', None)

    if mode is None:
        # Initial endpoint
        mode_entry(endpoints, addon_handle)
        return
    elif mode[0] == 'available_devices':
        # Available devices endpoint
        mode_available_devices(bt, endpoints, addon_handle)
    elif mode[0] == 'paired_devices':
        # Paired devices endpoint
        mode_paired_devices(bt, endpoints, addon_handle)

    if mode[0] in ['connect', 'disconnect', 'pair', 'remove']:
        device = args['device'][0]
        address = args['address'][0]

        if mode[0] == 'connect':
            # Connect endpoint
            mode_connect(bt, device, address, addon_name)
        elif mode[0] == 'disconnect':
            # Disconnect endpoint
            mode_disconnect(bt, device, address, addon_name)
        elif mode[0] == 'pair':
            # Pair endpoint
            mode_pair(bt, device, address, addon_name)
        elif mode[0] == 'remove':
            # Remove endpoint
            mode_remove(bt, device, address, addon_name)


def mode_entry(endpoints: Endpoints, addon_handle: str) -> None:
    """Initial endpoint"""
    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=endpoints.build_url({'mode': 'available_devices'}),
        listitem=xbmcgui.ListItem('Available Devices'),
        isFolder=True
    )

    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=endpoints.build_url({'mode': 'paired_devices'}),
        listitem=xbmcgui.ListItem('Paired Devices'),
        isFolder=True
    )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_available_devices(bt: Bluetoothctl, endpoints: Endpoints,
                           addon_handle: str) -> None:
    with busy_dialog():
        try:
            process = bt.scan()
            logdebug(f'scanning succeeded.\nstdout: {process.stdout}')
        except CalledProcessError as e:
            logerror(f'scanning failed.\nreturn code: {e.returncode}\n'
                     f'stdout: {e.stdout}'
                     f'stderr: e.stderr)')
        devices = bt.get_devices()

    for device, address in devices.items():
        logdebug(f'listing device {device}')
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


def mode_paired_devices(bt: Bluetoothctl, endpoints: Endpoints,
                        addon_handle: str) -> None:
    with busy_dialog():
        devices = bt.get_paired_devices()

    for device, address in devices.items():
        logdebug(f'listing device {device}')
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


def mode_connect(bt: Bluetoothctl, device: str, address: str,
                 addon_name: str) -> None:

    loginfo(f'attempting connection to {device} {address}')
    with busy_dialog():
        message = bt.connect(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')


def mode_disconnect(bt: Bluetoothctl, device: str, address: str,
                    addon_name: str) -> None:
    loginfo(f'attempting to disconnect from {device} {address}')
    with busy_dialog():
        message = bt.disconnect(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')


def mode_pair(bt: Bluetoothctl, device: str, address: str,
              addon_name: str) -> None:
    loginfo(f'attempting to pair with {device} {address}')
    with busy_dialog():
        message = bt.pair(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')


def mode_remove(bt: Bluetoothctl, device: str, address: str,
                addon_name: str) -> None:
    loginfo(f'attempting to remove {device} {address}')
    with busy_dialog():
        message = bt.remove(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')

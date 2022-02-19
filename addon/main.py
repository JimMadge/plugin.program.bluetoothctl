from subprocess import CalledProcessError
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

    if mode[0] in ['device', 'connect', 'disconnect', 'pair', 'remove',
                   'trust', 'untrust']:
        device = args['device'][0]
        address = args['address'][0]

        if mode[0] == 'device':
            # Device actions endpoint
            paired = args['paired'][0]
            mode_device(bt, endpoints, device, address, paired, addon_handle)
        elif mode[0] == 'connect':
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
        elif mode[0] == 'trust':
            # Trust endpoint
            mode_trust(bt, device, address, addon_name)
        elif mode[0] == 'untrust':
            # Untrust endpoint
            mode_untrust(bt, device, address, addon_name)


def mode_entry(endpoints: Endpoints, addon_handle: str) -> None:
    """Initial endpoint"""
    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=endpoints.build_url({'mode': 'paired_devices'}),
        listitem=xbmcgui.ListItem('Paired Devices'),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=endpoints.build_url({'mode': 'available_devices'}),
        listitem=xbmcgui.ListItem('Available Devices'),
        isFolder=True
    )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_available_devices(bt: Bluetoothctl, endpoints: Endpoints,
                           addon_handle: str) -> None:
    with busy_dialog():
        process = bt.scan()

    if process.returncode == 0:
        logdebug(f'scanning succeeded.\nstdout: {process.stdout}')
    else:
        logerror(f'scanning failed.\nreturn code: {process.returncode}\n'
                 f'stdout: {process.stdout}'
                 f'stderr: process.stderr)')

    # Remove paired devices from list
    devices = get_available_devices(bt)
    paired_devices = get_paired_devices(bt)
    for device in paired_devices.keys():
        devices.pop(device, None)

    for device, address in devices.items():
        logdebug(f'listing device {device}')

        li = xbmcgui.ListItem(device)
        li.addContextMenuItems([
            ('Pair',
             f'RunPlugin({endpoints.build_url_pair(device, address)})'),
            ('Connect',
             f'RunPlugin({endpoints.build_url_connect(device, address)})'),
        ])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=endpoints.build_url_device(device, address, paired=False),
            listitem=li,
            isFolder=True
        )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_paired_devices(bt: Bluetoothctl, endpoints: Endpoints,
                        addon_handle: str) -> None:
    devices = get_paired_devices(bt)

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
            url=endpoints.build_url_device(device, address, paired=True),
            listitem=li,
            isFolder=True
        )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_device(bt: Bluetoothctl, endpoints: Endpoints, device: str,
                address: str, paired: str, addon_handle: str) -> None:
    logdebug(f'paired: {paired}')
    logdebug(f'type of paired: {type(paired)}')
    if paired == str(True):
        logdebug('paired == True')
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Connect"),
            url=endpoints.build_url_connect(device, address)
        )
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Disconnect"),
            url=endpoints.build_url_disconnect(device, address)
        )
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Unpair"),
            url=endpoints.build_url_disconnect(device, address)
        )
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Trust"),
            url=endpoints.build_url_trust(device, address)
        )
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Revoke trust"),
            url=endpoints.build_url_untrust(device, address)
        )
    elif paired == str(False):
        logdebug('paired == False')
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Pair"),
            url=endpoints.build_url_pair(device, address)
        )
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            listitem=xbmcgui.ListItem("Connect"),
            url=endpoints.build_url_connect(device, address)
        )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_connect(bt: Bluetoothctl, device: str, address: str,
                 addon_name: str) -> None:
    dialog = xbmcgui.Dialog()

    loginfo(f'attempting connection to {device} {address}')
    with busy_dialog():
        process = bt.connect(address)

    if process.returncode == 0:
        loginfo('connection successful')
        dialog.notification(
            heading=addon_name,
            message='Connection successful',
            icon=xbmcgui.NOTIFICATION_INFO
        )
    else:
        logerror(f'connection failed.\n'
                 f'return code: {process.returncode}\n'
                 f'stdout: {process.stdout}\n'
                 f'stderr: process.stderr)')
        dialog.notification(
            heading=addon_name,
            message='Connection failed',
            icon=xbmcgui.NOTIFICATION_ERROR
        )


def mode_disconnect(bt: Bluetoothctl, device: str, address: str,
                    addon_name: str) -> None:
    dialog = xbmcgui.Dialog()

    loginfo(f'attempting to disconnect from {device} {address}')
    with busy_dialog():
        process = bt.disconnect(address)

    if process.returncode == 0:
        loginfo('disconnection successful')
        dialog.notification(
            heading=addon_name,
            message='Disconnection successful',
            icon=xbmcgui.NOTIFICATION_INFO
        )
    else:
        logerror(f'disconnection failed.\n'
                 f'return code: {process.returncode}\n'
                 f'stdout: {process.stdout}\n'
                 f'stderr: process.stderr)')
        dialog.notification(
            heading=addon_name,
            message='Disconnection failed',
            icon=xbmcgui.NOTIFICATION_ERROR
        )


def mode_pair(bt: Bluetoothctl, device: str, address: str,
              addon_name: str) -> None:
    dialog = xbmcgui.Dialog()

    loginfo(f'attempting to pair with {device} {address}')
    with busy_dialog():
        process = bt.pair(address)

    if process.returncode == 0:
        loginfo('pairing successful')
        dialog.notification(
            heading=addon_name,
            message='Pairing successful',
            icon=xbmcgui.NOTIFICATION_INFO
        )
    else:
        logerror(f'pairing failed.\n'
                 f'return code: {process.returncode}\n'
                 f'stdout: {process.stdout}\n'
                 f'stderr: process.stderr)')
        dialog.notification(
            heading=addon_name,
            message='pairing failed',
            icon=xbmcgui.NOTIFICATION_ERROR
        )


def mode_remove(bt: Bluetoothctl, device: str, address: str,
                addon_name: str) -> None:
    dialog = xbmcgui.Dialog()

    loginfo(f'attempting to remove {device} {address}')
    with busy_dialog():
        process = bt.remove(address)

    if process.returncode == 0:
        loginfo('removing successful')
        dialog.notification(
            heading=addon_name,
            message='trusting successful',
            icon=xbmcgui.NOTIFICATION_INFO
        )
    else:
        logerror(f'removing failed.\n'
                 f'return code: {process.returncode}\n'
                 f'stdout: {process.stdout}\n'
                 f'stderr: process.stderr)')
        dialog.notification(
            heading=addon_name,
            message='removing failed',
            icon=xbmcgui.NOTIFICATION_ERROR
        )


def mode_trust(bt: Bluetoothctl, device: str, address: str,
               addon_name: str) -> None:
    dialog = xbmcgui.Dialog()

    loginfo(f'attempting to trust {device} {address}')
    with busy_dialog():
        process = bt.trust(address)

    if process.returncode == 0:
        loginfo('trusting successful')
        dialog.notification(
            heading=addon_name,
            message='trusting successful',
            icon=xbmcgui.NOTIFICATION_INFO
        )
    else:
        logerror(f'trusting failed.\n'
                 f'return code: {process.returncode}\n'
                 f'stdout: {process.stdout}\n'
                 f'stderr: process.stderr)')
        dialog.notification(
            heading=addon_name,
            message='trusting failed',
            icon=xbmcgui.NOTIFICATION_ERROR
        )


def mode_untrust(bt: Bluetoothctl, device: str, address: str,
                 addon_name: str) -> None:
    dialog = xbmcgui.Dialog()

    loginfo(f'attempting to revoke trust in {device} {address}')
    with busy_dialog():
        process = bt.trust(address)

    if process.returncode == 0:
        loginfo('revoking trust successful')
        dialog.notification(
            heading=addon_name,
            message='revoking trust successful',
            icon=xbmcgui.NOTIFICATION_INFO
        )
    else:
        logerror(f'revoking trust failed.\n'
                 f'return code: {process.returncode}\n'
                 f'stdout: {process.stdout}\n'
                 f'stderr: process.stderr)')
        dialog.notification(
            heading=addon_name,
            message='revoking trust failed',
            icon=xbmcgui.NOTIFICATION_ERROR
        )


def get_available_devices(bt: Bluetoothctl) -> dict[str, str]:
    try:
        devices = bt.get_devices()
        logdebug('getting available devices succeeded.'
                 f'\ndevices: {devices}')
    except CalledProcessError as e:
        logerror(f'listing available devices failed.\n'
                 f'return code: {e.returncode}\n'
                 f'stdout: {e.stdout}'
                 f'stderr: e.stderr)')
        devices = {}

    return devices


def get_paired_devices(bt: Bluetoothctl) -> dict[str, str]:
    try:
        devices = bt.get_paired_devices()
        logdebug('getting paired devices succeeded.'
                 f'\ndevices: {devices}')
    except CalledProcessError as e:
        logerror(f'listing paired devices failed.\n'
                 f'return code: {e.returncode}\n'
                 f'stdout: {e.stdout}'
                 f'stderr: e.stderr)')
        devices = {}

    return devices

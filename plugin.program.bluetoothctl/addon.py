from subprocess import CalledProcessError, CompletedProcess
from typing import Callable
import xbmcgui  # type: ignore
import xbmcplugin  # type: ignore
from resources.lib.plugin import Plugin
from resources.lib.bluetoothctl import Bluetoothctl
from resources.lib.busy_dialog import busy_dialog
from resources.lib.logging import logerror, logdebug, loginfo

plugin = Plugin()
bt = Bluetoothctl()


@plugin.action()
def root(params: dict[str, str]) -> None:
    xbmcplugin.addDirectoryItem(
        handle=plugin.handle,
        url=plugin.build_url(action='paired_devices'),
        listitem=xbmcgui.ListItem('paired devices'),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        handle=plugin.handle,
        url=plugin.build_url(action='available_devices'),
        listitem=xbmcgui.ListItem('available devices'),
        isFolder=True
    )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.action()
def available_devices(params: dict[str, str]) -> None:
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
        # li.addContextMenuItems([
        # ])
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            url=plugin.build_url(action='device', device=device,
                                 address=address, paired=False),
            listitem=li,
            isFolder=True
        )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.action()
def paired_devices(param: dict[str, str]) -> None:
    devices = get_paired_devices(bt)

    for device, address in devices.items():
        logdebug(f'listing device {device}')
        li = xbmcgui.ListItem(device)
        # li.addContextMenuItems([
        # ])
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            url=plugin.build_url(action='device', device=device,
                                 address=address, paired=True),
            listitem=li,
            isFolder=True
        )

    xbmcplugin.endOfDirectory(plugin.handle)


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


@plugin.action()
def device(params: dict[str, str]) -> None:
    device = params['device']
    address = params['address']
    paired = params['paired']

    if paired == str(True):
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Connect"),
            url=plugin.build_url(action='connect', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Disconnect"),
            url=plugin.build_url(action='disconnect', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Unpair"),
            url=plugin.build_url(action='unpair', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Trust"),
            url=plugin.build_url(action='trust', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Revoke trust"),
            url=plugin.build_url(action='untrust', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Information"),
            url=plugin.build_url(action='info', device=device,
                                 address=address)
        )
    elif paired == str(False):
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Pair"),
            url=plugin.build_url(action='pair', device=device, address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Connect"),
            url=plugin.build_url(action='connect', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=xbmcgui.ListItem("Information"),
            url=plugin.build_url(action='info', device=device,
                                 address=address)
        )

    xbmcplugin.endOfDirectory(plugin.handle)


def device_action_mode_factory(
    infinitive: str, present: str,
    bt_method: Callable[[str], CompletedProcess[str]], addon_name: str
) -> Callable[[dict[str, str]], None]:
    """
    Create a 'mode function' for running a bluetoothctl action on a device e.g.
    connecting, pairing. This function handles running the method as well as
    logging and errors.

    Args:
        infinitive: Infinitive verb e.g. 'trust', 'pair'.
        present: Present tense verb e.g. 'trusting', 'pairing'.
        bt_method: Method of `Bluetoothctl` object to call. It is expected that
            the method takes the device address as the only argument.
        addon_name: Name of the addon.
    """

    def func(params: dict[str, str]) -> None:
        device = params['device']
        address = params['address']

        dialog = xbmcgui.Dialog()

        loginfo(f'attempting to {infinitive}: {device} {address}')
        with busy_dialog():
            process = bt_method(address)

        if process.returncode == 0:
            loginfo(f'{present} successful')
            dialog.notification(
                heading=addon_name,
                message=f'{present} successful',
                icon=xbmcgui.NOTIFICATION_INFO
            )
        else:
            logerror(f'{present} failed.\n'
                     f'return code: {process.returncode}\n'
                     f'stdout: {process.stdout}\n'
                     f'stderr: process.stderr)')
            dialog.notification(
                heading=addon_name,
                message=f'{present} failed',
                icon=xbmcgui.NOTIFICATION_ERROR
            )

    return func


connect = device_action_mode_factory(
    'connect', 'connecting', bt.connect, plugin.name
)
plugin.action('connect')(connect)

disconnect = device_action_mode_factory(
    'disconnect', 'disconnecting', bt.disconnect, plugin.name
)
plugin.action('disconnect')(disconnect)

pair = device_action_mode_factory(
    'pair', 'pairing', bt.pair, plugin.name
)
plugin.action('pair')(pair)

remove = device_action_mode_factory(
    'remove', 'removing', bt.remove, plugin.name
)
plugin.action('remove')(remove)

trust = device_action_mode_factory(
    'trust', 'trusting', bt.trust, plugin.name
)
plugin.action('trust')(trust)

untrust = device_action_mode_factory(
    'revoke trust', 'revoking trust', bt.trust, plugin.name
)
plugin.action('untrust')(untrust)


@plugin.action()
def info(params: dict[str, str]) -> None:
    device = params['device']
    address = params['address']

    process = bt.info(address)
    if process.returncode != 0:
        logerror(f'failed to get information for {device} {address}')
        return
    else:
        loginfo(f'fetched information for {device} {address}')

    dialog = xbmcgui.Dialog()
    dialog.textviewer(
        heading=device,
        text=process.stdout,
        usemono=True
    )


if __name__ == "__main__":
    plugin.run()

from functools import wraps
from subprocess import CalledProcessError, CompletedProcess
from typing import Callable
import xbmcgui  # type: ignore
import xbmcplugin  # type: ignore
from resources.lib.plugin import Plugin, Action, LOGERROR, LOGDEBUG
from resources.lib.bluetoothctl import Bluetoothctl
from resources.lib.busy_dialog import busy_dialog

plugin = Plugin()

bluetoothctl_path = plugin.get_setting('bluetoothctl_path')
plugin.log(LOGDEBUG, f'fetched bluetoothctl path {bluetoothctl_path}')
bluetoothctl_timeout = int(plugin.get_setting('bluetoothctl_timeout'))
plugin.log(LOGDEBUG, f'fetched bluetoothctl timeout {bluetoothctl_timeout}')
bt = Bluetoothctl(executable=bluetoothctl_path,
                  scan_timeout=bluetoothctl_timeout)


@plugin.action()
def root(params: dict[str, str]) -> None:
    xbmcplugin.addDirectoryItem(
        handle=plugin.handle,
        url=plugin.build_url(action='paired_devices'),
        listitem=plugin.list_item(plugin.localise(30201)),
        isFolder=True
    )
    xbmcplugin.addDirectoryItem(
        handle=plugin.handle,
        url=plugin.build_url(action='available_devices'),
        listitem=plugin.list_item(plugin.localise(30202)),
        isFolder=True
    )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.action()
def available_devices(params: dict[str, str]) -> None:
    with busy_dialog():
        process = bt.scan()

    if process.returncode == 0:
        plugin.log(LOGDEBUG, f'scanning succeeded.\nstdout: {process.stdout}')
    else:
        plugin.log(LOGERROR,
                   f'scanning failed.\nreturn code: {process.returncode}\n'
                   f'stdout: {process.stdout}'
                   f'stderr: process.stderr)')

    # Remove paired devices from list
    devices = get_available_devices(bt)
    paired_devices = get_paired_devices(bt)
    for device in paired_devices.keys():
        devices.pop(device, None)

    for device, address in devices.items():
        plugin.log(LOGDEBUG, f'listing device {device}')

        li = plugin.list_item(device)
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
        plugin.log(LOGDEBUG, f'listing device {device}')
        li = plugin.list_item(device)
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
        plugin.log(LOGDEBUG, 'getting available devices succeeded.'
                   f'\ndevices: {devices}')
    except CalledProcessError as e:
        plugin.log(LOGERROR, f'listing available devices failed.\n'
                   f'return code: {e.returncode}\n'
                   f'stdout: {e.stdout}'
                   f'stderr: {e.stderr})')
        devices = {}

    return devices


def get_paired_devices(bt: Bluetoothctl) -> dict[str, str]:
    try:
        devices = bt.get_paired_devices()
        plugin.log(LOGDEBUG, 'getting paired devices succeeded.'
                   f'\ndevices: {devices}')
    except CalledProcessError as e:
        plugin.log(LOGERROR, f'listing paired devices failed.\n'
                   f'return code: {e.returncode}\n'
                   f'stdout: {e.stdout}'
                   f'stderr: {e.stderr})')
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
            listitem=plugin.list_item(plugin.localise(30203)),
            url=plugin.build_url(action='connect', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30204)),
            url=plugin.build_url(action='disconnect', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30206)),
            url=plugin.build_url(action='unpair', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30207)),
            url=plugin.build_url(action='trust', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30208)),
            url=plugin.build_url(action='untrust', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30209)),
            url=plugin.build_url(action='info', device=device,
                                 address=address)
        )
    elif paired == str(False):
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30205)),
            url=plugin.build_url(action='pair', device=device, address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30203)),
            url=plugin.build_url(action='connect', device=device,
                                 address=address)
        )
        xbmcplugin.addDirectoryItem(
            handle=plugin.handle,
            listitem=plugin.list_item(plugin.localise(30209)),
            url=plugin.build_url(action='info', device=device,
                                 address=address)
        )

    xbmcplugin.endOfDirectory(plugin.handle)


DeviceAction = Callable[[dict[str, str]], CompletedProcess[str]]


def device_action(infinitive: str,
                  present: str) -> Callable[[DeviceAction], Action]:
    def decorator(func: DeviceAction) -> Action:
        nonlocal infinitive
        nonlocal present

        @wraps(func)
        def wrapper(params: dict[str, str]) -> None:
            nonlocal infinitive
            nonlocal present

            address = params['address']

            dialog = xbmcgui.Dialog()

            plugin.log(LOGDEBUG,
                       f'attempting to {infinitive}: {device} {address}')
            process = func(params)

            if process.returncode == 0:
                plugin.log(LOGDEBUG, f'{present} successful')
                dialog.notification(
                    heading=plugin.name,
                    message=f'{present} successful',
                    icon=xbmcgui.NOTIFICATION_INFO
                )
            else:
                plugin.log(LOGERROR, f'{present} failed.\n'
                           f'return code: {process.returncode}\n'
                           f'stdout: {process.stdout}\n'
                           f'stderr: process.stderr)')
                dialog.notification(
                    heading=plugin.name,
                    message=f'{present} failed',
                    icon=xbmcgui.NOTIFICATION_ERROR
                )
        return wrapper
    return decorator


@plugin.action()
@device_action(infinitive='connect', present='connecting')
def connect(params: dict[str, str]) -> CompletedProcess[str]:
    address = params['address']

    with busy_dialog():
        process = bt.connect(address)

    return process


@plugin.action()
@device_action(infinitive='disconnect', present='disconnecting')
def disconnect(params: dict[str, str]) -> CompletedProcess[str]:
    address = params['address']

    with busy_dialog():
        process = bt.disconnect(address)

    return process


@plugin.action()
@device_action(infinitive='pair', present='pairing')
def pair(params: dict[str, str]) -> CompletedProcess[str]:
    address = params['address']

    with busy_dialog():
        process = bt.pair(address)

    return process


@plugin.action()
@device_action(infinitive='remove', present='removing')
def remove(params: dict[str, str]) -> CompletedProcess[str]:
    address = params['address']

    with busy_dialog():
        process = bt.remove(address)

    return process


@plugin.action()
@device_action(infinitive='trust', present='trusting')
def trust(params: dict[str, str]) -> CompletedProcess[str]:
    address = params['address']

    with busy_dialog():
        process = bt.trust(address)

    return process


@plugin.action()
@device_action(infinitive='revoke trust', present='revoking trust')
def untrust(params: dict[str, str]) -> CompletedProcess[str]:
    address = params['address']

    with busy_dialog():
        process = bt.trust(address)

    return process


@plugin.action()
def info(params: dict[str, str]) -> None:
    device = params['device']
    address = params['address']

    dialog = xbmcgui.Dialog()

    process = bt.info(address)
    if process.returncode != 0:
        plugin.log(LOGERROR,
                   f'failed to get information for {device} {address}')
        dialog.notification(
            heading=plugin.name,
            message='failed to get information',
            icon=xbmcgui.NOTIFICATION_ERROR
        )
        return
    else:
        plugin.log(LOGDEBUG, f'fetched information for {device} {address}')

    dialog.textviewer(
        heading=device,
        text=process.stdout,
        usemono=True
    )


if __name__ == "__main__":
    plugin.run()

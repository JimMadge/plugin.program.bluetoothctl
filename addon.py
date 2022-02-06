from collections.abc import Generator
from contextlib import contextmanager
import sys
import urllib.parse
import xbmc  # type: ignore
import xbmcgui  # type: ignore
import xbmcplugin  # type: ignore
from lib.bluetoothctl import Bluetoothctl

# Get arguments
# Each 'page' is a separate invocation of this script with it's path given by a
# URL. Argument 0 is the base of this url and arugment 2 is the query string.
# See
# https://kodi.wiki/view/Audio-video_add-on_tutorial#Navigating_between_pages
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])


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


def build_url(query: dict[str, str]) -> str:
    """
    Construct a url to recall this script with a set of arguments encoded in
    the query string.

    Args:
        query: Dict of arguments
    """
    return ''.join([base_url, '?', urllib.parse.urlencode(query)])


# Get 'mode' argument, default to None
mode = args.get('mode', None)

if mode is None:
    # Initial entry point
    url = build_url({'mode': 'available_devices'})
    li = xbmcgui.ListItem('Available Devices')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'available_devices':
    # Available devices entry point
    bt = Bluetoothctl()
    with busy_dialog():
        bt.scan()
        devices = bt.devices()

    for device in devices:
        li = xbmcgui.ListItem(device)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=base_url,
                                    listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

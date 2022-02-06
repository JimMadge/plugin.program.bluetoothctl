import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Get arguments
# Each 'page' is a separate invocation of this script with it's path given by a
# URL. Argument 0 is the base of this url and arugment 2 is the query string.
# See
# https://kodi.wiki/view/Audio-video_add-on_tutorial#Navigating_between_pages
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])


def build_url(query: dict):
    """
    Construct a url to recall this script with a set of arguments encoded in
    the query string.

    Args:
        query: Dict of arguments
    """
    return base_url + '?' + urllib.parse.urlencode(query)


# Get 'mode' argument, default to None
mode = args.get('mode', None)

if mode is None:
    # Initial entry point
    url = build_url({'mode': 'folder', 'foldername': 'Folder One'})
    li = xbmcgui.ListItem('Folder One')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'Folder Two'})
    li = xbmcgui.ListItem('Folder Two')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)
elif mode[0] == 'folder':
    # Folder entry point
    foldername = args['foldername'][0]
    url = 'http://localhost/some_video.mkv'
    li = xbmcgui.ListItem(foldername + ' Video')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)

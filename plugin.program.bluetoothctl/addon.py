import sys
import urllib.parse
from resources.lib.main import main

# Get arguments
# Each 'page' is a separate invocation of this script with it's path given by a
# URL. Argument 0 is the base of this url and arugment 2 is the query string.
# See
# https://kodi.wiki/view/Audio-video_add-on_tutorial#Navigating_between_pages
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

main(base_url, addon_handle, args)

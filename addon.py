import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')

line1 = "This is a simple example of OK dialog"
line2 = "Showing this message using"
line3 = "XBMC python modules"

xbmcgui.Dialog().ok(addonname, "\n".join((line1, line2, line3)))

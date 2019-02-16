# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import os
import sqlite3
import xbmc
import xbmcgui
import xbmcaddon
import gen_html

__settings__ = xbmcaddon.Addon(id='script.export-movie-lib')
addon_name = __settings__.getAddonInfo("name")
__language__ = __settings__.getLocalizedString
__language__(30204)
# settings = __settings__.openSettings()
#
# path = __settings__.getSetting("path")
# recursive = __settings__.getSetting("recursive")
# watched = __settings__.getSetting("watched")



file = gen_html.main()

if file:
    xbmcgui.Dialog().ok(addon_name, "Movies library exported to " + file)
else:
    xbmcgui.Dialog().ok(addon_name, "There was an error while exporting library check log")

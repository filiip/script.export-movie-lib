# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import os
import sqlite3
import xbmc
import xbmcgui
import xbmcaddon

__settings__ = xbmcaddon.Addon(id='script.export-movie-lib')
addon_name = __settings__.getAddonInfo("name")
__language__ = __settings__.getLocalizedString
__language__(30204)
settings = __settings__.openSettings()

path = __settings__.getSetting("path")
recursive = __settings__.getSetting("recursive")
watched = __settings__.getSetting("watched")




if recursive == "true":
    path += "%"
play_count = "1" if watched == "watched" else "0"

db_path = os.path.join(xbmc.translatePath("special://database"), 'MyVideos107.db')


conn = sqlite3.connect(db_path)
c = conn.cursor()

cmd_get_files = (u"select distinct files.strFilename from movie,files,path where movie.idFile=files.idFile "
                 u"and files.idPath=path.idPath and path.strPath LIKE '{path}';".format(path=path))
paths = c.execute(cmd_get_files).fetchall()


cmd_set = u"update files set playCount='{count}' where strFilename = '{file}'"
for a in paths:
    c.execute(cmd_set.format(count=play_count, file=a[0]))

conn.commit()

cmd_check = u"select distinct playCount from files where strFilename = '{file}'"
counts = []
for a in paths:
    c.execute(cmd_set.format(count=play_count, file=a[0]))


conn.close()

if all(count == play_count for count in counts):
    xbmcgui.Dialog().ok(addon_name, "Movies in folder " + path, "sucessfully set as " + watched)
else:
    xbmcgui.Dialog().ok(addon_name, "There was an error while setting watched status for selected folder, check log")
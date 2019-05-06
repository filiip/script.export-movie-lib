# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import os

import xbmcgui
import xbmcaddon

from resources.lib import gen_html


SORT_BY = {"0": u"title",
           "1": u"year",
           "2": u"rating"}

SORT_ORD = {"0": u"ascending",
            "1": u"descending"}


def to_bool(val):
    """Convert string to bool value

    :param val: value to convert
    :type val: str
    :return: converted value
    :rtype: bool
    """
    if val.lower() == "true":
        return True
    return False


def main():
    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo("name")

    addon.openSettings()

    path = addon.getSetting(u"path")
    if path == u"$HOME":
        path = os.path.expanduser("~")
    path = os.path.join(path, "movie_lib.html")

    sort_by = SORT_BY[addon.getSetting(u"sort_by")]
    sort_ord = SORT_ORD[addon.getSetting(u"sort_ord")]
    width = addon.getSetting(u"width")

    lims = {}
    gen_lims = []
    if to_bool(addon.getSetting(u"limits")):
        lim_opts = ["year_from", "year_to", "actor", "director", "country", "tag"]
        for opt in lim_opts:
            val = addon.getSetting(u"lim_{}".format(opt))
            if opt in ["year_from", "year_to"]:
                val = int(val)
            elif val == u"any":
                continue
            lims[opt] = val

        if to_bool(addon.getSetting(u"genre_lim")):
            genres = ["comedy", "drama", "romance", "adventure", "scifi", "animation", "fantasy",
                      "action", "crime", "thriller", "mystery", "horror", "music", "war"]
            for genre in genres:
                val = to_bool(addon.getSetting(u"genre_lim_{}".format(genre)))
                if val:
                    gen_lims.append(genre)

    dialog = xbmcgui.Dialog()
    conf = dialog.yesno("Configuration check",
                        "Export movie library to {path}, sorted by {sort_by} in {sort_ord} order".format(path=path, sort_by=sort_by, sort_ord=sort_ord),
                        "Export limited to: {}".format(lims) if lims else "",
                        "Export only following genres: {}".format(gen_lims) if gen_lims else "",
                        yeslabel="Export",
                        nolabel="Cancel")

    if not conf:
        return

    page = gen_html.HtmlPage(path)
    page.set_filters(lims)
    page.set_genre_filters(gen_lims)
    file = page.gen_html(sort_by, sort_ord, int(width))

    if file:
        xbmcgui.Dialog().ok(addon_name, u"Movies library exported to " + file)


if __name__ == '__main__':
    main()

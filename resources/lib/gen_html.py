
import io
import datetime
import urllib
import json
import xml.etree.ElementTree as Etree

import xbmc
import xbmcgui
import xbmcaddon

from resources.lib import css_style

RATE = u"rating"
DIRECT = u"director"
TITLE = u"originaltitle"
YEAR = u"year"
TAG = u"tagline"
COUNTRY = u"country"
ART = u"art"
IMDBID = u"imdbnumber"
POSTER = u"poster"


class DbRequestException(Exception):
    pass


class HtmlPage(object):
    """Class for handling HTML page with exported data"""

    def __init__(self, path):
        """Class constructor

        :param path: path for the html file
        :type  path: str
        """
        self.path = path
        self.filter = {"and": []}

    @staticmethod
    def _inner_table(parent, params):
        """Create the "inner table" inside of movie poster

        :param parent: parent xml element
        :type parent: xml.Etree.ElementTree.Element
        :param params: list with parameters of the movie (items for the table)
        :type params: list
        """
        table = Etree.SubElement(parent, "table", Class="text")
        for param in params:
            tr = Etree.SubElement(table, "tr", style="border-bottom:1pt solid black;")
            Etree.SubElement(tr, "td").text = param

    @staticmethod
    def _get_img(movie):
        """Get poster url from JSON data

        :param movie: JSON movie data
        :type movie: dict
        :return: url of poster image
        :rtype: str
        """
        return urllib.unquote(movie[ART][POSTER].lstrip(u"image:").strip(u"/"))

    @staticmethod
    def _get_link(movie_id):
        """Get IMDB link for a movie

        :param movie_id: IMDB movie ID
        :type movie_id: str
        :return: IMDB link to the movie
        :rtype: str
        """
        return "https://www.imdb.com/title/" + movie_id

    def _prettify(self, elem, level=0):
        """Prettify XML

        :param elem: top level element to prettify
        :type elem: xml.Etree.ElementTree.Element
        :param level: current level of prettifying
        :type level: int
        :return: prettified XML element
        :rtype: xml.Etree.ElementTree.Element
        """
        i = "\n" + level*"  "
        j = "\n" + (level - 1)*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                self._prettify(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem

    def set_filters(self, filters):
        """Set filters for movie export

        :param filters: dict in form of lim_<item>: value
        :type filters: dict
        """
        for opt, val in filters.items():
            if opt == u"year_from":
                item = {"operator": "greaterthan", "field": "year", "value": str(val-1)}
            elif opt == u"year_to":
                item = {"operator": "lessthan", "field": "year", "value": str(val+1)}
            else:
                item = {"operator": "contains", "field": opt.strip("lim_"), "value": val}

            self.filter["and"].append(item)

    def set_genre_filters(self, filters):
        """Set filters for genres

        :param filters: list of allowed genres
        :type filters: list
        """
        item = {"operator": "startswith", "field": "genre", "value": []}
        for genre in filters:
            gen = genre.replace("genre_lim_", "")[:3]
            item["value"].append(gen)
        self.filter["and"].append(item)

    def gen_html(self, sort_by, sort_ord, width):
        """Generate HTML page with exported movie database

        :param sort_by: parameter used for sorting of movies
        :type sort_by: str
        :param sort_ord: sorting order (ascending|descending)
        :type sort_ord: str
        :param width: width of the page in movie posters (number of posters in one line)
        :type width: int
        :return: path of created HTMML page
        :rtype: str
        """
        xbmcgui.Dialog().ok("Filters", str(self.filter))
        html = Etree.Element("html")
        head = Etree.SubElement(html, "head")
        Etree.SubElement(head, "title").text = "Kodi Movie Library"
        Etree.SubElement(head, "style").text = css_style.STYLE
        body = Etree.SubElement(html, "body")
        dt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        Etree.SubElement(body, "p").text = "Movie library exported {dt}".format(dt=dt)
        table = Etree.SubElement(body, "table", style="margin:1em auto;")

        query = {"jsonrpc": "2.0",
                 "params": {"sort": {"order": sort_ord, "method": sort_by},
                            "filter": self.filter,
                            "properties": [RATE, DIRECT, TITLE, YEAR, TAG, COUNTRY, ART, IMDBID]},
                 "method": "VideoLibrary.GetMovies",
                 "id": "libMovies"}

        res = xbmc.executeJSONRPC(json.dumps(query))
        res = json.loads(res)

        if u"error" in res:
            addon = xbmcaddon.Addon()
            msg = addon.getLocalizedString(32100)
            if u"message" in res[u"error"][u"data"][u"stack"]:
                msg2 = res[u"error"][u"data"][u"stack"][u"message"]
            else:
                msg2 = res[u"error"][u"data"][u"stack"][u"property"][u"message"]
            xbmcgui.Dialog().ok("Error", msg, res[u"error"][u"message"], msg2)
            raise DbRequestException(msg2)

        if u"movies" not in res[u"result"]:
            xbmcgui.Dialog().ok("Error", "No movie fits the selected filters")
            return

        tr = None
        idx = 0
        for movie in res[u"result"][u"movies"]:
            link = self._get_link(movie[IMDBID])

            if idx % width == 0:
                tr = Etree.SubElement(table, "tr")

            div1 = Etree.SubElement(tr, "th", Class="container")
            ahref = Etree.SubElement(div1, "a", href=link)
            Etree.SubElement(ahref, "img", src=self._get_img(movie), Class="image")
            div = Etree.SubElement(ahref, "div", Class="overlay")

            self._inner_table(div, [movie[TITLE], str(int(round(movie[RATE] * 10))) + "%", ",".join(movie[DIRECT]),
                              str(movie[YEAR]), ",".join(movie[COUNTRY]), movie[TAG]])
            idx += 1

        with io.open(self.path, mode="w", encoding="utf-8") as fo:
            towrite = Etree.tostring(self._prettify(html), method="xml", encoding="utf-8").decode("utf-8")
            fo.write(towrite)

        return self.path

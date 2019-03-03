import os
import io
import datetime
import urllib
import json

import xbmc
import xbmcgui

import xml.etree.ElementTree as ETREE

RATE = u"rating"
DIRECT = u"director"
TITLE = u"originaltitle"
YEAR = u"year"
TAG = u"tagline"
COUNTRY = u"country"
ART = u"art"
IMDBID = u"imdbnumber"

def inner_table(elem, params):
    table = ETREE.SubElement(elem, "table", Class="text")
    for param in params:
        tr = ETREE.SubElement(table, "tr", style="border-bottom:1pt solid black;")
        ETREE.SubElement(tr, "td").text = param


def get_img(movie):
    return urllib.unquote(movie[u"art"]["poster"].lstrip(u"image:").strip(u"/"))


def get_link(movie_id):
    link = "https://www.imdb.com/title/" + str(movie_id)
    return link


def prettify(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level - 1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            prettify(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def gen_html(path):
    html = ETREE.Element("html")
    head = ETREE.SubElement(html, "head")
    ETREE.SubElement(head, "title").text = "Kodi Movie Library"
    ETREE.SubElement(head, "style").text = """body {background: linear-gradient(to left, #648880, #293f50);}
    table {{border-collapse:collapse; text-align:left; margin:20px;}}
      tr:hover td{{background-color: #8FAFEF;}}
      tr:nth-child(even) {{background-color: #eee;}}
      tr:nth-child(odd) {{background-color: #fff;}}
      th {{border-bottom:2px solid grey; color: white; background-color: #8F8F8F; padding: 4px;}}
      td {{padding:3px;}}
        
        .container {
          position: relative;
          transition: transform .5s;
          width: 300px;
        }
        
        .image {
          display: block;
          width: 300px;
          height: 450px;
        }
        
        .container:hover{
        transform: scale(1.2);
        z-index: 1;
        }
        
        .container:hover .overlay {
          opacity: 0.8;
        }
        
        .overlay {
          position: absolute;
          top: 0;
          bottom: 0;
          left: 0;
          right: 0;
          width: 301px;
          height: 451px;
          opacity: 0;
          transition: .5s ease;
          background-color: #293f50 ;
        }
        .text {
          color: white;
          font-size: 20px;
          position: absolute;
          top: 50%;
          left: 50%;
          -webkit-transform: translate(-50%, -50%);
          -ms-transform: translate(-50%, -50%);
          transform: translate(-50%, -50%);
          text-align: center;
          border-collapse:collapse;
        }
        """

    body = ETREE.SubElement(html, "body")
    dt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    style = "font-family:Courier New,Courier,monospace;font-size:30px;text-align: center;"
    ETREE.SubElement(body, "p",  style=style).text = "Movie library exported {dt}".format(dt=dt)
    table = ETREE.SubElement(body, "table", style="margin:1em auto;")

    query = {"jsonrpc": "2.0",
             "params": {"sort": {"order": "ascending", "method": "title"},
                        "properties": [RATE, DIRECT, TITLE, YEAR, TAG, COUNTRY, ART, IMDBID]},
             "method": "VideoLibrary.GetMovies",
             "id": "libMovies"}

    res = xbmc.executeJSONRPC(json.dumps(query))
    res = json.loads(res)
    # TODO: error handling

    line = 6  # TODO: get dynamically size

    tr = None
    idx = 0
    for movie in res[u"result"][u"movies"]:
        link = get_link(movie[IMDBID])

        if idx % line == 0:
            tr = ETREE.SubElement(table, "tr")

        div1 = ETREE.SubElement(tr, "th", Class="container")
        ahref = ETREE.SubElement(div1, "a", href=link)
        ETREE.SubElement(ahref, "img", src=get_img(movie), Class="image")
        div = ETREE.SubElement(ahref, "div", Class="overlay")

        inner_table(div,
                    [movie[TITLE],
                     str(int(round(movie[RATE] * 10))) + "%",
                     ",".join(movie[DIRECT]),
                     str(movie[YEAR]),
                     ",".join(movie[COUNTRY]),
                     movie[TAG]])
        idx += 1

    with io.open(path, mode="w", encoding='utf-8') as fo:
        towrite = ETREE.tostring(prettify(html), method="xml", encoding="utf-8").decode("utf-8")
        fo.write(towrite)

    return path

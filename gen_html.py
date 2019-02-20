import os
import sys
import datetime

import sqlite3
import xml.etree.ElementTree as ETREE
import xml.dom.minidom


FILE = home = os.path.expanduser("~") + "/movie_lib.html"
DB_FILE = r"C:\Users\Filip\AppData\Roaming\Kodi\userdata\Database\MyVideos116.db"


def inner_table(elem, params):
    table = ETREE.SubElement(elem, "table", Class="text")
    for param in params:
        tr = ETREE.SubElement(table, "tr", style="border-bottom:1pt solid black;")
        ETREE.SubElement(tr, "td").text = param


def get_rating(cur, id):
    cmd_get_info = (u"select rating from rating where rating_id={};".format(id))
    rate = cur.execute(cmd_get_info).fetchall()[0][0]
    return str(rate * 10).split(".")[0] + "%"


def get_link(data, id):
    for line in data:
        # print(type(id), type(line[0]))
        if line[0] == int(id) and line[-1] == "imdb":
            break
    link = "https://www.imdb.com/title/" + line[3]
    return link

def prettify(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
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


def main():
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
    ETREE.SubElement(body, "p",  style="font-family:Courier New,Courier,monospace;font-size:30px;text-align: center;").text = "Movie library exported {dt}".format(dt=dt)
    table = ETREE.SubElement(body, "table", style="margin:1em auto;")

    db_path = os.path.join("/home/filip/.kodi/userdata/Database/", 'MyVideos107.db')
    db_path = DB_FILE   #TODO: get the db file dynamically
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    #c08 = img, c15 = director, c16 = name, c21 = county
    cmd_get_info = (u"select premiered, c03, c08, c15, c16, c21, c05, c09 from movie;")
    info = cur.execute(cmd_get_info).fetchall()


    cmd_get_info = (u"select * from uniqueid;")
    data = cur.execute(cmd_get_info).fetchall()

    # data = cur.execute("select * from movie")
    # for a in data:
    #     for b in a:
    #         print(b)
    #     break


    line = 6 #TODO: get dynamically size
    for idx in range(len(info)):
        date, tag, img, direct, name, country, rate_id, uniq_id = info[idx]
        year = date.split("-")[0]
        rate = get_rating(cur, rate_id)
        link = get_link(data, uniq_id)
        # print(link)
        if idx % line == 0:
            tr = ETREE.SubElement(table, "tr")

        div1 = ETREE.SubElement(tr, "th", Class="container")

        # print(img)
        imgs = ETREE.fromstring("<fanart>{}</fanart>".format(img))
        # print(ETREE.tostring(imgs, pretty_print=True))

        ahref = ETREE.SubElement(div1, "a", href=link)
        ETREE.SubElement(ahref, "img", src=imgs[-1].text, title=name, Class="image")
        div = ETREE.SubElement(ahref, "div", Class="overlay")

        inner_table(div, [name, rate, direct, year, country, tag])


    with open(FILE, "w") as fo:
        if sys.version_info[0] >= 3:
            towrite = ETREE.tostring(prettify(html), method="xml", encoding="unicode")
        else:
            towrite = ETREE.tostring(prettify(html), method="xml", encoding="unicode").encode("utf-8")
        fo.write(towrite)
    # print("Exported to {}".format(FILE))
    conn.close()
    return FILE



if __name__ == "__main__":
    main()

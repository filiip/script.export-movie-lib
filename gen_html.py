import os
import datetime

import sqlite3
import lxml.etree as ETREE


FILE = home = os.path.expanduser("~") + "/movie_lib.html"


def inner_table(elem, params):
    table = ETREE.SubElement(elem, "table", Class="text")
    for param in params:
        tr = ETREE.SubElement(table, "tr")
        ETREE.SubElement(tr, "td").text = param

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
      //.zoom {
      //    background-color: black;
      //    transition: transform .2s; /* Animation */
      //    width: 200px;
      //    height: 300px;
      //    margin: 0 auto;
      //  }
        
       // .zoom:hover{
       // transform: scale(1.2);
       // }
        
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
          background-color: #008CBA;
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
        }
        """

    body = ETREE.SubElement(html, "body")
    dt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    ETREE.SubElement(body, "h1").text = "Movie library KODI exported {dt}".format(dt=dt)
    table = ETREE.SubElement(body, "table", style="float: left")

    db_path = os.path.join("/home/filip/.kodi/userdata/Database/", 'MyVideos107.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    #c08 = img, c15 = director, c16 = name,
    cmd_get_info = (u"select movie.c08, movie.c15, movie.c16 from movie;")
    info = cur.execute(cmd_get_info).fetchall()

    line = 4
    for idx in range(len(info)):
        img, direct, name = info[idx]
        if idx % line == 0:
            tr = ETREE.SubElement(table, "tr")
        div1 = ETREE.SubElement(tr, "th", Class="container")

        start = img.find("preview=\"") + len("preview=\"") #TODO: use lxml to extract value
        end = img.find("\">", start)

        ETREE.SubElement(div1, "img", src=img[start:end], title=name, Class="image")
        div = ETREE.SubElement(div1, "div", Class="overlay")

        inner_table(div, [name, direct])


    with open(FILE, "w") as fo:
        fo.write(ETREE.tostring(html, pretty_print=True, encoding="unicode"))
    print("Exported to {}".format(FILE))


if __name__ == "__main__":
    main()
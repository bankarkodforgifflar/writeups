#!/usr/bin/python3
import argparse
import json
import os
import sys
import re
import sqlite3
import datetime
import tomllib
import pathlib

directory = "./"
manifest = {}
con = None
cur = None


def init_db():
    global con, cur
    os.remove("compiled.sqlite3") if os.path.exists("compiled.sqlite3") else print(
        "No db was found, creating new")  # Poor mans DROP ALL TABLES
    con = sqlite3.connect("compiled.sqlite3")
    cur = con.cursor()
    cur.execute("""CREATE TABLE competitions(
    name TEXT NOT NULL,
    categories TEXT NOT NULL,
    date INTEGER NOT NULL
);""")
    cur.execute("""CREATE TABLE metadata(
    title TEXT NOT NULL,
    author TEXT,
    date INTEGER,
    content BLOB NOT NULL,
    competition TEXT NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (competition)
        REFERENCES competitions (name)
);""")


def compile_data():
    global manifest, cur, con
    init_db()
    get_manifest()
    for comp in manifest["competitions"]:
        try:
            cmanifest = load_comp_manifest(comp)
            # Insert competition
            cur.execute("INSERT INTO competitions(name,categories,date) VALUES(?,?,?)",
                    (cmanifest["name"], json.dumps(cmanifest["categories"]), int(datetime.datetime.strptime(cmanifest["yearmonth"], "%Y%m").timestamp())))
            data = collect_writeups(comp, cmanifest["name"])
            for d in data:
                cur.execute("INSERT INTO metadata(title,author,date,content,competition,category) VALUES(?,?,?,?,?,?)", d)
        except Exception as e:
            print(f"[WARNING] Skipping {comp} - Encountered error:")
            print(e)
        
    con.commit()

def collect_writeups(comp: str, name: str):
    metadata = []
    sql_friendly_data = []
    comp = pathlib.Path(comp).glob('**/*.md')
    for w in comp:
        content = open(w,"r").read()
        start=content.find("<!--BKFG")
        if start == -1: # Doesn't contain metadata tag, skip
            continue
        elif content.find("-->") == -1: # closing tag wasn't found
            print(f"[{w}] [WARNING] Start of metadata tag found but no closing tag found!")
            continue
        tag = content[start+8:content.find("-->")]
        parsed = tomllib.loads(tag)
        parsed["content"] = content
        l = str(w).split("/")
        category = l[1] if 1 < len(l) else None
        if category == None:
            print(f"[{w}] [WARNING] Failed to get category, skipping")
        parsed["category"] = category
        metadata.append(parsed)
    for m in metadata:
        date = m.get("date")
        if not date == None:
            date = int(datetime.datetime.strptime(date, "%Y%m%d").timestamp())
        sql_friendly_data.append((m["title"], m.get("author"), date, m["content"], name, m["category"]))
    return sql_friendly_data

def load_comp_manifest(comp: str):
    m = open(os.path.join(comp, "manifest.json"), "r").read()
    return json.loads(m)


def get_manifest():
    global directory, manifest
    if not os.path.exists(os.path.join(directory, "manifest.json")):
        print(
            f"[ERROR] There's no manifest.json present here ({directory}), have you specified a correct directory?")
        exit(1)
    m = open(os.path.join(directory, "manifest.json"), "r").read()
    manifest = json.loads(m)


def update_manifest():
    global directory, manifest
    if not os.path.exists(os.path.join(directory, "manifest.json")):
        print(
            f"[ERROR] There's no manifest.json present here ({directory}), have you specified a correct directory?")
        exit(1)
    json.dump(fp=open(os.path.join(directory, "manifest.json"), "w"),
              ensure_ascii=False, obj=manifest)


def create_ctf(name, categories, yearmonth, dirname=None):
    global directory, manifest
    if dirname == None:
        dirname = re.sub(r'[^\x00-\x7F]', '_', name)
    else:
        dirname = dirname[0]
    try:
        # check so it follows format
        datetime.datetime.strptime(yearmonth, "%Y%m")
    except:
        print("Invalid date, make sure it follow YYYYMM (%Y%m)")
        exit(1)
    categories = [c.lower() for c in categories]  # Lowercase em all
    newbasepath = os.path.join(directory, dirname)
    if os.path.exists(newbasepath):
        print(f"[ERROR] Directory {name} already exists!!")
        exit(1)

    os.makedirs(newbasepath)
    manifest["competitions"].append(dirname)

    update_manifest()

    ctf_manifest = {
        "name": name,
        "categories": categories,
        "yearmonth": date
    }

    # create manifest and folders
    for c in categories:
        os.makedirs(os.path.join(newbasepath, c))

    json.dump(fp=open(os.path.join(newbasepath, "manifest.json"),
              "w"), obj=ctf_manifest, ensure_ascii=False)


parser = argparse.ArgumentParser(
    prog='writeup-cli',
    description='Manage writeup directory structure with ease',
    epilog='Copyright Goofy Industries 1420-2069')

parser.add_argument('--dir', '-d', action='store_true',
                    help='Set writeup directory, default is .', default="./")
# command handling
subparsers = parser.add_subparsers(help='Commands')

p_compile = subparsers.add_parser('compile', help="Compile writeup metadata")
p_compile.set_defaults(which="p_compile")

p_create = subparsers.add_parser('create', help="Create new ctf")
p_create.set_defaults(which="p_create")  # Identifier
p_create.add_argument("name", nargs=1, help="Ctf name")
p_create.add_argument("-n", "--dirname", nargs=1, required=False,
                      help="A legal directory name, in case you want the name to be something else than the directory name use this option!", default=None)
p_create.add_argument("-c", "--categories", nargs="+",
                      required=True, help="Categories")
p_create.add_argument('-t', '--yearmonth', nargs=1, required=True,
                      help="When it happened, needs to follow format YYYYMM")

# Funny oneliner to parse and set args to --help if no arguments were passed
args = parser.parse_args(args=sys.argv[1:] if sys.argv[1:] else ['--help'])

get_manifest()
match args.which:
    case "p_create":
        create_ctf(args.name[0], args.categories,
                   args.yearmonth[0], args.dirname)
    case "p_compile":
        compile_data()

#!/usr/bin/python
import argparse, json, os, sys, re

directory = "./"
manifest = {}
def get_manifest():
    global directory, manifest
    if not os.path.exists(os.path.join(directory,"manifest.json")):
        print(f"[ERROR] There's no manifest.json present here ({directory}), have you specified a correct directory?")
        exit(1)
    m = open(os.path.join(directory, "manifest.json"), "r").read()
    manifest = json.loads(m)

def update_manifest():
    global directory, manifest
    if not os.path.exists(os.path.join(directory,"manifest.json")):
        print(f"[ERROR] There's no manifest.json present here ({directory}), have you specified a correct directory?")
        exit(1)
    json.dump(fp=open(os.path.join(directory, "manifest.json"), "w"), ensure_ascii=False, obj=manifest)

def create_ctf(name, categories, yearmonth, dirname=None):
    global directory, manifest
    if dirname == None:
        dirname = re.sub(r'[^\x00-\x7F]', '_', name)
    else:
        dirname = dirname[0]

    categories = [c.lower() for c in categories] # Lowercase em all
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
        "yearmonth": yearmonth
    }

    # create manifest and folders
    for c in categories:
        os.makedirs(os.path.join(newbasepath, c))
    
    json.dump(fp=open(os.path.join(newbasepath, "manifest.json"), "w"), obj=ctf_manifest, ensure_ascii=False)


parser = argparse.ArgumentParser(
                    prog='writeup-cli',
                    description='Manage writeup directory structure with ease',
                    epilog='Copyright Goofy Industries 1420-2069')

parser.add_argument('--dir', '-d', action='store_true', help='Set writeup directory, default is .', default="./")
# command handling
subparsers = parser.add_subparsers(help='Commands')

p_create = subparsers.add_parser('create', help="Create new ctf")
p_create.set_defaults(which="p_create") # Identifier
p_create.add_argument("name", nargs=1, help="Ctf name")
p_create.add_argument("-n", "--dirname", nargs=1, required=False, help="A legal directory name, in case you want the name to be something else than the directory name use this option!", default=None)
p_create.add_argument("-c", "--categories", nargs="+", required=True, help="Categories")
p_create.add_argument('-t', '--yearmonth', nargs=1, required=True, help="When it happened")

# Funny oneliner to parse and set args to --help if no arguments were passed
args = parser.parse_args(args=sys.argv[1:] if sys.argv[1:] else ['--help'])

get_manifest()

match args.which:
    case "p_create":
        create_ctf(args.name[0], args.categories, args.yearmonth[0], args.dirname)

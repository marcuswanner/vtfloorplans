import re, os, glob, sys

linepattern = re.compile("(.*) \(([0-9A-Z]{4})\)$") #to grab lines from list
namepattern = re.compile("[\W]+") #to reformat names
floorpattern = re.compile(".*sa(\d+)\.gif$") #to pull floor num from img name

def touchdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == 17: #File exists
            pass
        else:
            raise e

if os.path.exists("by-name"):
    sys.stderr.write("We need to put things in ./by-name. Get rid of it!\n")
    exit(-1)

blistf = open("buildinglist.html.links-dump", "r")
blist = {}
usednames = []
while 1: 
    line = blistf.readline()
    if len(line) == 0:
        break
    line = line.strip()
    m = linepattern.match(line)
    if not m:
        continue

    simplename = m.group(1).lower()
    simplename = simplename.replace(" ", "-")
    simplename = simplename.replace("&", "and")
    simplename = simplename.replace("/", "-")
    simplename = simplename.replace("'", "")
    simplename = simplename.replace('"', "")
    simplename = namepattern.sub("-", simplename)
    if simplename in usednames: #...yes, there are duplicates...
        suffix = 1
        while simplename+str(suffix).zfill(2) in usednames:
            suffix += 1
            if suffix > 99:
                raise ValueError("Too many duplicate {}\n".format(simplename))
        simplename += str(suffix).zfill(2)
    usednames.append(simplename)
    buildingcode = m.group(2).lower()

    if not buildingcode in blist.keys():
        blist[buildingcode] = []
    blist[buildingcode].append(simplename)

blistf.close()

codelist = [c for c in blist.keys()]
codelist.sort() #sort list for determinism
for buildingcode in codelist:
    for img in glob.glob("floorplans/{}sa*.gif".format(buildingcode)):
        floor = int(floorpattern.match(img).group(1))
        for name in blist[buildingcode]:
            touchdir("by-name/{}".format(name))
            os.symlink("../../"+img, "by-name/{}/fl{}.gif".format(name, floor))

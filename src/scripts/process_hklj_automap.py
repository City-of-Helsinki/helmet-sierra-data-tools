import csv
import re
import json

csvfile = open('output/hkljs_20250506.csv', 'r')
csvobj = csv.reader(csvfile, dialect='excel-tab')

dict = {}

while (row := next(csvobj, None)) is not None:
    cfn = re.sub(r'[^0-9.]', '', row[0])
    if cfn != '':

        dict[cfn] = {"narrow": sorted(json.loads(row[1].replace('\'', '\"'))), "wide": sorted(json.loads(row[2].replace('\'', '\"')))}

jsonfile = open('hklj_automap.json', 'w')

json.dump(dict, jsonfile, indent=2, sort_keys=True, ensure_ascii=True)
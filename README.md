## CSV Exports

### Base script

This repository contains a base script which takes an SQL file as a command line parameter, executes it and stores the result into a file which is configured by command line parameters path, prefix and timestamp format.

```
python -m src.scripts.report -h
usage: python -m src.scripts.report [-h] -s [SQLFILE] -p [PATH] -f [PREFIX] [-b [BATCHSIZE]] [-t [TIMESTAMP]] [-d [DIALECT]]

Generates a CSV report based on SQL file input.

options:
  -h, --help            show this help message and exit
  -s [SQLFILE], --sqlfile [SQLFILE]
                        Path to SQL file (required).
  -p [PATH], --path [PATH]
                        Output path (required).
  -f [PREFIX], --prefix [PREFIX]
                        Output csv file prefix (required).
  -b [BATCHSIZE], --batchsize [BATCHSIZE]
                        Yield interval for asynchonous result streaming (optional, default: 30000).
  -t [TIMESTAMP], --timestamp [TIMESTAMP]
                        Output CSV file timestamp format string (optional, default: %Y%m%d).
  -d [DIALECT], --dialect [DIALECT]
                        Python CSV dialect (optional, default: excel-tab).

The output file is stored into the path with prefix and timestamp concatenated by an underscore.
```

### Helmet catalogue usage snapshot per demographics and geographical location

This report is used to generate statistics of the usage of Helmet catalogue per demographics and geographical areas.

```
python -m src.scripts.report -s ./src/scripts/sql/items_bibs_checkouts_addresses_patrons.sql -p ./output -f helmet_cat_demo_geo
```
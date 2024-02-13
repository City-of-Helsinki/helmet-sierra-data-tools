#!/usr/bin/env python
import os
import asyncio
import time
import datetime
import csv
import argparse
import pathlib

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.sql import text

load_dotenv()
parser = argparse.ArgumentParser(
                    prog='python -m src.scripts.report',
                    description='Generates a CSV report based on SQL file input.',
                    epilog='The output file is stored into the path with prefix and timestamp concatenated by an underscore.')

parser.add_argument('-s', '--sqlfile', type=argparse.FileType('r', encoding='UTF-8'), help="Path to SQL file (required).", required=True, nargs="?")
parser.add_argument('-p', '--path', type=pathlib.Path, help="Output path (required).", required=True, nargs="?")
parser.add_argument('-f', '--prefix', type=str, help="Output csv file prefix (required).", required=True, nargs="?")
parser.add_argument('-b', '--batchsize', type=int, default=30000, help="Yield interval for asynchonous result streaming (optional, default: 30000).", nargs="?")
parser.add_argument('-t', '--timestamp', type=str, default='%Y%m%d', help="Output CSV file timestamp format string (optional, default: %%Y%%m%%d).", nargs="?")
parser.add_argument('-d', '--dialect', type=str, default='excel-tab', help="Python CSV dialect (optional, default: excel-tab).", nargs="?")
args = parser.parse_args()


async def async_main() -> None:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}",
        echo=False
    )

    print("Start report generation.")
    start = time.perf_counter()

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    outpath = args.path / f'{args.prefix}_{datetime.datetime.now().strftime(args.timestamp)}.csv'
    with open(outpath, 'w') as outfile:
        outcsv = csv.writer(outfile, dialect=args.dialect)
        async with async_session() as session:
            stmt = text(
                args.sqlfile.read()
            ).execution_options(stream_results=True, yield_per=args.batchsize)

            result = await session.stream(stmt)

            print(f"Start write at {time.perf_counter() - start:0.4f} seconds")

            outcsv.writerow(result.keys())

            async for row in result:
                outcsv.writerow(row)
                await engine.dispose()
            outfile.close()

        print(f"Finished in {time.perf_counter() - start:0.4f} seconds")

asyncio.run(async_main())

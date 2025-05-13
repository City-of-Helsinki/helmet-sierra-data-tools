#!/usr/bin/env python
import os
import asyncio
import time
import datetime
import argparse
import pathlib
import multiprocessing

from importlib import import_module

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.sql import text

from src.scripts.rowprocessors.baserowprocessor import BaseRowProcessor

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
parser.add_argument('-r', '--rowprocessor', type=argparse.FileType('r', encoding='UTF-8'), help="Path to python script for additional row processing.", required=False, nargs="?")
parser.add_argument('-c', '--cache', type=bool, default=False, help="Cache rows before processing (optional, default: False).", nargs="?")

args = parser.parse_args()

rows = multiprocessing.Manager().list()
lock = multiprocessing.Lock()

try:
    name = args.rowprocessor.name.replace(".py", "").replace("./", "").replace("/", ".")
    processor = getattr(import_module(name), "RowProcessor")
except Exception as e:
    if e:
        print(e)
    processor = BaseRowProcessor


async def async_main() -> None:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}",
        echo=False
    )

    print("Start report generation.")
    start = time.perf_counter()

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    with processor(args.path / f'{args.prefix}_{datetime.datetime.now().strftime(args.timestamp)}.csv', args.dialect) as p:

        async with async_session() as session:
            stmt = text(
                args.sqlfile.read()
            ).execution_options(stream_results=True, yield_per=args.batchsize)

            result = await session.stream(stmt)

            print(f"Start write at {time.perf_counter() - start:0.4f} seconds")

            p.processkeys(result.keys())

            if not args.cache:
                async for row in result:
                    p.processrow(row)
                    await engine.dispose()
            else:
                async for row in result:
                    with lock:
                        rows.append(row)
                    await engine.dispose()

        if args.cache:
            print(f"Start processing cache at {time.perf_counter() - start:0.4f} seconds")
            for row in rows:
                with lock:
                    p.processrow(row)

        print(f"Finished in {time.perf_counter() - start:0.4f} seconds")

asyncio.run(async_main())

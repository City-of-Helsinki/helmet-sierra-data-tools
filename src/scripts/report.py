#!/usr/bin/env python
import os
import asyncio
import time
import datetime
import csv

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.sql import text

load_dotenv()


async def async_main() -> None:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}",
        echo=False
    )
    customSelect = ""
    with open('src/scripts/sql/items_bibs_checkouts_addresses_patrons.sql', encoding="utf-8") as f:
        customSelect = f.read()

    print("Start report generation.")
    start = time.perf_counter()

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    with open(f'helmet_{datetime.date.today().strftime("%Y%m%d")}.csv', 'w') as outfile:
        outcsv = csv.writer(outfile, dialect='excel-tab')
        async with async_session() as session:
            stmt = text(customSelect).execution_options(stream_results=True, yield_per=10000)
            result = await session.stream(stmt)
            print(f"Start write at {time.perf_counter() - start:0.4f} seconds")
            outcsv.writerow(result.keys())
            async for row in result:
                outcsv.writerow(row)
                await engine.dispose()
            outfile.close()
        print(f"Finished in {time.perf_counter() - start:0.4f} seconds")

asyncio.run(async_main())

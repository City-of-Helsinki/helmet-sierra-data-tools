#!/usr/bin/env python
import os
import asyncio
import time
from datetime import datetime

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.orm.item import Item

load_dotenv()


async def async_main() -> None:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}",
        echo=False
    )
    global i
    i = 0
    start = time.perf_counter()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Item).filter(
                (Item.last_checkout_gmt < datetime.now()) & (datetime.now() < Item.last_checkin_gmt)
            ).execution_options(
                stream_results=True, yield_per=1000
            ).options(selectinload(Item.bib))
        result = await session.stream(stmt)
        async for item in result.scalars():
            item.bib
            i += 1
            await engine.dispose()
        print(i)
        end = time.perf_counter()
    print(f"Took {end - start:0.4f} seconds")

asyncio.run(async_main())

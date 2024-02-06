#!/usr/bin/env python
import os
import asyncio
import time

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
    global k
    start = time.perf_counter()
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        stmt = select(Item).limit(1000).execution_options(stream_results=True, yield_per=100).options(selectinload(Item.bib))
        result = await session.stream(stmt)
        async for item in result.scalars():
            k = item.id
        await engine.dispose()
    end = time.perf_counter()
    print(f"Took {end - start:0.4f} seconds")

asyncio.run(async_main())

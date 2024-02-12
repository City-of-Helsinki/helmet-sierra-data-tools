#!/usr/bin/env python
import os
import asyncio
import time

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.orm.patron import Patron

load_dotenv()


async def async_main() -> None:
    engine = create_async_engine(
        f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}",
        echo=False
    )
    start = time.perf_counter()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Patron).execution_options(
            stream_results=True,
            yield_per=1000
        ).options(
            selectinload(Patron.fullname),
            selectinload(Patron.addresses),
            selectinload(Patron.phones),
            selectinload(Patron.varfields),
        )
        result = await session.stream(stmt)
        async for patron in result.scalars():
            print(patron.__dict__)
            await engine.dispose()
        end = time.perf_counter()
    print(f"Took {end - start:0.4f} seconds")

asyncio.run(async_main())

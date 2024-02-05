#!/usr/bin/env python
import os
from dotenv import load_dotenv
import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from orm.item import Item
from datetime import datetime, timedelta

load_dotenv()

engine = create_engine(f"postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}")

Session = sessionmaker(bind=engine)

session = Session()

item = session.query(Item).filter(Item.last_checkout_gmt > datetime.now() - timedelta(days=21)).first()
#item = session.query(CircTrans)

result = []
if item.bib.items:
    for qws_instance in item.bib.items:
        result.append(qws_instance.__dict__)

pprint.PrettyPrinter(depth=4).pprint(item.bib.items[0].bib.__dict__)

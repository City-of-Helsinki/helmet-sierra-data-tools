#!/usr/bin/env python
import os
from dotenv import load_dotenv
import pprint
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import sessionmaker

from orm.item import Item
from orm.patron import Patron
from orm.circ_trans import CircTrans
import pprint
from datetime import *



load_dotenv()

engine = create_engine(f"postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}")

Session = sessionmaker(bind=engine)

session = Session()

item = session.query(Item).filter(Item.last_checkout_gmt > datetime.now() - timedelta(days=21)).first()
#item = session.query(CircTrans)
print()

pprint.PrettyPrinter(depth=4).pprint(item.varfields[1].__dict__)
#!/usr/bin/env python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker

from saxonche import PySaxonProcessor

from pymarc import Record, Field, Subfield
from pymarc import marcxml

from src.orm.bib import Bib
from src.orm.fields import Subfield

load_dotenv()

engine = create_engine(f"postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}")

Session = sessionmaker(bind=engine)

session = Session()

bibs = session.query(Bib).filter(
    Bib.record_id.in_(
        select(Subfield.record_id).where(
            and_(
                and_(
                    Subfield.marc_tag == "245",
                    Subfield.tag == "a"
                ),
                Subfield.content.contains("Sinuhe")
            )
        )
    )).all()

records = []

print(len(bibs))

for bib in bibs:
    base_address=bib.leaderfields[0].base_address if bib.leaderfields[0].base_address else "     "
    marc_leader=(
        f'     {bib.leaderfields[0].record_status_code}'
        f'{bib.leaderfields[0].record_status_code}'
        f'{bib.leaderfields[0].bib_level_code} '
        f'{bib.leaderfields[0].char_encoding_scheme_code}'
        f'22{"{:>5}".format(base_address)}'
        f'{bib.leaderfields[0].encoding_level_code} '
        f'{bib.leaderfields[0].multipart_level_code}    '
    )
    record = Record(leader=marc_leader)
    for varfield in bib.varfields:
        subfields = []
        for subfield in varfield.subfields:
            subfields.append(Subfield(subfield.tag, subfield.content))
        record.add_field(
            Field(
                tag = varfield.marc_tag,
                indicators = [varfield.marc_ind1, varfield.marc_ind2],
                data = varfield.field_content,
                subfields = subfields
            )
        )
    records.append(record)

import xml.etree.ElementTree as ET
element = ET.XML(marcxml.record_to_xml(records[0], quiet=True, namespace=True))
ET.indent(element)
print(ET.tostring(element, encoding='unicode'))

with PySaxonProcessor(license=False) as proc:
    xslt30_processor = proc.new_xslt30_processor()
    document = proc.parse_xml(xml_text=marcxml.record_to_xml(records[0], quiet=True, namespace=True).decode('utf-8'))
    xslt30_transformer = xslt30_processor.compile_stylesheet(stylesheet_file = 'marc2bibframe2-v.2.4.0/xsl/marc2bibframe2.xsl')
    result = xslt30_transformer.apply_templates_returning_value(xdm_value = document)
    print(result)

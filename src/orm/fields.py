from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

import src.orm.base
import src.orm.bib
import src.orm.item


class Leaderfield(src.orm.base.Base):
    __tablename__ = 'leader_field'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    record_status_code: Mapped[str] = mapped_column("record_status_code")
    record_type_code: Mapped[str] = mapped_column("record_type_code")
    bib_level_code: Mapped[str] = mapped_column("bib_level_code")
    char_encoding_scheme_code: Mapped[str] = mapped_column("char_encoding_scheme_code")
    encoding_level_code: Mapped[str] = mapped_column("encoding_level_code")
    descriptive_cat_form_code: Mapped[str] = mapped_column("descriptive_cat_form_code")
    multipart_level_code: Mapped[str] = mapped_column("multipart_level_code")
    base_address: Mapped[str] = mapped_column("base_address")


class Controlfield(src.orm.base.Base):
    __tablename__ = 'control_field'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    varfield_type_code: Mapped[str] = mapped_column("varfield_type_code", String)
    control_num: Mapped[int] = mapped_column("control_num")
    p00: Mapped[str] = mapped_column("p00")
    p01: Mapped[str] = mapped_column("p01")
    p02: Mapped[str] = mapped_column("p02")
    p03: Mapped[str] = mapped_column("p03")
    p04: Mapped[str] = mapped_column("p04")
    p05: Mapped[str] = mapped_column("p05")
    p06: Mapped[str] = mapped_column("p06")
    p07: Mapped[str] = mapped_column("p07")
    p08: Mapped[str] = mapped_column("p08")
    p09: Mapped[str] = mapped_column("p09")
    p10: Mapped[str] = mapped_column("p10")
    p11: Mapped[str] = mapped_column("p11")
    p12: Mapped[str] = mapped_column("p12")
    p13: Mapped[str] = mapped_column("p13")
    p14: Mapped[str] = mapped_column("p14")
    p15: Mapped[str] = mapped_column("p15")
    p16: Mapped[str] = mapped_column("p16")
    p17: Mapped[str] = mapped_column("p17")
    p18: Mapped[str] = mapped_column("p18")
    p19: Mapped[str] = mapped_column("p19")
    p20: Mapped[str] = mapped_column("p20")
    p21: Mapped[str] = mapped_column("p21")
    p22: Mapped[str] = mapped_column("p22")
    p23: Mapped[str] = mapped_column("p23")
    p24: Mapped[str] = mapped_column("p24")
    p25: Mapped[str] = mapped_column("p25")
    p26: Mapped[str] = mapped_column("p26")
    p27: Mapped[str] = mapped_column("p27")
    p28: Mapped[str] = mapped_column("p28")
    p29: Mapped[str] = mapped_column("p29")
    p30: Mapped[str] = mapped_column("p30")
    p31: Mapped[str] = mapped_column("p31")
    p32: Mapped[str] = mapped_column("p32")
    p33: Mapped[str] = mapped_column("p33")
    p34: Mapped[str] = mapped_column("p34")
    p35: Mapped[str] = mapped_column("p35")
    p36: Mapped[str] = mapped_column("p36")
    p37: Mapped[str] = mapped_column("p37")
    p38: Mapped[str] = mapped_column("p38")
    p39: Mapped[str] = mapped_column("p39")
    p40: Mapped[str] = mapped_column("p40")
    p41: Mapped[str] = mapped_column("p41")
    p42: Mapped[str] = mapped_column("p42")
    p43: Mapped[str] = mapped_column("p43")
    occ_num: Mapped[int] = mapped_column("occ_num")
    remainder: Mapped[int] = mapped_column("remainder")


class Varfield(src.orm.base.Base):
    __tablename__ = 'varfield'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    varfield_type_code: Mapped[str] = mapped_column("varfield_type_code")
    marc_tag: Mapped[str] = mapped_column("marc_tag")
    marc_ind1: Mapped[str] = mapped_column("marc_ind1")
    marc_ind2: Mapped[str] = mapped_column("marc_ind2")
    occ_num: Mapped[str] = mapped_column("occ_num")
    field_content: Mapped[str] = mapped_column("field_content")
    subfields: Mapped[List["Subfield"]] = relationship(back_populates="varfield", lazy='joined')


class Subfield(src.orm.base.Base):
    __tablename__ = 'subfield'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    __mapper_args__ = {
        "primary_key": ['record_id', 'varfield_id', 'tag']
    }
    record_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    varfield_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sierra_view.varfield.id"))
    varfield_type_code: Mapped[str] = mapped_column("field_type_code")
    marc_tag: Mapped[str] = mapped_column("marc_tag")
    marc_ind1: Mapped[str] = mapped_column("marc_ind1")
    marc_ind2: Mapped[str] = mapped_column("marc_ind2")
    occ_num: Mapped[str] = mapped_column("occ_num")
    display_order: Mapped[int] = mapped_column("display_order")
    tag: Mapped[str] = mapped_column("tag")
    content: Mapped[str] = mapped_column("content")
    varfield: Mapped[Varfield] = relationship(back_populates="subfields")

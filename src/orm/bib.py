from __future__ import annotations

from typing import List
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

import src.orm.base
import src.orm.fields
import src.orm.item
import src.orm.bib_item
import src.orm.volume
import src.orm.bib_volume
import src.orm.order
import src.orm.bib_order
import src.orm.holding
import src.orm.bib_holding


class Bib(src.orm.base.Base):
    __tablename__ = 'bib_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", BigInteger, primary_key=True)
    language_code: Mapped[str] = mapped_column("language_code")
    bcode1: Mapped[str] = mapped_column("bcode1")
    bcode2: Mapped[str] = mapped_column("bcode2")
    bcode3: Mapped[str] = mapped_column("bcode3")
    country_code: Mapped[str] = mapped_column("country_code")
    index_change_count: Mapped[str] = mapped_column("index_change_count")
    is_on_course_reserve: Mapped[str] = mapped_column("is_on_course_reserve")
    is_right_result_exact: Mapped[str] = mapped_column("is_right_result_exact")
    allocation_rule_code: Mapped[str] = mapped_column("allocation_rule_code")
    skip_num: Mapped[int] = mapped_column("skip_num")
    cataloging_date_gmt: Mapped[datetime] = mapped_column("cataloging_date_gmt")
    marc_type_code: Mapped[str] = mapped_column("marc_type_code")
    is_suppressed: Mapped[bool] = mapped_column("is_suppressed")
    leaderfields:  Mapped[List["src.orm.fields.Leaderfield"]] = relationship(
        "src.orm.fields.Leaderfield",
        primaryjoin='src.orm.fields.Leaderfield.record_id == Bib.record_id',
        foreign_keys='src.orm.fields.Leaderfield.record_id',
        lazy='joined'
    )
    controlfields: Mapped[List["src.orm.fields.Controlfield"]] = relationship(
        "src.orm.fields.Controlfield",
        primaryjoin='src.orm.fields.Controlfield.record_id == Bib.record_id',
        foreign_keys='src.orm.fields.Controlfield.record_id',
        lazy='joined'
    )
    varfields: Mapped[List["src.orm.fields.Varfield"]] = relationship(
        "src.orm.fields.Varfield",
        primaryjoin='src.orm.fields.Varfield.record_id == Bib.record_id',
        foreign_keys='src.orm.fields.Varfield.record_id',
        lazy='joined'
    )
    items: Mapped[List["src.orm.item.Item"]] = relationship(
        "src.orm.item.Item",
        secondary=src.orm.bib_item.BibItem.__table__,
        back_populates="bib",
        lazy='select'
    )
    volumes: Mapped[List["src.orm.volume.Volume"]] = relationship(
        "src.orm.volume.Volume",
        secondary=src.orm.bib_volume.BibVolume.__table__,
        back_populates="bibs",
        lazy='select'
    )
    orders: Mapped[List["src.orm.order.Order"]] = relationship(
        "src.orm.order.Order",
        secondary=src.orm.bib_order.BibOrder.__table__,
        back_populates="bibs",
        lazy='select'
    )
    holdings: Mapped[List["src.orm.holding.Holding"]] = relationship(
        "src.orm.holding.Holding",
        secondary=src.orm.bib_holding.BibHolding.__table__,
        back_populates="bib",
        lazy='select'
    )

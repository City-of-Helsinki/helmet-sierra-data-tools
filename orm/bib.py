from __future__ import annotations

from typing import List
from datetime import datetime

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orm.base import Base
import orm.fields
import orm.item
import orm.bib_item


class Bib(Base):
    __tablename__ = 'bib_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", Integer, primary_key=True)
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
    leaderfields:  Mapped[List["orm.fields.Leaderfield"]] = relationship(
        "orm.fields.Leaderfield",
        primaryjoin='orm.fields.Leaderfield.record_id == Bib.record_id',
        foreign_keys='orm.fields.Leaderfield.record_id',
        lazy='joined'
    )
    controlfields: Mapped[List["orm.fields.Controlfield"]] = relationship(
        "orm.fields.Controlfield",
        primaryjoin='orm.fields.Controlfield.record_id == Bib.record_id',
        foreign_keys='orm.fields.Controlfield.record_id',
        lazy='joined'
    )
    varfields: Mapped[List["orm.fields.Varfield"]] = relationship(
        "orm.fields.Varfield",
        primaryjoin='orm.fields.Varfield.record_id == Bib.record_id',
        foreign_keys='orm.fields.Varfield.record_id',
        lazy='joined'
    )
    items: Mapped[List["orm.item.Item"]] = relationship(
        "orm.item.Item",
        secondary=orm.bib_item.BibItem.__table__,
        back_populates="bib",
        lazy='select'
    )

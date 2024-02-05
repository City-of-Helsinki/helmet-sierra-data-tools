from __future__ import annotations

from typing import List
from typing import Optional

from datetime import datetime

from sqlalchemy import ForeignKey, func, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from orm.base import Base
import orm.fields
import orm.patron
import orm.bib


class CircTrans(Base):
    __tablename__ = 'circ_trans'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    transaction_gmt: Mapped[datetime] = mapped_column("transaction_gmt")
    application_name: Mapped[str] = mapped_column("application_name")
    source_code: Mapped[str] = mapped_column("source_code")
    op_code: Mapped[str] = mapped_column("op_code")
    patron_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.patron.record_id"))
    patron: Mapped["orm.patron.Patron"] = relationship(
        "orm.patron.Patron",
        primaryjoin='orm.patron.Patron.record_id == CircTrans.patron_record_id',
        foreign_keys='orm.patron.Patron.record_id',
        #lazy='joined'
    )
    item_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.item.record_id"))
    item: Mapped["orm.item.Item"] = relationship(
        "orm.item.Item",
        primaryjoin='orm.item.Item.record_id == CircTrans.item_record_id',
        foreign_keys='orm.item.Item.record_id',
        #lazy='joined'
    )
    volume_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.volume.record_id"))
    bib_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.bib.record_id"))
    bib: Mapped["orm.bib.Bib"] = relationship(
        "orm.bib.Bib",
        primaryjoin='orm.bib.Bib.record_id == CircTrans.bib_record_id',
        foreign_keys='orm.bib.Bib.record_id',
        #lazy='joined'
    )

    stat_group_code_num: Mapped[int] = mapped_column("stat_group_code_num")
    due_date_gmt: Mapped[datetime] = mapped_column("due_date_gmt")
    count_type_code_num: Mapped[int] = mapped_column("count_type_code_num")
    itype_code_num: Mapped[int] = mapped_column("itype_code_num")
    icode1: Mapped[int] = mapped_column("icode1")
    icode2: Mapped[str] = mapped_column("icode2")
    item_location_code: Mapped[str] = mapped_column("item_location_code")
    item_agency_code_num: Mapped[int] = mapped_column("item_agency_code_num")
    ptype_code: Mapped[str] = mapped_column("ptype_code")
    pcode1: Mapped[str] = mapped_column("pcode1")
    pcode2: Mapped[str] = mapped_column("pcode2")
    pcode3: Mapped[int] = mapped_column("pcode3")
    pcode4: Mapped[int] = mapped_column("pcode4")
    patron_home_library_code: Mapped[str] = mapped_column("patron_home_library_code")
    patron_agency_code_num: Mapped[int] = mapped_column("patron_agency_code_num")
    loanrule_code_num: Mapped[int] = mapped_column("loanrule_code_num")
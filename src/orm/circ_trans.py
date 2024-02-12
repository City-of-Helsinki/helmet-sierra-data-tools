from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.orm.base import Base
import src.orm.fields
import src.orm.patron
import src.orm.bib
import src.orm.item


class CircTrans(Base):
    __tablename__ = 'circ_trans'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    transaction_gmt: Mapped[datetime] = mapped_column("transaction_gmt")
    application_name: Mapped[str] = mapped_column("application_name")
    source_code: Mapped[str] = mapped_column("source_code")
    op_code: Mapped[str] = mapped_column("op_code")
    patron_record_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sierra_view.patron.record_id"))
    patron: Mapped["src.orm.patron.Patron"] = relationship(
        "src.orm.patron.Patron",
        primaryjoin='src.orm.patron.Patron.record_id == CircTrans.patron_record_id',
        foreign_keys='src.orm.patron.Patron.record_id'
    )
    item_record_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sierra_view.item.record_id"))
    item: Mapped["src.orm.item.Item"] = relationship(
        "src.orm.item.Item",
        primaryjoin='src.orm.item.Item.record_id == CircTrans.item_record_id',
        foreign_keys='src.orm.item.Item.record_id'
    )
    volume_record_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sierra_view.volume.record_id"))
    bib_record_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sierra_view.bib.record_id"))
    bib: Mapped["src.orm.bib.Bib"] = relationship(
        "src.orm.bib.Bib",
        primaryjoin='src.orm.bib.Bib.record_id == CircTrans.bib_record_id',
        foreign_keys='src.orm.bib.Bib.record_id'
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

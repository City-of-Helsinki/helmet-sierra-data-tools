from __future__ import annotations

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

import src.orm.base
import src.orm.bib
import src.orm.bib_holding
import src.orm.item
import src.orm.item_holding


class Holding(src.orm.base.Base):
    __tablename__ = 'holding_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", BigInteger, primary_key=True)
    is_inherit_loc: Mapped[bool] = mapped_column("is_inherit_loc")
    allocation_rule_code: Mapped[str] = mapped_column("allocation_rule_code")
    accounting_unit_code_num: Mapped[int] = mapped_column("accounting_unit_code_num")
    label_code: Mapped[str] = mapped_column("label_code")
    scode1: Mapped[str] = mapped_column("scode1")
    scode2: Mapped[str] = mapped_column("scode2")
    claimon_date_gmt: Mapped[datetime] = mapped_column("claimon_date_gmt")
    receiving_location_code: Mapped[str] = mapped_column("receiving_location_code")
    vendor_code: Mapped[str] = mapped_column("vendor_code")
    scode3: Mapped[str] = mapped_column("scode3")
    scode4: Mapped[str] = mapped_column("scode4")
    update_cnt: Mapped[str] = mapped_column("update_cnt")
    piece_cnt: Mapped[int] = mapped_column("piece_cnt")
    echeckin_code: Mapped[str] = mapped_column("echeckin_code")
    media_type_code: Mapped[str] = mapped_column("media_type_code")
    is_suppressed: Mapped[bool] = mapped_column("is_suppressed")
    bib: Mapped["src.orm.bib.Bib"] = relationship(
        "src.orm.bib.Bib",
        secondary=src.orm.bib_holding.BibHolding.__table__,
        back_populates="holdings"
    )
    item: Mapped["src.orm.item.Item"] = relationship(
        "src.orm.item.Item",
        secondary=src.orm.item_holding.ItemHolding.__table__,
        back_populates="holdings"
    )

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

import orm.base
import orm.bib
import orm.holding


class BibHolding(orm.base.Base):
    __tablename__ = 'bib_record_holding_record_link'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    bib_record_id: Mapped[int] = mapped_column("bib_record_id", ForeignKey("sierra_view.bib_record.record_id"))
    holding_record_id: Mapped[int] = mapped_column("holding_record_id", ForeignKey("sierra_view.holding_record.record_id"))
    holdings_display_order: Mapped[int] = mapped_column("holdings_display_order")

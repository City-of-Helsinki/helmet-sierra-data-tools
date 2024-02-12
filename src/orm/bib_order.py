from __future__ import annotations

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

import src.orm.base


class BibOrder(src.orm.base.Base):
    __tablename__ = 'bib_record_order_record_link'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    bib_record_id: Mapped[int] = mapped_column("bib_record_id", ForeignKey("sierra_view.bib_record.record_id"))
    order_record_id: Mapped[int] = mapped_column("order_record_id", ForeignKey("sierra_view.order_record.record_id"))
    orders_display_order: Mapped[int] = mapped_column("orders_display_order")

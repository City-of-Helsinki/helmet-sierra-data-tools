from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

import orm.base
import orm.item
import orm.holding


class ItemHolding(orm.base.Base):
    __tablename__ = 'holding_record_item_record_link'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    item_record_id: Mapped[int] = mapped_column("item_record_id", ForeignKey("sierra_view.item_record.record_id"))
    holding_record_id: Mapped[int] = mapped_column("holding_record_id", ForeignKey("sierra_view.holding_record.record_id"))
    items_display_order: Mapped[int] = mapped_column("items_display_order")
    holdings_display_order: Mapped[int] = mapped_column("holdings_display_order")

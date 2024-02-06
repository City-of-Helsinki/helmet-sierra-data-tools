from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

import src.orm.base


class ItemVolume(src.orm.base.Base):
    __tablename__ = 'volume_record_item_record_link'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    item_record_id: Mapped[int] = mapped_column("item_record_id", ForeignKey("sierra_view.item_record.record_id"))
    volume_record_id: Mapped[int] = mapped_column("volume_record_id", ForeignKey("sierra_view.volume_record.record_id"))
    items_display_order: Mapped[int] = mapped_column("items_display_order")

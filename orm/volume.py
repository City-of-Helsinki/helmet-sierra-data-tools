from __future__ import annotations

from typing import List

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

import orm.base
import orm.bib
import orm.bib_volume
import orm.item
import orm.item_volume


class Volume(orm.base.Base):
    __tablename__ = 'volume_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", Integer, primary_key=True)
    sort_order: Mapped[int] = mapped_column("sort_order")
    is_suppressed: Mapped[bool] = mapped_column("is_suppressed")
    bibs: Mapped[List["orm.bib.Bib"]] = relationship(
        "orm.bib.Bib",
        secondary=orm.bib_volume.BibVolume.__table__,
        back_populates="volumes"
    )
    items: Mapped[List["orm.item.Item"]] = relationship(
        "orm.item.Item",
        secondary=orm.item_volume.ItemVolume.__table__,
        back_populates="volumes"
    )
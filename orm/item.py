from __future__ import annotations

from typing import List
from decimal import Decimal
from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

import orm.base
import orm.bib
import orm.bib_item
import orm.patron
import orm.fields
import orm.item_holding
import orm.holding
import orm.item_volume
import orm.volume


class Item(orm.base.Base):
    __tablename__ = 'item_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", Integer, primary_key=True)
    icode1: Mapped[int] = mapped_column("icode1")
    icode2: Mapped[str] = mapped_column("icode2")
    itype_code_num: Mapped[int] = mapped_column("itype_code_num")
    location_code: Mapped[str] = mapped_column("location_code")
    agency_code_num: Mapped[int] = mapped_column("agency_code_num")
    item_status_code: Mapped[int] = mapped_column("item_status_code")
    is_inherit_loc: Mapped[bool] = mapped_column("is_inherit_loc")
    price: Mapped[Decimal] = mapped_column("price")
    last_checkin_gmt: Mapped[datetime] = mapped_column("last_checkin_gmt")
    checkout_total: Mapped[int] = mapped_column("checkout_total")
    renewal_total: Mapped[int] = mapped_column("renewal_total")
    last_year_to_date_checkout_total: Mapped[int] = mapped_column("last_year_to_date_checkout_total")
    year_to_date_checkout_total: Mapped[int] = mapped_column("year_to_date_checkout_total")
    is_bib_hold: Mapped[bool] = mapped_column("is_bib_hold")
    copy_num: Mapped[int] = mapped_column("copy_num")
    checkout_statistic_group_code_num: Mapped[int] = mapped_column("checkout_statistic_group_code_num")
    last_patron_record_metadata_id: Mapped[int] = mapped_column(ForeignKey("sierra_view.patron_record.record_id"))
    last_patron: Mapped["orm.patron.Patron"] = relationship("Patron", back_populates="last_patron_of_items")
    inventory_gmt: Mapped[datetime] = mapped_column("inventory_gmt")
    checkin_statistics_group_code_num: Mapped[int] = mapped_column("checkin_statistics_group_code_num")
    use3_count: Mapped[int] = mapped_column("use3_count")
    last_checkout_gmt: Mapped[datetime] = mapped_column("last_checkout_gmt")
    internal_use_count: Mapped[int] = mapped_column("internal_use_count")
    copy_use_count: Mapped[int] = mapped_column("copy_use_count")
    item_message_code: Mapped[str] = mapped_column("item_message_code")
    opac_message_code: Mapped[str] = mapped_column("opac_message_code")
    virtual_type_code: Mapped[str] = mapped_column("virtual_type_code")
    virtual_item_central_code_num: Mapped[int] = mapped_column("virtual_item_central_code_num")
    holdings_code: Mapped[str] = mapped_column("holdings_code")
    save_itype_code_num: Mapped[int] = mapped_column("save_itype_code_num")
    save_location_code: Mapped[str] = mapped_column("save_location_code")
    save_checkout_total: Mapped[int] = mapped_column("save_checkout_total")
    old_location_code: Mapped[str] = mapped_column("old_location_code")
    distance_learning_status: Mapped[int] = mapped_column("distance_learning_status")
    is_suppressed: Mapped[bool] = mapped_column("is_suppressed")
    is_available_at_library: Mapped[bool] = mapped_column("is_available_at_library")
    last_status_update: Mapped[datetime] = mapped_column("last_status_update")
    varfields: Mapped[List["orm.fields.Varfield"]] = relationship(
        "orm.fields.Varfield",
        primaryjoin='orm.fields.Varfield.record_id == Item.record_id',
        foreign_keys='orm.fields.Varfield.record_id',
        lazy='joined',
        overlaps="varfields"
    )
    bib: Mapped["orm.bib.Bib"] = relationship(
        "orm.bib.Bib",
        secondary=orm.bib_item.BibItem.__table__,
        back_populates="items"
    )
    holdings: Mapped[List["orm.holding.Holding"]] = relationship(
        "orm.holding.Holding",
        secondary=orm.item_holding.ItemHolding.__table__,
        back_populates="item",
        lazy='select'
    )
    volumes: Mapped[List["orm.holding.Holding"]] = relationship(
        "orm.volume.Volume",
        secondary=orm.item_volume.ItemVolume.__table__,
        back_populates="items",
        lazy='select'
    )

from __future__ import annotations

from typing import List

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from decimal import Decimal

import src.orm.base
import src.orm.bib
import src.orm.bib_order


class Order(src.orm.base.Base):
    __tablename__ = 'order_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", BigInteger, primary_key=True)
    accounting_unit_code_num: Mapped[int] = mapped_column("accounting_unit_code_num")
    acq_type_code: Mapped[str] = mapped_column("acq_type_code")
    catalog_date_gmt: Mapped[datetime] = mapped_column("catalog_date_gmt")
    claim_action_code: Mapped[str] = mapped_column("claim_action_code")
    ocode1: Mapped[str] = mapped_column("ocode1")
    ocode2: Mapped[str] = mapped_column("ocode2")
    ocode3: Mapped[str] = mapped_column("ocode3")
    ocode4: Mapped[str] = mapped_column("ocode4")
    estimated_price: Mapped[Decimal] = mapped_column("estimated_price")
    form_code: Mapped[str] = mapped_column("form_code")
    order_date_gmt: Mapped[datetime] = mapped_column("order_date_gmt")
    order_note_code: Mapped[str] = mapped_column("order_note_code")
    order_type_code: Mapped[str] = mapped_column("order_type_code")
    receiving_action_code: Mapped[str] = mapped_column("receiving_action_code")
    received_date_gmt: Mapped[datetime] = mapped_column("received_date_gmt")
    receiving_location_code: Mapped[str] = mapped_column("receiving_location_code")
    billing_location_code: Mapped[str] = mapped_column("billing_location_code")
    order_status_code: Mapped[str] = mapped_column("order_status_code")
    temporary_location_code: Mapped[str] = mapped_column("temporary_location_code")
    vendor_record_code: Mapped[str] = mapped_column("vendor_record_code")
    language_code: Mapped[str] = mapped_column("language_code")
    blanket_purchase_order_num: Mapped[str] = mapped_column("blanket_purchase_order_num")
    country_code: Mapped[str] = mapped_column("country_code")
    volume_count: Mapped[int] = mapped_column("volume_count")
    fund_allocation_rule_code: Mapped[str] = mapped_column("fund_allocation_rule_code")
    reopen_text: Mapped[str] = mapped_column("reopen_text")
    list_price: Mapped[Decimal] = mapped_column("list_price")
    list_price_foreign_amt: Mapped[Decimal] = mapped_column("list_price_foreign_amt")
    list_price_discount_amt: Mapped[Decimal] = mapped_column("list_price_discount_amt")
    list_price_service_charge: Mapped[Decimal] = mapped_column("list_price_service_charge")
    is_suppressed: Mapped[bool] = mapped_column("is_suppressed")
    fund_copies_paid: Mapped[int] = mapped_column("fund_copies_paid")
    bibs: Mapped[List["src.orm.bib.Bib"]] = relationship(
        "src.orm.bib.Bib",
        secondary=src.orm.bib_order.BibOrder.__table__,
        back_populates="orders"
    )

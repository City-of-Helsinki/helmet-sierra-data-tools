from __future__ import annotations

from typing import List
from decimal import Decimal
from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orm.base import Base
import orm.fields
import orm.item


class Patron(Base):
    __tablename__ = 'patron_record'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column("record_id", Integer, primary_key=True)
    ptype_code: Mapped[int] = mapped_column("ptype_code")
    home_library_code: Mapped[str] = mapped_column("home_library_code")
    expiration_date_gmt: Mapped[datetime] = mapped_column("expiration_date_gmt")
    pcode1: Mapped[str] = mapped_column("pcode1")
    pcode2: Mapped[str] = mapped_column("pcode2")
    pcode3: Mapped[int] = mapped_column("pcode3")
    pcode4: Mapped[int] = mapped_column("pcode4")
    birth_date_gmt: Mapped[datetime] = mapped_column("birth_date_gmt")
    mblock_code: Mapped[str] = mapped_column("mblock_code")
    firm_code: Mapped[str] = mapped_column("firm_code")
    block_until_date_gmt: Mapped[datetime] = mapped_column("block_until_date_gmt")
    patron_agency_code_num: Mapped[int] = mapped_column("patron_agency_code_num")
    iii_language_pref_code: Mapped[str] = mapped_column("iii_language_pref_code")
    checkout_total: Mapped[int] = mapped_column("checkout_total")
    renewal_total: Mapped[int] = mapped_column("renewal_total")
    checkout_count: Mapped[int] = mapped_column("checkout_count")
    patron_message_code: Mapped[str] = mapped_column("patron_message_code")
    highest_level_overdue_num: Mapped[int] = mapped_column("highest_level_overdue_num")
    claims_returned_total: Mapped[int] = mapped_column("claims_returned_total")
    owed_amt: Mapped[Decimal] = mapped_column("owed_amt")
    itema_count: Mapped[int] = mapped_column("itema_count")
    itemb_count: Mapped[int] = mapped_column("itemb_count")
    overdue_penalty_count: Mapped[int] = mapped_column("overdue_penalty_count")
    ill_checkout_total: Mapped[int] = mapped_column("ill_checkout_total")
    debit_amt: Mapped[Decimal] = mapped_column("debit_amt")
    itemc_count: Mapped[int] = mapped_column("itemc_count")
    itemd_count: Mapped[int] = mapped_column("itemd_count")
    activity_gmt: Mapped[datetime] = mapped_column("activity_gmt")
    notification_medium_code: Mapped[str] = mapped_column("notification_medium_code")
    registration_count: Mapped[int] = mapped_column("registration_count")
    registration_total: Mapped[int] = mapped_column("registration_total")
    attendance_total: Mapped[int] = mapped_column("attendance_total")
    waitlist_count: Mapped[int] = mapped_column("waitlist_count")
    is_reading_history_opt_in: Mapped[bool] = mapped_column("is_reading_history_opt_in")
    fullname: Mapped["FullName"] = relationship(back_populates="patron", lazy='joined')
    addresses: Mapped[List["Address"]] = relationship(back_populates="patron", lazy='joined')
    phones: Mapped[List["Phone"]] = relationship(back_populates="patron", lazy='joined')
    varfields: Mapped[List["orm.fields.Varfield"]] = relationship(
        "Varfield",
        primaryjoin='Varfield.record_id == Patron.record_id',
        foreign_keys='Varfield.record_id',
        lazy='joined',
        overlaps="varfields"
    )
    last_patron_of_items: Mapped[List["orm.item.Item"]] = relationship(back_populates="last_patron")


class Address(Base):
    __tablename__ = 'patron_record_address'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    patron_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.patron_record.id"))
    patron: Mapped["Patron"] = relationship(back_populates="addresses")
    patron_record_address_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.patron_record_address_type.id"))
    address_type: Mapped["AddressType"] = relationship("AddressType", primaryjoin="Address.patron_record_address_type_id==AddressType.id")
    display_order: Mapped[int] = mapped_column("display_order")
    addr1: Mapped[str] = mapped_column("addr1")
    addr2: Mapped[str] = mapped_column("addr2")
    addr3: Mapped[str] = mapped_column("addr3")
    village: Mapped[str] = mapped_column("village")
    city: Mapped[str] = mapped_column("city")
    region: Mapped[str] = mapped_column("region")
    postal_code: Mapped[str] = mapped_column("postal_code")
    country: Mapped[str] = mapped_column("country")


class AddressType(Base):
    __tablename__ = 'patron_record_address_type'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    code: Mapped[str] = mapped_column("code")
    address: Mapped["Address"] = relationship(back_populates="address_type")


class FullName(Base):
    __tablename__ = 'patron_record_fullname'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    patron_record_id: Mapped[Patron] = mapped_column(Integer, ForeignKey("sierra_view.patron_record.id"))
    patron: Mapped["Patron"] = relationship(back_populates="fullname")
    display_order: Mapped[int] = mapped_column("display_order")
    prefix: Mapped[str] = mapped_column("prefix")
    first_name: Mapped[str] = mapped_column("first_name")
    middle_name: Mapped[str] = mapped_column("middle_name")
    last_name: Mapped[str] = mapped_column("last_name")
    suffix: Mapped[str] = mapped_column("suffix")


class Phone(Base):
    __tablename__ = 'patron_record_phone'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    patron_record_id: Mapped[Patron] = mapped_column(Integer, ForeignKey("sierra_view.patron_record.id"))
    patron: Mapped["Patron"] = relationship(back_populates="phones")
    patron_record_phone_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("sierra_view.patron_record_phone_type.id"))
    phone_type: Mapped["PhoneType"] = relationship(back_populates="phone", lazy='joined')
    display_order: Mapped[int] = mapped_column("display_order")
    phone_number: Mapped[str] = mapped_column("phone_number")


class PhoneType(Base):
    __tablename__ = 'patron_record_phone_type'
    __table_args__ = {
        'info': dict(is_view=True),
        'schema': 'sierra_view'
    }
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    code: Mapped[str] = mapped_column("code")
    phone: Mapped["Phone"] = relationship(back_populates="phone_type")

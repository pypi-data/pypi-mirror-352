# -*- coding: utf-8 -*-
#
# Swiss QR Bill Generator
# Copyright (c) 2017 Manuel Bleichenbacher
# Licensed under MIT License
# https://opensource.org/licenses/MIT
#
# C#   : https://github.com/manuelbl/SwissQRBill.NET
# Java : https://github.com/manuelbl/SwissQRBill
#
# Code ported to Python by Martin Mohnhaupt, m.mohnhaupt@bluewin.ch
# Copyright (c) 2022 Martin Mohnhaupt
#
from typing import List
from .address import Address, AddressType
from .bill import Bill


class QRCodeText:
    """Class for encoding the text embedded in the QR code."""

    def __init__(self, bill: Bill) -> None:
        self._bill = bill
        self._text = []

    @staticmethod
    def create(bill: Bill) -> str:
        """Create the string from which a QR code is to be generated (according to the data structure defined by SIX).

        Args:
            bill (Bill): The source bill to be "QR coded"

        Returns:
            str: The textual data
        """
        return QRCodeText(bill)._create_text()

    def _create_text(self) -> List[str]:
        """Create the QR code embedded text.

        Returns:
            List[str]: The QR code textual data
        """
        # Header
        self._text.append("SPC")  # QRType
        self._text.append("0200")  # Version
        self._text.append("1")  # Coding
        # CdtrInf
        self._append_data_field(self._bill.account)  # IBAN
        self._append_address(self._bill.creditor)  # Cdtr
        self._append_address(None)  # UltmtCdtr
        # CcyAmt
        self._append_data_field("" if self._bill.amount is None else f"{self._bill.amount:.02f}")  # Amt
        self._append_data_field(self._bill.currency)  # Ccy
        # UltmtDbtr
        self._append_address(self._bill.debtor)  # UltmtDbtr
        # RmtInf
        self._append_data_field(self._bill.reference_type.value)  # Tp
        self._append_data_field(self._bill.reference)  # Ref
        # AddInf
        self._append_data_field(self._bill.unstructured_message)  # Unstrd
        self._append_data_field("EPD")  # Trailer

        has_alternative_schemes = self._bill.alternative_schemes is not None and len(self._bill.alternative_schemes) > 0
        if has_alternative_schemes or self._bill.bill_information is not None:
            self._append_data_field(self._bill.bill_information)  # StrdBkgInf

        # AltPmtInf
        if has_alternative_schemes:
            self._append_data_field(self._bill.alternative_schemes[0].instruction)  # AltPmt
            if len(self._bill.alternative_schemes) > 0:
                self._append_data_field(self._bill.alternative_schemes[0].instruction)  # AltPmt

        return "\n".join(self._text)

    def _append_address(self, address: Address):
        """Append an address (creditor or debtor).

        Args:
            address (Address): The address
        """
        if address is not None:
            self._append_data_field("S" if address.type == AddressType.STRUCTURED else "K")  # AdrTp
            self._append_data_field(address.name)  # Name
            self._append_data_field(address.street if address.type == AddressType.STRUCTURED else address.address_line1)  # StrtNmOrAdrLine1
            self._append_data_field(address.house_no if address.type == AddressType.STRUCTURED else address.address_line2)  # StrtNmOrAdrLine2
            self._append_data_field(address.postal_code)  # PstCd
            self._append_data_field(address.town)  # TwnNm
            self._append_data_field(address.country_code)  # Ctry
            return

        # Empty Address : 7 empty lines
        for _ in range(0, 7):
            self._append_data_field("")

    def _append_data_field(self, value: str):
        """Append a field (single line)

        Args:
            value (any): the input value
        """
        self._text.append(str(value) if value else "")

# -*- coding: utf-8 -*-
#
# Swiss QR Bill Generator
# Copyright (c) 2017 Manuel Bleichenbacher
# Licensed under MIT License
# https://opensource.org/licenses/MIT
#
# Code ported to python by Martin Mohnhaupt
#
#
from decimal import Decimal
from typing import List

from .address import Address
from .alternative_scheme import AlternativeScheme
from .bill_format import BillFormat
from .enums import ReferenceType
from .payments import Payments


class Bill:
    VERSION = '0200'

    def __init__(self) -> None:
        self._version = Bill.VERSION
        self._amount: Decimal = None
        self._currency = None
        self._account: str = None
        self._creditor: Address = None
        self._reference_type = ReferenceType.REFERENCE_TYPE_NO_REF
        self._reference: str = None
        self._debtor: Address = None
        self._unstructured_message: str = None
        self._bill_information = None
        self._alternative_schemes: List[AlternativeScheme] = []
        self._format = BillFormat()

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value: Decimal):
        self._amount = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value: str):
        self._currency = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value: str):
        if isinstance(value, str):
            self._account = ''.join(value.split()).upper()
        else:
            self._account = None

    @property
    def creditor(self):
        return self._creditor

    @creditor.setter
    def creditor(self, value: Address):
        self._creditor = value

    @property
    def reference_type(self) -> ReferenceType:
        return self._reference_type

    @reference_type.setter
    def reference_type(self, value: ReferenceType):
        self._reference_type = value

    @property
    def reference(self) -> str:
        return self._reference

    @reference.setter
    def reference(self, value: str):
        """Sets the payment reference.

            The reference is mandatory for QR IBANs, i.e. IBANs in the range
            CHxx30000xxxxxx through CHxx31999xxxxx. QR IBANs require a valid QR
            reference (numeric reference corresponding to the ISR reference format).

            For non-QR IBANs, the reference is optional. If it is provided,
            it must be valid creditor reference according to ISO 11649 ("RFxxxx").

            Both types of references may contain spaces for formatting.
        """
        self._reference = value
        self.update_reference_type()

    @property
    def debtor(self) -> Address:
        return self._debtor

    @debtor.setter
    def debtor(self, value: Address):
        self._debtor = value

    @property
    def unstructured_message(self) -> str:
        return self._unstructured_message

    @unstructured_message.setter
    def unstructured_message(self, value: str):
        if isinstance(value, str):
            value = value.strip()
            value = value if value else None
        self._unstructured_message = value

    @property
    def bill_information(self) -> str:
        return self._bill_information

    @bill_information.setter
    def bill_information(self, value: str):
        self._bill_information = value

    @property
    def alternative_schemes(self) -> List[AlternativeScheme]:
        return self._alternative_schemes

    @alternative_schemes.setter
    def alternative_schemes(self, value: List[AlternativeScheme]):
        self._alternative_schemes = value

    @property
    def format(self) -> BillFormat:
        return self._format

    @format.setter
    def format(self, value):
        self._format = value

    def update_reference_type(self):
        if self._reference is not None:
            ref = self._reference.strip()
            if ref.startswith('RF'):
                self._reference_type = ReferenceType.REFERENCE_TYPE_CRED_REF
            elif len(ref) > 0:
                self._reference_type = ReferenceType.REFERENCE_TYPE_QR_REF
            else:
                self._reference_type = ReferenceType.REFERENCE_TYPE_NO_REF
        else:
            self._reference_type = ReferenceType.REFERENCE_TYPE_NO_REF

    def create_and_set_creditor_reference(self, raw_reference: str) -> None:
        """
        Creates and sets a ISO11649 creditor reference from a raw string by prefixing
        the String with "RF" and the modulo 97 checksum.
        """
        self.reference = Payments.create_ISO11649_reference(raw_reference) if raw_reference else None

    def create_and_set_QR_reference(self, raw_reference: str):
        """
        Creates and sets a QR reference from a raw string by appending the checksum digit
        and prepending zeros to make it the correct length.
        """
        raw_reference = str(raw_reference)
        self.reference = Payments.create_QR_reference(raw_reference) if raw_reference else None

    def __str__(self) -> str:
        schemes = []
        for s in self._alternative_schemes:
            schemes.append(str(s))
        return f'''
        Bill
            version={self._version} amount={self._amount} currency={self._currency}
            account={self._account}
            creditor={self._creditor}
            reference={self._reference} reference_type={self._reference_type} 
            debtor={self._debtor}
            unstructured_message={self._unstructured_message}
            bill_information={self._bill_information}
            alternative_schemes=\n{''.join(schemes)}
            format={self._format}
        '''

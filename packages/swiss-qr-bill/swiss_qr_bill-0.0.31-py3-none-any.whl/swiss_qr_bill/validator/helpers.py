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
from email import message_from_string
from enum import Enum, auto
from pprint import pprint
from typing import List

from swiss_qr_bill.generator.bill import Bill


class ValidationConstants(Enum):
    EMPTY = ''
    # Validation messageKey: currency must be 'CHF' or 'EUR'
    KEY_CURRENCY_NOT_CHF_OR_EUR = 'currency_not_chf_or_eur'
    # Validation messageKey: amount must be between 0.01 and 999999999.99
    KEY_AMOUNT_OUTSIDE_VALID_RANGE = 'amount_outside_valid_range'
    # Validation messageKey: account number should start with 'CH' or 'LI'
    KEY_ACCOUNT_IBAN_NOT_FROM_CH_OR_LI = 'account_iban_not_from_ch_or_li'
    # Validation messageKey: IBAN is not valid (incorrect format or check digit)
    KEY_ACCOUNT_IBAN_INVALID = 'account_iban_invalid'
    # Validation messageKey: The reference is invalid. It is neither a valid QR reference nor a valid ISO 11649
    # reference.
    KEY_REF_INVALID = 'ref_invalid'
    # Validation messageKey: QR reference is missing it is mandatory for payments to a QR-IBAN account.
    KEY_QR_REF_MISSING = 'qr_ref_missing'
    # Validation messageKey: For payments to a QR-IBAN account, a QR reference is required. An ISO 11649 reference
    # may not be used.
    KEY_CRED_REF_INVALID_USE_FOR_QR_IBAN = 'cred_ref_invalid_use_for_qr_iban'
    # Validation messageKey: A QR reference is only allowed for payments to a QR-IBAN account.
    KEY_QR_REF_INVALID_USE_FOR_NON_QR_IBAN = 'qr_ref_invalid_use_for_non_qr_iban'
    # Validation messageKey: Reference type should be one of 'QRR', 'SCOR' and 'NON' and match the reference.
    KEY_REF_TYPE_INVALID = 'ref_type_invalid'
    # Validation messageKey: Field must not be empty
    KEY_FIELD_VALUE_MISSING = 'field_value_missing'
    # Validation messageKey: Conflicting fields for both structured and combined elements address type have been used
    KEY_ADDRESS_TYPE_CONFLICT = 'address_type_conflict'
    # Validation messageKey: Country code must consist of two letters
    KEY_COUNTRY_CODE_INVALID = 'country_code_invalid'
    # Validation messageKey: Field has been clipped to not exceed the maximum length
    KEY_FIELD_VALUE_CLIPPED = 'field_value_clipped'
    # Validation messageKey: Field value exceed the maximum length
    KEY_FIELD_VALUE_TOO_LONG = 'field_value_too_long'
    # Validation messageKey: Unstructured message and bill information combined exceed the maximum length
    KEY_ADDITIONAL_INFO_TOO_LONG = 'additional_info_too_long'
    # Validation messageKey: Unsupported characters have been replaced
    KEY_REPLACED_UNSUPPORTED_CHARACTERS = 'replaced_unsupported_characters'
    # Validation messageKey: Invalid data structure it must start with 'SPC' and consists
    # of 32 to 34 lines of text (with exceptions)
    KEY_DATA_STRUCTURE_INVALID = 'data_structure_invalid'
    # Validation messageKey: Version 02.00 is supported only
    KEY_VERSION_UNSUPPORTED = 'version_unsupported'
    # Validation messageKey: Coding type 1 is supported only
    KEY_CODING_TYPE_UNSUPPORTED = 'coding_type_unsupported'
    # Validation messageKey: Valid number required (nnnnn.nn)
    KEY_NUMBER_INVALID = 'number_invalid'
    # Validation messageKey: The maximum of 2 alternative schemes has been exceeded
    KEY_ALT_SCHEME_MAX_EXCEEDED = 'alt_scheme_max_exceed'
    # Validation messageKey: The bill information is invalid (does not start with // or is too short)
    KEY_BILL_INFO_INVALID = 'bill_info_invalid'
    # Relative field name of an address' name.
    SUBFIELD_NAME = '.name'
    # Relative field of an address' line 1.
    SUBFIELD_ADDRESS_LINE_1 = '.addressLine1'
    # Relative field of an address' line 2.
    SUBFIELD_ADDRESS_LINE_2 = '.addressLine2'
    # Relative field of an address' street.
    SUBFIELD_STREET = '.street'
    # Relative field of an address' house number.
    SUBFIELD_HOUSE_NO = '.houseNo'
    # Relative field of an address' postal code.
    SUBFIELD_POSTAL_CODE = '.postalCode'
    # Relative field of an address' town.
    SUBFIELD_TOWN = '.town'
    # Relative field of an address' country code.
    SUBFIELD_COUNTRY_CODE = '.countryCode'
    # Field name of the QR code type.
    FIELD_QR_TYPE = 'qrText'
    # Field name of the QR bill version.
    FIELD_VERSION = 'version'
    # Field name of the QR bill's coding type.
    FIELD_CODING_TYPE = 'codingType'
    # Field name of the QR bill's trailer ('EPD').
    FIELD_TRAILER = 'trailer'
    # Field name of the currency.
    FIELD_CURRENCY = 'currency'
    # Field name of the amount.
    FIELD_AMOUNT = 'amount'
    # Field name of the account number.
    FIELD_ACCOUNT = 'account'
    # Field name of the reference type.
    FIELD_REFERENCE_TYPE = 'referenceType'
    # Field name of the reference.
    FIELD_REFERENCE = 'reference'
    # Start of field name of the creditor address.
    FIELD_ROOT_CREDITOR = 'creditor'
    # Field name of the creditor's name.
    FIELD_CREDITOR_NAME = 'creditor.name'
    # Field name of the creditor's street.
    FIELD_CREDITOR_STREET = 'creditor.street'
    # Field name of the creditor's house number.
    FIELD_CREDITOR_HOUSE_NO = 'creditor.houseNo'
    # Field name of the creditor's postal code.
    FIELD_CREDITOR_POSTAL_CODE = 'creditor.postalCode'
    # Field name of the creditor's town.
    FIELD_CREDITOR_TOWN = 'creditor.town'
    # Field name of the creditor's country code.
    FIELD_CREDITOR_COUNTRY_CODE = 'creditor.countryCode'
    # Field name of the unstructured message.
    FIELD_UNSTRUCTURED_MESSAGE = 'unstructuredMessage'
    # Field name of the bill information.
    FIELD_BILL_INFORMATION = 'billInformation'
    # Field name of the alternative schemes.
    FIELD_ALTERNATIVE_SCHEMES = 'altSchemes'
    # Start of field name of the debtor's address.
    FIELD_ROOT_DEBTOR = 'debtor'
    # Field name of the debtor's name.
    FIELD_DEBTOR_NAME = 'debtor.name'
    # Field name of the debtor's street.
    FIELD_DEBTOR_STREET = 'debtor.street'
    # Field name of the debtor's house number.
    FIELD_DEBTOR_HOUSE_NO = 'debtor.houseNo'
    # Field name of the debtor's postal code.
    FIELD_DEBTOR_POSTAL_CODE = 'debtor.postalCode'
    # Field name of the debtor's town.
    FIELD_DEBTOR_TOWN = 'debtor.town'
    # Field name of the debtor's country code.
    FIELD_DEBTOR_COUNTRY_CODE = 'debtor.countryCode'

    def __add__(self, other) -> str:
        result = self.value + other.value
        return self.value + other.value


ERROR_MESSAGES = {
    ValidationConstants.KEY_CURRENCY_NOT_CHF_OR_EUR.value: 'Currency should be "CHF" or "EUR"',
    ValidationConstants.KEY_AMOUNT_OUTSIDE_VALID_RANGE.value: 'Amount should be between 0.01 and 999 999 999.99',
    ValidationConstants.KEY_ACCOUNT_IBAN_NOT_FROM_CH_OR_LI.value: 'Account number should start with "CH" or "LI"',
    ValidationConstants.KEY_ACCOUNT_IBAN_INVALID.value: 'Account number is not a valid IBAN (invalid format or checksum)',
    ValidationConstants.KEY_REF_INVALID.value: 'Reference is invalid; it is neither a valid QR reference nor a valid ISO 11649 reference',
    ValidationConstants.KEY_QR_REF_MISSING.value: 'QR reference is missing; it is mandatory for payments to a QR-IBAN account',
    ValidationConstants.KEY_CRED_REF_INVALID_USE_FOR_QR_IBAN.value: 'For payments to a QR-IBAN account, a QR reference is required (an ISO 11649 reference may not be used)',
    ValidationConstants.KEY_QR_REF_INVALID_USE_FOR_NON_QR_IBAN.value: 'A QR reference is only allowed for payments to a QR-IBAN account',
    ValidationConstants.KEY_REF_TYPE_INVALID.value: 'Reference type should be one of "QRR", "SCOR" and "NON" and match the reference',
    ValidationConstants.KEY_FIELD_VALUE_MISSING.value: 'Field "{}" may not be empty',
    ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT.value: 'Fields for either structured address or combined elements address may be filled but not both',
    ValidationConstants.KEY_COUNTRY_CODE_INVALID.value: 'Country code is invalid: it should consist of two letters',
    ValidationConstants.KEY_FIELD_VALUE_CLIPPED.value: 'The value for field "{}" has been clipped to not exceed the maximum length of {} characters',
    ValidationConstants.KEY_FIELD_VALUE_TOO_LONG.value: 'The value for field "{}" should not exceed a length of {} characters',
    ValidationConstants.KEY_ADDITIONAL_INFO_TOO_LONG.value: 'The additional information and the structured bill information combined should not exceed 140 characters',
    ValidationConstants.KEY_REPLACED_UNSUPPORTED_CHARACTERS.value: 'Unsupported characters have been replaced in field "{}"',
    ValidationConstants.KEY_ALT_SCHEME_MAX_EXCEEDED.value: 'No more than two alternative schemes may be used',
    ValidationConstants.KEY_BILL_INFO_INVALID.value: 'Structured bill information must start with "//"',
}


class MessageType(Enum):
    WARNING = auto()
    ERROR = auto()


class Message:

    def __init__(self, message_type: MessageType, field: ValidationConstants, sub_field: ValidationConstants, key: ValidationConstants, parameters: List[str] = None) -> None:
        """Initializes a new instance with the given values.

        For valid field names and message keys, see the constants in the ValidationConstants class.

        Parameters:
            * type: The message type.
            * field: The name of the affected field.
            * sub_field: The name of the affected sub-field.
            * key: The language - neutral message key
            * parameters: The optional variable text parts to be inserted into localized message.
        """
        self.type = message_type
        self.field = field
        self.sub_field = sub_field
        self.key = key
        self.parameters = parameters

    def __str__(self) -> str:
        return f'Message: type={self.type}, field={self.field}, sub_field={self.sub_field}, key={self.key}, parameters={self.parameters}'


class ValidationResult:
    def __init__(self) -> None:
        self._messages: List[Message] = []
        self._cleaned_bill = None

    @property
    def cleaned_bill(self):
        return self._cleaned_bill

    @cleaned_bill.setter
    def cleaned_bill(self, bill: Bill):
        self._cleaned_bill = bill if isinstance(bill, Bill) else None

    @property
    def has_messages(self):
        return len(self._messages) > 0

    @property
    def has_warnings(self):
        if self.has_messages is False:
            return False
        for message in self._messages:
            if message.type == MessageType.WARNING:
                return True
        return False

    @property
    def has_errors(self):
        if self.has_messages is False:
            return False
        for message in self._messages:
            if message.type == MessageType.ERROR:
                return True
        return False

    @property
    def is_valid(self):
        return self.has_errors == False

    def add_message(self, type: MessageType, field: ValidationConstants, sub_field: ValidationConstants, key: ValidationConstants, parameters: List[str] = None):
        self._messages.append(Message(type, field, sub_field, key, parameters))

    def get_description(self) -> str:
        if self.has_errors is False:
            return 'Valid bill data'
        desc_list = []
        for message in self._messages:
            if message.type != MessageType.ERROR:
                continue
            field_name = message.field.value + message.sub_field.value if message.sub_field else ''
            desc = ERROR_MESSAGES.get(message.key.value, 'Unknown error')
            if message.key in [ValidationConstants.KEY_FIELD_VALUE_MISSING, ValidationConstants.KEY_REPLACED_UNSUPPORTED_CHARACTERS]:
                desc = desc.format(field_name)
            elif message.key in [ValidationConstants.KEY_FIELD_VALUE_TOO_LONG, ValidationConstants.KEY_FIELD_VALUE_CLIPPED]:
                desc = desc.format(field_name, message.parameters[0])
            desc_list.append(f'{desc} ({message.key.value})')
        return '\n'.join(desc_list)

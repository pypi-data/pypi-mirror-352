# -*- coding: utf-8 -*-
from typing import List
from swiss_qr_bill.generator.address import Address
from swiss_qr_bill.generator.alternative_scheme import AlternativeScheme
from swiss_qr_bill.generator.bill import Bill
from swiss_qr_bill.generator.bill_format import BillFormat
from swiss_qr_bill.generator.payments import Payments
from swiss_qr_bill.generator.enums import AddressType, ReferenceType
from swiss_qr_bill.validator.helpers import MessageType, ValidationResult, ValidationConstants


class Validator:
    """Internal class for validating and cleaning QR bill data."""

    def __init__(self, bill: Bill) -> None:
        self._bill_in: Bill = bill
        self._bill_out: Bill = Bill()
        self._bill_out.format = BillFormat(self._bill_in.format) if self._bill_in.format is None else self._bill_in.format
        self._bill_out.version = self._bill_in.version
        self._validation_result = ValidationResult()

    @staticmethod
    def validate(bill: Bill) -> ValidationResult:
        validator = Validator(bill)
        return validator._validate_bill()

    def _validate_bill(self) -> ValidationResult:
        self._validate_account_number()
        self._validate_creditor()
        self._validate_currency()
        self._validate_amount()
        self._validate_debtor()
        self._validate_reference()
        self._validate_additional_information()
        self._validate_alternative_achemes()
        self._validation_result.cleaned_bill = self._bill_out
        return self._validation_result

    def _validate_account_number(self):
        account = self._bill_in.account
        if not self._validate_mandatory(account, ValidationConstants.FIELD_ACCOUNT):
            return

        account = "".join(account.split()).upper()
        if not self._validate_iban(account):
            return

        if account[:2] not in ["CH", "LI"]:
            self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_ACCOUNT, None, ValidationConstants.KEY_ACCOUNT_IBAN_NOT_FROM_CH_OR_LI)
        elif len(account) != 21:
            self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_ACCOUNT, None, ValidationConstants.KEY_ACCOUNT_IBAN_INVALID)
        else:
            self._bill_out.account = account

    def _validate_creditor(self):
        self._bill_out.creditor = self._validate_address(self._bill_in.creditor, ValidationConstants.FIELD_ROOT_CREDITOR, True)

    def _validate_currency(self):
        currency = self._bill_in.currency
        if not self._validate_mandatory(currency, ValidationConstants.FIELD_CURRENCY):
            return

        currency = "".join(currency.split()).upper()
        if currency not in ["CHF", "EUR"]:
            self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_CURRENCY, None, ValidationConstants.KEY_CURRENCY_NOT_CHF_OR_EUR)
        else:
            self._bill_out.currency = currency

    def _validate_amount(self):
        amount = self._bill_in.amount
        if amount is None:
            self._bill_out.amount = None
        else:
            amt = round(amount, 2)  # round to multiple of 0.01
            if amt <= 0.01 or amt > 999999999.99:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_AMOUNT, None, ValidationConstants.KEY_AMOUNT_OUTSIDE_VALID_RANGE)
            else:
                self._bill_out.amount = amt

    def _validate_debtor(self):
        self._bill_out.debtor = self._validate_address(self._bill_in.debtor, ValidationConstants.FIELD_ROOT_DEBTOR, False)

    def _validate_reference(self):
        account = self._bill_in.account
        is_valid_account = account is not None
        is_qr_bill_iban = account is not None and Payments.is_qr_iban(account)

        reference = self._bill_in.reference
        has_reference_error = False
        if reference is not None:
            reference = "".join(reference.split()).upper()
            reference.isnumeric()
            if reference.isnumeric():
                self._validate_qr_reference(reference)
            else:
                self._validate_iso_reference(reference)
            has_reference_error = self._bill_out.reference is None

        if is_qr_bill_iban:
            if self._bill_out.reference_type == ReferenceType.REFERENCE_TYPE_NO_REF and not has_reference_error:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE, None, ValidationConstants.KEY_QR_REF_MISSING)
            elif self._bill_out.reference_type == ReferenceType.REFERENCE_TYPE_CRED_REF:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE, None, ValidationConstants.KEY_CRED_REF_INVALID_USE_FOR_QR_IBAN)
        elif is_valid_account:
            if self._bill_out.reference_type == ReferenceType.REFERENCE_TYPE_QR_REF:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE, None, ValidationConstants.KEY_QR_REF_INVALID_USE_FOR_NON_QR_IBAN)

    def _validate_additional_information(self):
        bill_information = self._bill_in.bill_information
        unstructured_message = self._bill_in.unstructured_message

        if bill_information and (not bill_information.startswith("//") or len(bill_information) < 4):
            self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_BILL_INFORMATION, None, ValidationConstants.KEY_BILL_INFO_INVALID)
            bill_information = None

        if not bill_information and not unstructured_message:
            return

        if bill_information is None:
            unstructured_message = self.cleaned_value(unstructured_message, ValidationConstants.FIELD_UNSTRUCTURED_MESSAGE)
            unstructured_message = self.clipped_value(unstructured_message, 140, ValidationConstants.FIELD_UNSTRUCTURED_MESSAGE)
            self._bill_out.unstructured_message = unstructured_message
        elif unstructured_message is None:
            bill_information = self.cleaned_value(bill_information, ValidationConstants.FIELD_BILL_INFORMATION)
            if self.validate_length(bill_information, 140, ValidationConstants.FIELD_BILL_INFORMATION):
                self._bill_out.bill_information = bill_information
        else:
            bill_information = self.cleaned_value(bill_information, ValidationConstants.FIELD_BILL_INFORMATION)
            unstructured_message = self.cleaned_value(unstructured_message, ValidationConstants.FIELD_UNSTRUCTURED_MESSAGE)
            combined_length = len(bill_information) + len(unstructured_message)
            if combined_length > 140:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_UNSTRUCTURED_MESSAGE, None, ValidationConstants.KEY_ADDITIONAL_INFO_TOO_LONG)
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_BILL_INFORMATION, None, ValidationConstants.KEY_ADDITIONAL_INFO_TOO_LONG)
            else:
                self._bill_out.unstructured_message = unstructured_message
                self._bill_out.bill_information = bill_information

    def _validate_alternative_achemes(self):
        schemes_out: List[AlternativeScheme] = None
        if self._bill_in.alternative_schemes:
            scheme_list = self.create_clean_scheme_list()
            if len(scheme_list):
                schemes_out = scheme_list
                if len(schemes_out) > 2:
                    self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_ALTERNATIVE_SCHEMES, None, ValidationConstants.KEY_ALT_SCHEME_MAX_EXCEEDED)
                    schemes_out = schemes_out[:2]
        self._bill_out.alternative_schemes = schemes_out

    #########################################################

    def _validate_mandatory(self, value: str, field: ValidationConstants, sub_field=ValidationConstants.EMPTY) -> bool:
        if not value:
            self._validation_result.add_message(MessageType.ERROR, field, sub_field, ValidationConstants.KEY_FIELD_VALUE_MISSING)
            return False
        return True

    def _validate_iban(self, value: str) -> bool:
        if Payments.is_valid_iban(value):
            return True
        self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_ACCOUNT, None, ValidationConstants.KEY_ACCOUNT_IBAN_INVALID)
        return False

    def _validate_address(self, address: Address, field_root: str, mandatory: bool) -> Address:
        address_out = self._cleaned_address(address, field_root)
        if address_out is None:
            self.validate_empty_address(field_root, mandatory)
            return None

        if address_out.type == AddressType.CONFLICTING:
            self.emit_errors_for_conflicting_type(address, field_root)

        self.check_mandatory_address_fields(address, field_root)

        if address_out.country_code is not None:
            if len(address_out.country_code) != 2 or not address_out.country_code.isalpha():
                self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_COUNTRY_CODE, ValidationConstants.KEY_COUNTRY_CODE_INVALID)

        self.clean_address_fields(address_out, field_root)

        return address_out

    def _cleaned_address(self, address: Address, field_root: str) -> Address:
        if address is None:
            return None
        address_out = Address()
        address_out.name = self.cleaned_value(address.name, field_root, ValidationConstants.SUBFIELD_NAME)
        value = self.cleaned_value(address.address_line1, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_1)
        if value:
            address_out.address_line1 = value
        value = self.cleaned_value(address.address_line2, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_2)
        if value:
            address_out.address_line2 = value
        value = self.cleaned_value(address.street, field_root, ValidationConstants.SUBFIELD_STREET)
        if value:
            address_out.street = value
        value = self.cleaned_value(address.house_no, field_root, ValidationConstants.SUBFIELD_HOUSE_NO)
        if value:
            address_out.house_no = value
        value = self.cleaned_value(address.postal_code, field_root, ValidationConstants.SUBFIELD_POSTAL_CODE)
        if value:
            address_out.postal_code = value
        value = self.cleaned_value(address.town, field_root, ValidationConstants.SUBFIELD_TOWN)
        if value:
            address_out.town = value

        address_out.country_code = address.country_code.strip() if address.country_code else address.country_code

        if address_out.name is None and address_out.country_code is None and address_out.type == AddressType.UNDETERMINED:
            return None

        return address_out

    def _validate_qr_reference(self, reference: str):
        if len(reference) < 27:
            reference = "00000000000000000000000000"[0 : 27 - len(reference)] + reference
        if not Payments.is_valid_qr_reference(reference):
            self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE, None, ValidationConstants.KEY_REF_INVALID)
        else:
            self._bill_out.reference = reference
            if self._bill_in.reference_type != ReferenceType.REFERENCE_TYPE_QR_REF:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE_TYPE, None, ValidationConstants.KEY_REF_TYPE_INVALID)

    def _validate_iso_reference(self, reference: str):
        if not Payments.is_valid_iso_reference(reference):
            self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE, None, ValidationConstants.KEY_REF_INVALID)
        else:
            self._bill_out.reference = reference
            if self._bill_in.reference_type != ReferenceType.REFERENCE_TYPE_CRED_REF:
                self._validation_result.add_message(MessageType.ERROR, ValidationConstants.FIELD_REFERENCE_TYPE, None, ValidationConstants.KEY_REF_TYPE_INVALID)

    def cleaned_value(self, value: str, *args) -> str:
        result = Payments.CleaningResult()
        Payments.clean_value(value, result)
        if result.replaced_unsupported_chars:
            field = None
            sub_field = None
            if len(args) == 1:
                field = args[0]
            elif len(args) == 2:
                field = args[0]
                sub_field = args[1]
            self._validation_result.add_message(MessageType.WARNING, field, sub_field, ValidationConstants.KEY_REPLACED_UNSUPPORTED_CHARACTERS)
        return result.cleaned_string

    def clipped_value(self, value: str, max_length: int, *args) -> str:
        if value is not None and len(value) > max_length:
            field = None
            sub_field = None
            if len(args) == 1:
                field = args[0]
            elif len(args) == 2:
                field = args[0]
                sub_field = args[1]
            self._validation_result.add_message(MessageType.WARNING, field, sub_field, ValidationConstants.KEY_FIELD_VALUE_CLIPPED, str(max_length))
            return value[:max_length]
        return value

    def clean_address_fields(self, address: Address, field_root: str):
        address.name = self.clipped_value(address.name, 70, field_root, ValidationConstants.SUBFIELD_NAME)

        if address.type == AddressType.STRUCTURED:
            address.street = self.clipped_value(address.street, 70, field_root, ValidationConstants.SUBFIELD_STREET)
            address.house_no = self.clipped_value(address.house_no, 16, field_root, ValidationConstants.SUBFIELD_HOUSE_NO)
            address.postal_code = self.clipped_value(address.postal_code, 16, field_root, ValidationConstants.SUBFIELD_POSTAL_CODE)
            address.town = self.clipped_value(address.town, 35, field_root, ValidationConstants.SUBFIELD_TOWN)
        elif address.type == AddressType.COMBINED_ELEMENTS:
            address.address_line1 = self.clipped_value(address.address_line1, 70, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_1)
            address.address_line2 = self.clipped_value(address.address_line2, 70, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_2)

        if address.country_code:
            address.country_code = address.country_code.upper()

    def validate_empty_address(self, field_root: str, mandatory: bool):
        if not mandatory:
            return
        self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_NAME, ValidationConstants.KEY_FIELD_VALUE_MISSING)
        self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_POSTAL_CODE, ValidationConstants.KEY_FIELD_VALUE_MISSING)
        self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_2, ValidationConstants.KEY_FIELD_VALUE_MISSING)
        self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_TOWN, ValidationConstants.KEY_FIELD_VALUE_MISSING)
        self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_COUNTRY_CODE, ValidationConstants.KEY_FIELD_VALUE_MISSING)

    def emit_errors_for_conflicting_type(self, address: Address, field_root: str):
        if address.address_line1:
            self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_1, ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT)
        if address.address_line2:
            self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_2, ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT)
        if address.street:
            self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_STREET, ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT)
        if address.house_no:
            self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_HOUSE_NO, ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT)
        if address.postal_code:
            self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_POSTAL_CODE, ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT)
        if address.town:
            self._validation_result.add_message(MessageType.ERROR, field_root, ValidationConstants.SUBFIELD_TOWN, ValidationConstants.KEY_ADDRESS_TYPE_CONFLICT)

    def check_mandatory_address_fields(self, address: Address, field_root: str):
        self._validate_mandatory(address.name, field_root, ValidationConstants.SUBFIELD_NAME)
        if address.type == AddressType.STRUCTURED or address.type == AddressType.UNDETERMINED:
            self._validate_mandatory(address.postal_code, field_root, ValidationConstants.SUBFIELD_POSTAL_CODE)
            self._validate_mandatory(address.town, field_root, ValidationConstants.SUBFIELD_TOWN)
        if address.type == AddressType.COMBINED_ELEMENTS or address.type == AddressType.UNDETERMINED:
            self._validate_mandatory(address.address_line2, field_root, ValidationConstants.SUBFIELD_ADDRESS_LINE_2)
            self._validate_mandatory(address.country_code, field_root, ValidationConstants.SUBFIELD_COUNTRY_CODE)

    def validate_length(self, value: str, max_length: str, field: ValidationConstants) -> bool:
        if value and len(value) > max_length:
            self._validation_result.add_message(MessageType.ERROR, field, None, ValidationConstants.KEY_FIELD_VALUE_TOO_LONG, str(max_length))
            return False
        return True

    def create_clean_scheme_list(self) -> List[AlternativeScheme]:
        scheme_list: List[AlternativeScheme] = []
        for schema in self._bill_in.alternative_schemes:
            scheme_out = AlternativeScheme(schema.name, schema.instruction)
            if scheme_out.name and scheme_out.instruction and self.validate_length(scheme_out.instruction, 100, ValidationConstants.FIELD_ALTERNATIVE_SCHEMES):
                scheme_list.append(scheme_out)
        return scheme_list

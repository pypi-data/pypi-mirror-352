from stdnum import iso11649, iban


class Payments:
    class CleaningResult:
        def __init__(self) -> None:
            # Cleaned string
            self.cleaned_string: str = None
            # Flag indicating that unsupported characters have been replaced
            self.replaced_unsupported_chars = False

    @staticmethod
    def clean_value(value: str, result: CleaningResult):
        result.cleaned_string = None
        result.replaced_unsupported_chars = False
        Payments._clean_value(value, result)

    @staticmethod
    def _clean_value(value: str, result: CleaningResult):
        if not isinstance(value, str) or not len(value):
            return

        value_as_list = list(value)
        for i, c in enumerate(value):
            if Payments._is_valid_QR_bill_character(c) is False:
                value_as_list[i] = ''
                result.replaced_unsupported_chars = True
        if result.replaced_unsupported_chars is True:
            value = ''.join(value_as_list).strip()

        result.cleaned_string = value

    @staticmethod
    def create_QR_reference(value: str) -> str:
        ref = iso11649.compact(value)
        if not ref.isnumeric():
            raise TypeError(f'The reference must be numeric ({value})')
        if len(ref) > 26:
            raise ValueError(f'The reference must be 26 characters or less ({value})')
        return "0" * (26 - len(ref)) + ref + str(Payments._modulo10_checksum(ref))

    @staticmethod
    def create_ISO11649_reference(value: str) -> str:
        ref = iso11649.compact(value)
        checksum = iso11649.mod_97_10.calc_check_digits(ref + 'RF')
        return f'RF{checksum}{ref}'

    @staticmethod
    def is_valid_iban(value: str) -> bool:
        if not isinstance(value, str):
            return False
        try:
            iban.validate(value)
            return True
        except:
            return False

    @staticmethod
    def is_qr_iban(value: str) -> bool:
        if not isinstance(value, str):
            return False
        value = iban.compact(value)
        return Payments.is_valid_iban(value) and value[4] == '3' and value[5] in ['0', '1']

    @staticmethod
    def is_valid_qr_reference(value: str) -> bool:
        if not isinstance(value, str):
            return False
        if not value.isnumeric():
            return False
        if len(value) < 27:
            return False
        return Payments._modulo10_checksum(value) == 0

    @staticmethod
    def is_valid_iso_reference(value: str) -> bool:
        if not isinstance(value, str):
            return False
        if len(value) < 5 or len(value) > 25:
            return False
        if not value.isalnum():
            return False
        if not value.startswith('RF'):
            return False
        return iso11649.is_valid(value)

    @staticmethod
    def _modulo10_checksum(value: str) -> int:
        """"
        Calculate the check digits modulo 10, recursively

        See : https:#gist.github.com/christianmeichtry/9348451
        """
        lut = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
        digits = list(map(int, str(value)))
        report = 0  # Start at row 0
        for digit in digits:
            report = lut[(report + digit) % 10]
        return (10 - report) % 10

    @staticmethod
    def _is_valid_QR_bill_character(ch) -> bool:
        ch = ord(ch)
        if ch < 0x20:
            return False
        if ch == 0x5e:
            return False
        if ch <= 0x7e:
            return True
        if ch == 0xa3 or ch == 0xb4:
            return True
        if ch < 0xc0 or ch > 0xfd:
            return False
        if ch == 0xc3 or ch == 0xc5 or ch == 0xc6:
            return False
        if ch == 0xd0 or ch == 0xd5 or ch == 0xd7 or ch == 0xd8:
            return False
        if ch == 0xdd or ch == 0xde:
            return False
        if ch == 0xe3 or ch == 0xe5 or ch == 0xe6:
            return False
        return ch != 0xf0 and ch != 0xf5 and ch != 0xf8

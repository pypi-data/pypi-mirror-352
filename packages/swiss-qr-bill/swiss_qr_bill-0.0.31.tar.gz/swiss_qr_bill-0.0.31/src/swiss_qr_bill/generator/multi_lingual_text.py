from enum import Enum
from re import L
from .enums import Language


class MultiLingualText:

    class _EN(Enum):
        payment_part = 'Payment part'
        account_payable_to = 'Account / Payable to'
        reference = 'Reference'
        additional_info = 'Additional information'
        currency = 'Currency'
        amount = 'Amount'
        receipt = 'Receipt'
        acceptance_point = 'Acceptance point'
        payable_by = 'Payable by'
        payable_by_name_addr = 'Payable by (name/address)'
        do_not_use_for_payment = 'DO NOT USE FOR PAYMENT'

    class _FR(Enum):
        payment_part = 'Section paiement'
        account_payable_to = 'Compte / Payable à'
        reference = 'Référence'
        additional_info = 'Informations supplémentaires'
        currency = 'Monnaie'
        amount = 'Montant'
        receipt = 'Récépissé'
        acceptance_point = 'Point de dépôt'
        payable_by = 'Payable par'
        payable_by_name_addr = 'Payable par (nom/adresse)'
        do_not_use_for_payment = 'NE PAS UTILISER POUR LE PAIEMENT'

    class _DE(Enum):
        payment_part = 'Zahlteil'
        account_payable_to = 'Konto / Zahlbar an'
        reference = 'Referenz'
        additional_info = 'Zusätzliche Informationen'
        currency = 'Währung'
        amount = 'Betrag'
        receipt = 'Empfangsschein'
        acceptance_point = 'Annahmestelle'
        payable_by = 'Zahlbar durch'
        payable_by_name_addr = 'Zahlbar durch (Name/Adresse)'
        do_not_use_for_payment = 'NICHT ZUR ZAHLUNG VERWENDEN'

    class _IT(Enum):
        payment_part = 'Sezione pagamento'
        account_payable_to = 'Conto / Pagabile a'
        reference = 'Riferimento'
        additional_info = 'Informazioni supplementari'
        currency = 'Valuta'
        amount = 'Importo'
        receipt = 'Ricevuta'
        acceptance_point = 'Punto di accettazione'
        payable_by = 'Pagabile da'
        payable_by_name_addr = 'Pagabile da (nome/indirizzo)'
        do_not_use_for_payment = 'NON UTILIZZARE PER IL PAGAMENTO'

    class _RM(Enum):
        payment_part = 'Part da pajamaint'
        account_payable_to = 'Conto / Da pajar a'
        reference = 'Referenza'
        additional_info = 'Infuormaziuns supplementaras'
        currency = 'Valuta'
        amount = 'Import'
        receipt = 'Quittanza'
        acceptance_point = 'Post da recepziun'
        payable_by = 'Da pajar da'
        payable_by_name_addr = 'Da pajar da (nom/adressa)'
        do_not_use_for_payment = 'NA APPLITGAR PEL PAJAMAINT'

    class Keys:
        KEY_PAYMENT_PART = 'payment_part'
        KEY_ACCOUNT_PAYABLE_TO = 'account_payable_to'
        KEY_REFERENCE = 'reference'
        KEY_ADDITIONAL_INFO = 'additional_info'
        KEY_CURRENCY = 'currency'
        KEY_AMOUNT = 'amount'
        KEY_RECEIPT = 'receipt'
        KEY_ACCEPTANCE_POINT = 'acceptance_point'
        KEY_PAYABLE_BY = 'payable_by'
        KEY_PAYABLE_BY_NAME_ADDR = 'payable_by_name_addr'
        KEY_DO_NOT_USE_FOR_PAYMENT = 'do_not_use_for_payment'

    _LANG_DICT = {
        Language.DE: _DE,
        Language.FR: _FR,
        Language.EN: _EN,
        Language.IT: _IT,
        Language.RM: _RM
    }
    _DCT = _LANG_DICT.get(Language.EN)

    @staticmethod
    def set_language(language: Language):
        MultiLingualText._DCT = MultiLingualText._LANG_DICT.get(language)

    @staticmethod
    def get_text(key: Keys) -> str:
        return {i.name: i.value for i in MultiLingualText._DCT}.get(key, '???')

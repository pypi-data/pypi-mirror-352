# -*- coding: utf-8 -*-
from .enums import AddressType


class Address:
    def __init__(self) -> None:
        self._type = AddressType.UNDETERMINED
        self._name = None
        self._address_line1 = None
        self._address_line2 = None
        self._street = None
        self._house_no = None
        self._postal_code = None
        self._town = None
        self._country_code = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    @property
    def type(self) -> AddressType:
        return self._type

    @type.setter
    def type(self, value: AddressType):
        if not value:
            return
        self._type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value:
            return
        self._name = value

    @property
    def address_line1(self) -> str:
        return self._address_line1

    @address_line1.setter
    def address_line1(self, value: str):
        if not value:
            return
        self._address_line1 = value
        self._change_type(AddressType.COMBINED_ELEMENTS)

    @property
    def address_line2(self) -> str:
        return self._address_line2

    @address_line2.setter
    def address_line2(self, value: str):
        if not value:
            return
        self._address_line2 = value
        self._change_type(AddressType.COMBINED_ELEMENTS)

    @property
    def street(self) -> str:
        return self._street

    @street.setter
    def street(self, value: str):
        if not value:
            return
        self._street = value
        self._change_type(AddressType.STRUCTURED)

    @property
    def house_no(self) -> str:
        return self._house_no

    @house_no.setter
    def house_no(self, value: str):
        if not value:
            return
        self._house_no = str(value)
        self._change_type(AddressType.STRUCTURED)

    @property
    def postal_code(self) -> str:
        return self._postal_code

    @postal_code.setter
    def postal_code(self, value: str):
        if not value:
            return
        self._postal_code = str(value)
        self._change_type(AddressType.STRUCTURED)

    @property
    def town(self) -> str:
        return self._town

    @town.setter
    def town(self, value: str):
        if not value:
            return
        self._town = value
        self._change_type(AddressType.STRUCTURED)

    @property
    def country_code(self) -> str:
        return self._country_code

    @country_code.setter
    def country_code(self, value: str):
        if not value:
            return
        self._country_code = value

    def clear(self):
        self._type = AddressType.UNDETERMINED
        self._name = None
        self._address_line1 = None
        self._address_line2 = None
        self._street = None
        self._house_no = None
        self._postal_code = None
        self._town = None
        self._country_code = None

    def _change_type(self, value: AddressType):
        if value == self._type:
            return
        if self._type == AddressType.UNDETERMINED:
            self._type = value
        else:
            self._type = AddressType.CONFLICTING

    def create_reduced_address(self):
        # Address without street / house number
        reduced_address = Address()
        reduced_address.name = self.name
        reduced_address.country_code = self.country_code
        if self.type == AddressType.STRUCTURED:
            reduced_address.postal_code = self.postal_code
            reduced_address.town = self.town
        elif self.type == AddressType.COMBINED_ELEMENTS:
            reduced_address.address_line2 = self.address_line2
        return reduced_address

    def __str__(self) -> str:
        return f"""
        Address
            type={self._type}
            name={self._name}
            address_line1={self._address_line1}
            address_line2={self._address_line2}
            street={self._street} house_no={self._house_no} postal_code={self._postal_code} town={self._town} 
            country_code={self._country_code}
        """

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class CreationSource(Enum): 
    MANUAL = "manual"
    API = "api"
    CRM = "crm"
    OTHER = "other"

class TaxExemptStatus(Enum):
    NONE = "none"
    EXEMPT = "exempt"
    REVERSE = "reverse"

    @classmethod
    def _missing_(cls, value):
        """Handle unknown values by returning NONE"""
        return cls.NONE

@dataclass
class Address:
    line1: str
    city: str
    state: str
    zipCode: str
    country: str
    line2: Optional[str] = None

    def to_dict(self) -> dict:
        data = {
            'line1': self.line1,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zipCode,
            'country': self.country
        }
        if self.line2 is not None:
            data['line2'] = self.line2
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Address':
        if 'postalCode' in data:
            data['zipCode'] = data.pop('postalCode')
        return cls(**data)

@dataclass
class Account:
    id: str
    organizationId: str
    name: str
    phone: Optional[str] = None
    employeeCount: Optional[int] = None
    annualRevenue: Optional[float] = None
    taxExemptStatus: Optional[TaxExemptStatus] = None
    creationSource: Optional[CreationSource] = None
    website: Optional[str] = None
    externalId: Optional[str] = None
    billingAddress: Optional[Address] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        filtered_data = {k: v for k, v in data.items() if k in cls.__annotations__ and k not in ['createdAt', 'updatedAt']}
        
        if 'taxExemptStatus' in filtered_data and filtered_data['taxExemptStatus']:
            try:
                filtered_data['taxExemptStatus'] = TaxExemptStatus(filtered_data['taxExemptStatus'])
            except ValueError:
                filtered_data['taxExemptStatus'] = TaxExemptStatus.NONE
        if 'creationSource' in filtered_data and filtered_data['creationSource']:
            filtered_data['creationSource'] = CreationSource(filtered_data['creationSource'])
        
        if 'billingAddress' in filtered_data and filtered_data['billingAddress']:
            address_data = filtered_data['billingAddress']
            if 'street' in address_data:
                address_data['line1'] = address_data.pop('street')
            
            # Only create Address object if all required fields are present
            required_fields = {'line1', 'city', 'state', 'zipCode', 'country'}
            if all(field in address_data for field in required_fields):
                filtered_data['billingAddress'] = Address.from_dict(address_data)
            else:
                filtered_data['billingAddress'] = None
            
        return cls(**filtered_data)

    def to_dict(self) -> dict:
        data = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, datetime):
                    data[field_name] = field_value.isoformat()
                elif isinstance(field_value, Address):
                    data[field_name] = field_value.to_dict()
                elif isinstance(field_value, (TaxExemptStatus, CreationSource)):
                    data[field_name] = field_value.value
                else:
                    data[field_name] = field_value
        return data

@dataclass
class CreateAccountRequest:
    name: str
    phone: Optional[str] = None
    employeeCount: Optional[int] = None
    annualRevenue: Optional[float] = None
    taxExemptStatus: Optional[TaxExemptStatus] = None
    creationSource: Optional[CreationSource] = None
    website: Optional[str] = None
    externalId: Optional[str] = None
    billingAddress: Optional[Address] = None

    def to_dict(self) -> dict:
        data = {
            'name': self.name,
            'email': ''  # Always send empty email for backend compatibility
        }
        if self.phone is not None:
            data['phone'] = self.phone
        if self.employeeCount is not None:
            data['employeeCount'] = self.employeeCount
        if self.annualRevenue is not None:
            data['annualRevenue'] = self.annualRevenue
        if self.taxExemptStatus is not None:
            data['taxExemptStatus'] = self.taxExemptStatus.value
        if self.creationSource is not None:
            data['creationSource'] = self.creationSource.value
        if self.website is not None:
            data['website'] = self.website
        if self.externalId is not None:
            data['externalId'] = self.externalId
        if self.billingAddress is not None:
            data['billingAddress'] = self.billingAddress.to_dict()
        return data

@dataclass
class UpdateAccountRequest:
    name: Optional[str] = None
    phone: Optional[str] = None
    employeeCount: Optional[int] = None
    annualRevenue: Optional[float] = None
    taxExemptStatus: Optional[TaxExemptStatus] = None
    website: Optional[str] = None
    externalId: Optional[str] = None
    billingAddress: Optional[Address] = None

    def to_dict(self) -> dict:
        data = {}
        if self.name is not None:
            data['name'] = self.name
        if self.phone is not None:
            data['phone'] = self.phone
        if self.employeeCount is not None:
            data['employeeCount'] = self.employeeCount
        if self.annualRevenue is not None:
            data['annualRevenue'] = self.annualRevenue
        if self.taxExemptStatus is not None:
            data['taxExemptStatus'] = self.taxExemptStatus.value
        if self.website is not None:
            data['website'] = self.website
        if self.externalId is not None:
            data['externalId'] = self.externalId
        if self.billingAddress is not None:
            data['billingAddress'] = self.billingAddress.to_dict()
        return data 
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class AgentAttribute:
    name: str
    active: bool
    pricing: Dict[str, Any]
    id: Optional[str] = None
    agentId: Optional[str] = None

@dataclass
class Agent:
    id: str
    organizationId: str
    name: str
    description: Optional[str] = None
    active: bool = False
    agentCode: Optional[str] = None
    externalId: Optional[str] = None
    agentAttributes: List[AgentAttribute] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Agent':
        # If the response has a 'data' field, use that instead
        if 'data' in data:
            data = data['data']
            
        # Create a copy of the data and remove unwanted fields
        filtered_data = data.copy()
        fields_to_remove = ['orders', 'invoices', 'status', 'createdAt', 'updatedAt', 'ProductAttribute', 'attributes']
        for field in fields_to_remove:
            filtered_data.pop(field, None)
        
        # Map productCode to agentCode
        if 'productCode' in filtered_data:
            filtered_data['agentCode'] = filtered_data.pop('productCode')
        
        if 'active' in filtered_data:
            filtered_data['active'] = filtered_data.pop('active')
            
        return cls(**filtered_data)

@dataclass
class CreateAgentRequest:
    name: str
    description: str
    agentCode: Optional[str] = None  # Maps to productCode in backend
    externalId: Optional[str] = None

    def to_product_dict(self) -> dict:
        """Convert the agent request to a product dictionary format."""
        data = {
            'name': self.name,
            'description': self.description,
            'productCode': self.agentCode,
            'externalId': self.externalId
        }
        return data

@dataclass
class UpdateAgentRequest:
    name: Optional[str] = None
    description: Optional[str] = None
    agentAttributes: Optional[List[AgentAttribute]] = None
    externalId: Optional[str] = None
    agentCode: Optional[str] = None  # Maps to productCode in backend
    active: Optional[bool] = None

    def to_dict(self) -> dict:
        data = {}
        if self.name is not None:
            data['name'] = self.name
        if self.description is not None:
            data['description'] = self.description
        if self.externalId is not None:
            data['externalId'] = self.externalId
        if self.agentCode is not None:
            data['productCode'] = self.agentCode
        if self.active is not None:
            data['active'] = self.active
        if self.agentAttributes is not None:
            data['ProductAttribute'] = [
                {
                    'name': attr.name,
                    'active': attr.active,
                    'pricing': {
                        'eventName': attr.pricing.get('eventName'),
                        'chargeType': attr.pricing.get('chargeType'),
                        'billingFrequency': attr.pricing.get('billingFrequency'),
                        'pricingModel': attr.pricing.get('pricingModel'),
                        'pricePoints': {
                            currency: {
                                'unitPrice': price_point.get('unitPrice', 0.0) * 100,  # Convert to cents
                                'minQuantity': price_point.get('minQuantity', 0),
                                'includedQuantity': price_point.get('includedQuantity', 0),
                                'tiers': [
                                    {
                                        'minQuantity': tier.get('minQuantity', 0),
                                        'maxQuantity': tier.get('maxQuantity', 0),
                                        'unitPrice': tier.get('unitPrice', 0.0) * 100  # Convert to cents
                                    }
                                    for tier in price_point.get('tiers', [])
                                ]
                            }
                            for currency, price_point in attr.pricing.get('pricePoints', {}).items()
                        },
                        'taxable': attr.pricing.get('taxable', True),
                        'taxCategory': attr.pricing.get('taxCategory', '')
                    }
                }
                for attr in self.agentAttributes
            ]
        return data 
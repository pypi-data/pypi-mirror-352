from dataclasses import dataclass, field, fields
from typing import List, Optional, Dict, Any
from enum import Enum

class ChargeType(str, Enum):
    ONE_TIME = "oneTime"
    RECURRING = "recurring"
    USAGE = "usage"
    SEAT_BASED = "seatBased"

class PricingModelType(str, Enum):
    PER_UNIT = "PerUnit"
    VOLUME_PRICING = "VolumePricing"
    GRADUATED_PRICING = "GraduatedPricing"

class BillingFrequency(str, Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    SEMI_ANNUAL = "SemiAnnual"
    ANNUAL = "Annual"

class CreationState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

@dataclass
class Tier:
    lowerBound: float
    upperBound: Optional[float] = None
    price: float = 0

@dataclass
class PricePoint:
    currency: str
    unitPrice: float
    tiers: List[Tier] = field(default_factory=list)
    minQuantity: Optional[float] = None
    includedQuantity: Optional[float] = None

@dataclass
class OrderLineAttributePricing:
    eventName: str
    chargeType: ChargeType
    pricePoint: PricePoint
    pricingModel: PricingModelType
    billingFrequency: BillingFrequency

@dataclass
class OrderLineAttribute:
    agentAttributeId: str
    quantity: float = 0
    currency: str = ""
    pricing: Optional[OrderLineAttributePricing] = None

OrderLineAttributeList = List[OrderLineAttribute]

@dataclass
class OrderLine:
    id: str
    orderId: str
    name: str
    description: str
    startDate: str
    agentId: Optional[str] = None
    agentExternalId: Optional[str] = None
    endDate: Optional[str] = None
    totalAmount: Optional[float] = None
    billedAmountWithoutTax: Optional[float] = None
    billedTax: Optional[float] = None
    totalBilledAmount: Optional[float] = None
    agent: Optional[Dict[str, Any]] = None
    orderLineAttributes: OrderLineAttributeList = field(default_factory=list)
    creationState: Optional[CreationState] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'OrderLine':
        if isinstance(data, dict):
            # Filter out createdAt and updatedAt
            data = {k: v for k, v in data.items() if k not in ['createdAt', 'updatedAt']}
            
            # Convert creationState string to enum
            if 'creationState' in data and data['creationState']:
                data['creationState'] = CreationState(data['creationState'])
            
            # Map field names
            field_mapping = {
                'productId': 'agentId',
                'productExternalId': 'agentExternalId',
                'product': 'agent',
                'productAttributeId': 'agentAttributeId',
                'OrderLineAttribute': 'orderLineAttributes',
                'productCode': 'agentCode',
                'productAttribute': 'agentAttributes'
            }
            
            # Create a new dict with mapped field names
            mapped_data = {}
            for key, value in data.items():
                if key in field_mapping:
                    mapped_data[field_mapping[key]] = value
                else:
                    mapped_data[key] = value
            
            # Handle nested agent object
            if 'agent' in mapped_data and isinstance(mapped_data['agent'], dict):
                agent_data = mapped_data['agent']
                if 'productCode' in agent_data:
                    agent_data['agentCode'] = agent_data.pop('productCode')
                if 'productId' in agent_data:
                    agent_data['agentId'] = agent_data.pop('productId')
                if 'productExternalId' in agent_data:
                    agent_data['agentExternalId'] = agent_data.pop('productExternalId')
            
            # Handle orderLineAttribute list
            if 'orderLineAttributes' in mapped_data:
                for attr in mapped_data['orderLineAttributes']:
                    if 'productAttributeId' in attr:
                        attr['agentAttributeId'] = attr.pop('productAttributeId')
                    if 'productAttribute' in attr:
                        attr['agentAttributes'] = attr.pop('productAttribute')
                    if 'productId' in attr:
                        attr['agentId'] = attr.pop('productId')
                    if 'productExternalId' in attr:
                        attr['agentExternalId'] = attr.pop('productExternalId')
                    
                    # Handle nested agentAttribute object
                    if 'agentAttributes' in attr and isinstance(attr['agentAttributes'], dict):
                        agent_attr = attr['agentAttributes']
                        if 'productId' in agent_attr:
                            agent_attr['agentId'] = agent_attr.pop('productId')
                        if 'productExternalId' in agent_attr:
                            agent_attr['agentExternalId'] = agent_attr.pop('productExternalId')
                        # Remove pricing from agentAttributes
                        if 'pricing' in agent_attr:
                            del agent_attr['pricing']
                    
                    # Handle pricing in orderLineAttribute
                    if 'pricing' in attr and isinstance(attr['pricing'], dict):
                        pricing = attr['pricing']
                        # Remove PricePoints if it exists
                        if 'PricePoints' in pricing:
                            del pricing['PricePoints']
                        # Remove taxCategory if it exists
                        if 'taxCategory' in pricing:
                            del pricing['taxCategory']
                        # Convert pricePoints to pricePoint if needed
                        if 'pricePoints' in pricing and 'USD' in pricing['pricePoints']:
                            usd_price = pricing['pricePoints']['USD']
                            pricing['pricePoint'] = {
                                'currency': 'USD',
                                'unitPrice': usd_price['unitPrice'] / 100,
                                'tiers': [
                                    {
                                        'minQuantity': tier.get('minQuantity', 0),
                                        'maxQuantity': tier.get('maxQuantity', 0),
                                        'unitPrice': tier.get('unitPrice', 0) / 100
                                    }
                                    for tier in usd_price.get('tiers', [])
                                ],
                                'minQuantity': usd_price.get('minQuantity', 0),
                                'includedQuantity': usd_price.get('includedQuantity', 0)
                            }
                            del pricing['pricePoints']
                        # Handle existing pricePoint
                        elif 'pricePoint' in pricing:
                            price_point = pricing['pricePoint']
                            if 'unitPrice' in price_point:
                                price_point['unitPrice'] = price_point['unitPrice'] / 100
                            if 'tiers' in price_point:
                                for tier in price_point['tiers']:
                                    if 'unitPrice' in tier:
                                        tier['unitPrice'] = tier['unitPrice'] / 100
            
            # Remove any remaining productId fields
            if 'productId' in mapped_data:
                mapped_data['agentId'] = mapped_data.pop('productId')
            if 'productExternalId' in mapped_data:
                mapped_data['agentExternalId'] = mapped_data.pop('productExternalId')
            
            # Ensure required fields are present
            required_fields = {'id', 'orderId', 'name', 'description', 'startDate'}
            for field in required_fields:
                if field not in mapped_data:
                    mapped_data[field] = None
            
            # Create the instance with default values for missing fields
            return cls(**mapped_data)
        return data

OrderLineList = List[OrderLine]

@dataclass
class Order:
    id: str
    name: str
    organizationId: str
    startDate: str
    totalAmount: float
    estimatedTax: float
    billedAmountNoTax: float
    billedTax: float
    totalBilledAmount: float
    pendingBillingAmount: float
    accountId: Optional[str] = None
    accountExternalId: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[str] = None
    orderLines: OrderLineList = field(default_factory=list)
    account: Optional[Dict[str, Any]] = None
    creationState: Optional[CreationState] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        if 'data' in data:
            data = data['data']
            
        # Filter out createdAt and updatedAt
        data = {k: v for k, v in data.items() if k not in ['createdAt', 'updatedAt']}
            
        # Map field names to match the API response
        field_mapping = {
            'customerId': 'accountId',
            'customerExternalId': 'accountExternalId',
            'customer': 'account',
            'productId': 'agentId',
            'productExternalId': 'agentExternalId',
            'product': 'agent',
            'productAttributeId': 'agentAttributeId',
            'OrderLine': 'orderLines',
            'OrderLineAttribute': 'orderLineAttributes'
        }
        
        # Create a new dict with mapped field names
        mapped_data = {}
        for key, value in data.items():
            if key in field_mapping:
                mapped_data[field_mapping[key]] = value
            else:
                mapped_data[key] = value
            
        # Handle orderLine list
        if 'orderLines' in mapped_data and mapped_data['orderLines']:
            mapped_data['orderLines'] = [OrderLine.from_dict(line) for line in mapped_data['orderLines']]

        # Convert creationState string to enum
        if 'creationState' in mapped_data and mapped_data['creationState']:
            mapped_data['creationState'] = CreationState(mapped_data['creationState'])
            
        # Get the model fields
        model_fields = {f.name for f in fields(cls)}
        
        # Create a new dict with only the fields that exist in the model
        final_data = {}
        for field in model_fields:
            if field in mapped_data:
                final_data[field] = mapped_data[field]
            elif field == 'endDate' and 'endDate' in data:  # Explicitly handle endDate
                final_data[field] = data['endDate']
            
        return cls(**final_data)

@dataclass
class CreateOrderRequest:
    name: str
    accountId: Optional[str] = None
    accountExternalId: Optional[str] = None
    description: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    currency: Optional[Currency] = None
    orderLines: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> dict:
        data = self.__dict__
        
        # Map fields for the API
        field_mapping = {
            'accountId': 'customerId',
            'accountExternalId': 'customerExternalId',
            'agentId': 'productId',
            'agentExternalId': 'productExternalId'
        }
        
        # Create a new dict with mapped field names
        mapped_data = {}
        for key, value in data.items():
            if key in field_mapping:
                mapped_data[field_mapping[key]] = value
            else:
                mapped_data[key] = value
        
        # Handle orderLines mapping
        if 'orderLines' in mapped_data and mapped_data['orderLines']:
            for line in mapped_data['orderLines']:
                if 'agentId' in line:
                    line['productId'] = line.pop('agentId')
                if 'agentExternalId' in line:
                    line['productExternalId'] = line.pop('agentExternalId')
        
        return mapped_data
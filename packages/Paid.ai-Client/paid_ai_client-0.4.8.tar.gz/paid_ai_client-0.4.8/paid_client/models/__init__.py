"""
Models for the Paid.ai client.
"""

# These imports make the classes available when imported from paid_client.models
from .account import Account, Address, CreateAccountRequest, UpdateAccountRequest, CreationSource, TaxExemptStatus
from .agent import Agent, AgentAttribute, CreateAgentRequest, UpdateAgentRequest
from .contact import Contact, CreateContactRequest, Salutation
from .order import Order, OrderLine, OrderLineAttribute, CreateOrderRequest, ChargeType, PricingModelType, BillingFrequency, CreationState, Currency, Tier, PricePoint, OrderLineAttributePricing

# Define what should be exported when using "from paid_client.models import *"
__all__ = [
    # Account models
    "Account", "Address", "CreateAccountRequest", "UpdateAccountRequest", "CreationSource", "TaxExemptStatus",
    
    # Agent models
    "Agent", "AgentAttribute", "CreateAgentRequest", "UpdateAgentRequest",
    
    # Contact models
    "Contact", "CreateContactRequest", "UpdateContactRequest", "Salutation",
    
    # Order models
    "Order", "OrderLine", "OrderLineAttribute", "CreateOrderRequest",
    "ChargeType", "PricingModelType", "BillingFrequency", "CreationState",
    "Currency", "Tier", "PricePoint", "OrderLineAttributePricing",
] 
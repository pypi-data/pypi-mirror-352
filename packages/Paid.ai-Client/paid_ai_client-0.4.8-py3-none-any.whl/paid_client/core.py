import requests
import logging
import threading
import json
from typing import Any, List, TypeVar, Optional, Dict
from .models.account import Account, CreateAccountRequest, UpdateAccountRequest
from .models.signal import Signal
from .models.order import Order, OrderLine, CreateOrderRequest
from .models.agent import Agent, CreateAgentRequest, UpdateAgentRequest
from .models.contact import Contact, CreateContactRequest
from dataclasses import asdict

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

T = TypeVar('T')

class PaidClient:
    """
    Client for the AgentPaid API.
    Collects signals and flushes them to the API periodically or when the buffer is full.
    """

    ORG = 'org'  # or any string, it doesn't matter

    def __init__(self, api_key: str, api_url: str = 'https://api.agentpaid.io'):
        """
        Initialize the client with an API key and optional API URL.
        
        Args:
            api_key: The API key for authentication
            api_url: The base URL for the API (defaults to 'https://api.agentpaid.io')
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        self.signals: List[Signal[Any]] = []
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
        # Start the periodic flush timer
        self._start_timer()
        
        logger.info(f"ApClient initialized with endpoint: {self.api_url}")

    def _start_timer(self):
        """Start a timer to flush signals every 30 seconds"""
        self.timer = threading.Timer(30.0, self._timer_callback)
        self.timer.daemon = True  # Allow the program to exit even if timer is running
        self.timer.start()
        
    def _timer_callback(self):
        """Callback for the timer to flush signals and restart the timer"""
        try:
            self.flush()
        except Exception as e:
            logger.error(f"Error during automatic flush: {str(e)}")
        finally:
            self._start_timer()  # Restart the timer
            
    def flush(self):
        """
        Send all collected signals to the API and clear the buffer.
        """
        if not self.signals:
            logger.debug("No signals to flush")
            return
        
        url = f"{self.api_url}/api/entries/bulk"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        body = {
            "transactions": [vars(signal) for signal in self.signals]
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Successfully flushed {len(self.signals)} signals")
            self.signals = []
        except requests.RequestException as e:
            logger.error(f"Failed to flush signals: {str(e)}")
            raise RuntimeError(f"Failed to flush signals: {str(e)}")
    
    def record_usage(self, agent_id: str, external_user_id: str, signal_name: str, data: Any):
        """
        Record a usage signal.
        
        Args:
            agent_id: The ID of the agent
            external_user_id: The external user ID (customer)
            signal_name: The name of the signal event
            data: The data to include with the signal
        """
        signal = Signal(
            event_name=signal_name,
            agent_id=agent_id,
            customer_id=external_user_id,
            data=data
        )
        
        self.signals.append(signal)
        logger.debug(f"Recorded signal: {signal_name} for agent {agent_id}")
        
        # If buffer reaches 100 signals, flush immediately
        if len(self.signals) >= 100:
            logger.info("Signal buffer reached 100, flushing")
            self.flush()
    
    def __del__(self):
        """
        Cleanup method to flush remaining signals when the object is garbage collected.
        """
        try:
            # Cancel the timer
            if hasattr(self, 'timer'):
                self.timer.cancel()
            
            # Flush any remaining signals
            if self.signals:
                logger.info("Flushing signals during cleanup")
                self.flush()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    # Account methods
    def create_account(self, data: CreateAccountRequest) -> Account:
        """
        Create a new account.
        
        Args:
            data: Account data including name, email, etc.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/customers"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data.to_dict())
            response.raise_for_status()
            return Account.from_dict(response.json()['data'])
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to create account: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to create account: {str(e)}")

    def get_account(self, account_id: str) -> Account:
        """Get a specific account."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/customer/{account_id}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return Account.from_dict(response.json()['data'])
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to get account: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get account: {str(e)}")
    
    def get_account_by_external_id(self, external_id: str) -> Account:
        """
        Get an account by its external ID.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/customer/external/{external_id}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            if 'data' in response_data:
                return Account.from_dict(response_data['data'])
            return Account.from_dict(response_data)
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to get account by external ID: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get account by external ID: {str(e)}")

    def list_accounts(self) -> List[Account]:
        """List all accounts for an organization."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/customers"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return [Account.from_dict(account) for account in response.json()['data']]
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to list accounts: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to list accounts: {str(e)}")

    def update_account(self, account_id: str, data: UpdateAccountRequest) -> Account:
        """
        Update an existing account.
        
        Args:
            account_id: The account ID
            data: Fields to update
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/customer/{account_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.put(url, headers=headers, json=data.to_dict())
            response.raise_for_status()
            response_data = response.json()
            if 'data' in response_data:
                return Account.from_dict(response_data['data'])
            return Account.from_dict(response_data)
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to update account: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to update account: {str(e)}")
        

    def update_account_by_external_id(self, external_id: str, data: UpdateAccountRequest) -> Account:
        """
        Update an account by its external ID.
        
        Args:
            external_id: The external ID of the account
            data: Fields to update
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/customer/external/{external_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.put(url, headers=headers, json=data.to_dict())
            response.raise_for_status()
            
            # Check if response has content
            if not response.text:
                raise RuntimeError("Empty response received from server")
                
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON response: {str(e)}")
            
            # Handle both response formats
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return Account.from_dict(response_data['data'])
                return Account.from_dict(response_data)
            else:
                raise RuntimeError(f"Unexpected response format: {response_data}")
                
        except requests.exceptions.HTTPError as e:
            error_data = {}
            if e.response and e.response.text:
                try:
                    error_data = e.response.json()
                except json.JSONDecodeError:
                    error_data = {'error': {'message': e.response.text}}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to update account by external ID: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to update account by external ID: {str(e)}")

    def delete_account(self, account_id: str) -> None:
        """Delete an account."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/customer/{account_id}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to delete account: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to delete account: {str(e)}")
    
    def delete_account_by_external_id(self, external_id: str) -> None:
        """
        Delete an account by its external ID.
        
        Args:
            external_id: The external ID of the account to delete
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/customer/external/{external_id}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.text else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            raise RuntimeError(f"Failed to delete account by external ID: {error_message}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to delete account by external ID: {str(e)}")

    # Order methods
    def create_order(self, data: CreateOrderRequest) -> Order:
        """
        Create a new order.
        
        Args:
            data: Order data including accountId, name, description, etc.
        """
        # Convert the request to a dictionary
        request_data = asdict(data)
        
        # Map accountId and accountExternalId to customerId and customerExternalId
        # Only include non-null values
        if 'accountId' in request_data and request_data['accountId'] is not None:
            request_data['customerId'] = request_data.pop('accountId')
        if 'accountExternalId' in request_data and request_data['accountExternalId'] is not None:
            request_data['customerExternalId'] = request_data.pop('accountExternalId')
            
        # Map agentId to productId in order lines
        if 'orderLines' in request_data:
            for line in request_data['orderLines']:
                if 'agentId' in line and line['agentId'] is not None:
                    line['productId'] = line.pop('agentId')
                if 'agentExternalId' in line and line['agentExternalId'] is not None:
                    line['productExternalId'] = line.pop('agentExternalId')

        # Try to create the order
        try:
            # Make direct request to the V2 endpoint
            response = requests.post(
                f"{self.api_url}/api/organizations/{self.ORG}/sdk-orders",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json=request_data
            )
            response.raise_for_status()
            order_data = response.json()
            
            # Process the response data
            if 'data' in order_data:
                # Handle order lines
                if 'orderLine' in order_data['data']:
                    for line in order_data['data']['orderLine']:
                        # Rename productId to agentId
                        if 'productId' in line:
                            line['agentId'] = line.pop('productId')
                        
                        # Rename productCode to agentCode in agent object
                        if 'agent' in line and isinstance(line['agent'], dict):
                            if 'productCode' in line['agent']:
                                line['agent']['agentCode'] = line['agent'].pop('productCode')
                            if 'productId' in line['agent']:
                                line['agent']['agentId'] = line['agent'].pop('productId')
                            if 'productExternalId' in line['agent']:
                                line['agent']['agentExternalId'] = line['agent'].pop('productExternalId')
                        
                        # Handle order line attributes
                        if 'orderLineAttribute' in line:
                            for attr in line['orderLineAttribute']:
                                # Rename productAttributeId to agentAttributeId
                                if 'productAttributeId' in attr:
                                    attr['agentAttributeId'] = attr.pop('productAttributeId')
                                
                                # Handle agent attribute
                                if 'agentAttribute' in attr:
                                    # Get the agent attribute data
                                    agent_attr = attr.pop('agentAttribute')
                                    
                                    # Create a new agentAttributes object with only the fields we want
                                    new_agent_attr = {
                                        'name': agent_attr.get('name'),
                                        'active': agent_attr.get('active'),
                                        'id': agent_attr.get('id')
                                    }
                                    
                                    # Add agentId if productId exists
                                    if 'productId' in agent_attr:
                                        new_agent_attr['agentId'] = agent_attr['productId']
                                    if 'productExternalId' in agent_attr:
                                        new_agent_attr['agentExternalId'] = agent_attr['productExternalId']
                                    
                                    # Set the new agentAttributes
                                    attr['agentAttributes'] = new_agent_attr
            
            return Order.from_dict(order_data['data'])
        except Exception as e:
            print("\nError creating order:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response headers: {json.dumps(dict(e.response.headers), indent=2)}")
                try:
                    print(f"Response body: {json.dumps(e.response.json(), indent=2)}")
                except:
                    print(f"Response text: {e.response.text}")
            raise

    def get_order(self, order_id: str) -> Order:
        """Get a specific order."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/orders/{order_id}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f"API Response: {json.dumps(response_data, indent=2)}")
            return Order.from_dict(response_data['data'])
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to get order: {error_message}")
            raise RuntimeError(f"Failed to get order: {error_message}")

    def list_orders(self) -> List[Order]:
        """List all orders for an organization."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/orders"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return [Order.from_dict(order) for order in response.json()['data']]
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to list orders: {error_message}")
            raise RuntimeError(f"Failed to list orders: {error_message}")

    def add_order_lines(self, order_id: str, lines: List[Dict[str, Any]]) -> List[OrderLine]:
        """
        Add order lines to an existing order.
        
        Args:
            order_id: The order ID
            lines: List of order lines to add
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/sdk-orders/{order_id}/lines"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Map fields to match CreateOrderLineRequest interface
            order_lines = []
            for line in lines:
                mapped_line = {}
                if 'agentId' in line and line['agentId'] is not None:
                    mapped_line['productId'] = line['agentId']
                if 'agentExternalId' in line and line['agentExternalId'] is not None:
                    mapped_line['productExternalId'] = line['agentExternalId']
                if 'name' in line:
                    mapped_line['name'] = line['name']
                if 'description' in line:
                    mapped_line['description'] = line['description']
                order_lines.append(mapped_line)
            
            # Wrap in orderLines object as expected by the server
            request_data = {
                'orderLines': order_lines
            }
            
            response = requests.post(url, headers=headers, json=request_data)
            response.raise_for_status()
            
            # Extract order lines from the response
            response_data = response.json()
            if 'data' in response_data and 'OrderLine' in response_data['data']:
                # Process each order line to map product fields to agent fields
                for line in response_data['data']['OrderLine']:
                    # Rename productId to agentId
                    if 'productId' in line:
                        line['agentId'] = line.pop('productId')
                    if 'productExternalId' in line:
                        line['agentExternalId'] = line.pop('productExternalId')
                    
                    # Rename productCode to agentCode in agent object
                    if 'agent' in line and isinstance(line['agent'], dict):
                        if 'productCode' in line['agent']:
                            line['agent']['agentCode'] = line['agent'].pop('productCode')
                        if 'productId' in line['agent']:
                            line['agent']['agentId'] = line['agent'].pop('productId')
                        if 'productExternalId' in line['agent']:
                            line['agent']['agentExternalId'] = line['agent'].pop('productExternalId')
                    
                    # Handle order line attributes
                    if 'orderLineAttribute' in line:
                        for attr in line['orderLineAttribute']:
                            # Rename productAttributeId to agentAttributeId
                            if 'productAttributeId' in attr:
                                attr['agentAttributeId'] = attr.pop('productAttributeId')
                            
                            # Handle agent attribute
                            if 'agentAttribute' in attr:
                                # Get the agent attribute data
                                agent_attr = attr.pop('agentAttribute')
                                
                                # Create a new agentAttributes object with only the fields we want
                                new_agent_attr = {
                                    'name': agent_attr.get('name'),
                                    'active': agent_attr.get('active'),
                                    'id': agent_attr.get('id')
                                }
                                
                                # Add agentId if productId exists
                                if 'productId' in agent_attr:
                                    new_agent_attr['agentId'] = agent_attr['productId']
                                if 'productExternalId' in agent_attr:
                                    new_agent_attr['agentExternalId'] = agent_attr['productExternalId']
                                
                                # Set the new agentAttributes
                                attr['agentAttributes'] = new_agent_attr
                
                return [OrderLine.from_dict(line) for line in response_data['data']['OrderLine']]
            return []
        except Exception as e:
            print("\nError adding order lines:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response headers: {json.dumps(dict(e.response.headers), indent=2)}")
                try:
                    error_data = e.response.json()
                    print(f"Response body: {json.dumps(error_data, indent=2)}")
                    if error_data.get('error', {}).get('details') == "Product has no attributes":
                        print("\nThe agent used in this order line has no attributes. Please add attributes to the agent first using update_agent or update_agent_by_external_id.")
                except:
                    print(f"Response text: {e.response.text}")
            raise

    def activate_order(self, order_id: str) -> str:
        """
        Activate an order.
        
        Args:
            order_id: The ID of the order to activate
            
        Returns:
            str: "Order activated successfully" if the request succeeds
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/orders/{order_id}/activate"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return "Order activated successfully"
            
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to activate order: {error_message}")
            raise RuntimeError(f"Failed to activate order: {error_message}")

    def delete_order(self, order_id: str) -> None:
        """
        Delete an order. Only orders in draft state can be deleted.
        
        Args:
            order_id: The ID of the order to delete
            
        Raises:
            RuntimeError: If the order cannot be deleted (e.g., not in draft state)
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/orders/{order_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to delete order: {error_message}")
            raise RuntimeError(f"Failed to delete order: {error_message}")

    # Agent methods
    def create_agent(self, agent: CreateAgentRequest) -> Agent:
        """Create a new agent.

        Args:
            agent (CreateAgentRequest): The agent data to create.

        Returns:
            Agent: The created agent.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/products"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Convert the agent request to product format
            request_data = agent.to_product_dict()
            
            # Map agentAttribute to ProductAttribute for the API request
            if hasattr(agent, 'agentAttribute') and agent.agentAttribute:
                request_data['ProductAttribute'] = [
                    {
                        'name': attr.name,
                        'active': attr.active,
                        'pricing': attr.pricing
                    }
                    for attr in agent.agentAttribute
                ]
            
            response = requests.post(url, headers=headers, json=request_data)
            response.raise_for_status()
            data = response.json()
            
            # Process the response data
            if 'data' in data:
                # Remove attributes and ProductAttribute
                if 'attributes' in data['data']:
                    data['data'].pop('attributes', None)
                if 'ProductAttribute' in data['data']:
                    data['data'].pop('ProductAttribute', None)
            
            agent = Agent.from_dict(data['data'])
            if hasattr(agent, 'agentAttributes'):
                delattr(agent, 'agentAttributes')
            return agent
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to create agent: {error_message}")
            raise RuntimeError(f"Failed to create agent: {error_message}")

    def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID.

        Args:
            agent_id (str): The ID of the agent to get.

        Returns:
            Agent: The requested agent.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/products/{agent_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Map ProductAttribute to agentAttributes in response
            if 'data' in data:
                if 'ProductAttribute' in data['data']:
                    data['data']['agentAttributes'] = data['data'].pop('ProductAttribute')
                    # Also map productId to agentId in each attribute and convert prices
                    if data['data']['agentAttributes']:
                        for attr in data['data']['agentAttributes']:
                            if 'productId' in attr:
                                attr['agentId'] = attr.pop('productId')
                            
                            # Convert prices from cents to dollars and remove taxCategory
                            if 'pricing' in attr and 'pricePoints' in attr['pricing']:
                                for currency, price_point in attr['pricing']['pricePoints'].items():
                                    if 'unitPrice' in price_point:
                                        price_point['unitPrice'] = price_point['unitPrice'] / 100
                                    if 'tiers' in price_point:
                                        for tier in price_point['tiers']:
                                            if 'unitPrice' in tier:
                                                tier['unitPrice'] = tier['unitPrice'] / 100
                            # Remove taxCategory if present
                            if 'pricing' in attr and 'taxCategory' in attr['pricing']:
                                del attr['pricing']['taxCategory']
            
            return Agent.from_dict(data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to get agent: {error_message}")
            raise RuntimeError(f"Failed to get agent: {error_message}")

    def get_agent_by_external_id(self, external_id: str) -> Agent:
        """Get an agent by external ID.

        Args:
            external_id (str): The external ID of the agent to get.

        Returns:
            Agent: The requested agent.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/products/external/{external_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Map ProductAttribute to agentAttributes in response
            if 'data' in data:
                if 'ProductAttribute' in data['data']:
                    data['data']['agentAttributes'] = data['data'].pop('ProductAttribute')
                    # Also map productId to agentId in each attribute and convert prices
                    if data['data']['agentAttributes']:
                        for attr in data['data']['agentAttributes']:
                            if 'productId' in attr:
                                attr['agentId'] = attr.pop('productId')
                            
                            # Convert prices from cents to dollars and remove taxCategory
                            if 'pricing' in attr and 'pricePoints' in attr['pricing']:
                                for currency, price_point in attr['pricing']['pricePoints'].items():
                                    if 'unitPrice' in price_point:
                                        price_point['unitPrice'] = price_point['unitPrice'] / 100
                                    if 'tiers' in price_point:
                                        for tier in price_point['tiers']:
                                            if 'unitPrice' in tier:
                                                tier['unitPrice'] = tier['unitPrice'] / 100
                            # Remove taxCategory if present
                            if 'pricing' in attr and 'taxCategory' in attr['pricing']:
                                del attr['pricing']['taxCategory']
            
            return Agent.from_dict(data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to get agent by external ID: {error_message}")
            raise RuntimeError(f"Failed to get agent by external ID: {error_message}")

    def list_agents(self) -> List[Agent]:
        """List all agents.

        Returns:
            List[Agent]: A list of agents.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/products"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Map ProductAttribute to agentAttributes in each agent
            agents = []
            for agent_data in data.get('data', []):
                # Map ProductAttribute to agentAttributes
                if 'ProductAttribute' in agent_data:
                    agent_data['agentAttributes'] = agent_data.pop('ProductAttribute')
                    # Also map productId to agentId in each attribute and convert prices
                    if agent_data['agentAttributes']:
                        for attr in agent_data['agentAttributes']:
                            if 'productId' in attr:
                                attr['agentId'] = attr.pop('productId')
                            
                            # Convert prices from cents to dollars and remove taxCategory
                            if 'pricing' in attr and 'pricePoints' in attr['pricing']:
                                for currency, price_point in attr['pricing']['pricePoints'].items():
                                    if 'unitPrice' in price_point:
                                        price_point['unitPrice'] = price_point['unitPrice'] / 100
                                    if 'tiers' in price_point:
                                        for tier in price_point['tiers']:
                                            if 'unitPrice' in tier:
                                                tier['unitPrice'] = tier['unitPrice'] / 100
                            # Remove taxCategory if present
                            if 'pricing' in attr and 'taxCategory' in attr['pricing']:
                                del attr['pricing']['taxCategory']
                
                agents.append(Agent.from_dict({'data': agent_data}))
            
            return agents
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to list agents: {error_message}")
            raise RuntimeError(f"Failed to list agents: {error_message}")

    def update_agent(self, agent_id: str, data: UpdateAgentRequest) -> Agent:
        """
        Update an existing agent.
        
        Args:
            agent_id: The agent ID
            data: Fields to update
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/products/{agent_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Convert the dataclass to a dict
            request_data = data.to_dict()
            
            # Map agentAttribute to ProductAttribute for the API request
            if 'agentAttribute' in request_data:
                request_data['ProductAttribute'] = request_data.pop('agentAttribute')
                for attr in request_data['ProductAttribute']:
                    if 'agentId' in attr:
                        attr['productId'] = attr.pop('agentId')
                    # Remove taxCategory if present
                    if 'pricing' in attr:
                        if 'taxCategory' in attr['pricing']:
                            del attr['pricing']['taxCategory']
            
            # Log the request data for debugging
            logger.debug(f"Updating agent with data: {json.dumps(request_data, indent=2)}")
            
            response = requests.put(url, headers=headers, json=request_data)
            response.raise_for_status()
            data = response.json()
            
            # Map ProductAttribute to agentAttribute in response and remove taxCategory
            if 'data' in data:
                if 'ProductAttribute' in data['data']:
                    data['data']['agentAttributes'] = data['data'].pop('ProductAttribute')
                    for attr in data['data']['agentAttributes']:
                        if 'productId' in attr:
                            attr['agentId'] = attr.pop('productId')
                        # Remove taxCategory if present
                        if 'pricing' in attr:
                            if 'taxCategory' in attr['pricing']:
                                del attr['pricing']['taxCategory']
            
            return Agent.from_dict(data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to update agent: {error_message}")
            raise RuntimeError(f"Failed to update agent: {error_message}")

    def update_agent_by_external_id(self, external_id: str, data: UpdateAgentRequest) -> Agent:
        """
        Update an existing agent.
        
        Args:
            agent_id: The agent ID
            data: Fields to update
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/products/external/{external_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Convert the dataclass to a dict
            request_data = data.to_dict()
            
            # Map agentAttribute to ProductAttribute for the API request
            if 'agentAttribute' in request_data:
                request_data['ProductAttribute'] = request_data.pop('agentAttribute')
                for attr in request_data['ProductAttribute']:
                    if 'agentId' in attr:
                        attr['productId'] = attr.pop('agentId')
                    # Remove taxCategory if present
                    if 'pricing' in attr:
                        if 'taxCategory' in attr['pricing']:
                            del attr['pricing']['taxCategory']
            
            # Log the request data for debugging
            logger.debug(f"Updating agent with data: {json.dumps(request_data, indent=2)}")
            
            response = requests.put(url, headers=headers, json=request_data)
            response.raise_for_status()
            data = response.json()
            
            # Map ProductAttribute to agentAttribute in response and remove taxCategory
            if 'data' in data:
                if 'ProductAttribute' in data['data']:
                    data['data']['agentAttributes'] = data['data'].pop('ProductAttribute')
                    for attr in data['data']['agentAttributes']:
                        if 'productId' in attr:
                            attr['agentId'] = attr.pop('productId')
                        # Remove taxCategory if present
                        if 'pricing' in attr:
                            if 'taxCategory' in attr['pricing']:
                                del attr['pricing']['taxCategory']
            
            return Agent.from_dict(data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to update agent by external ID: {error_message}")
            raise RuntimeError(f"Failed to update agent by external ID: {error_message}")

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/products/{agent_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to delete agent: {error_message}")
            raise RuntimeError(f"Failed to delete agent: {error_message}")
    
    def delete_agent_by_external_id(self, external_id: str) -> None:
        """Delete an agent by external ID."""
        url = f"{self.api_url}/api/organizations/{self.ORG}/products/external/{external_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to delete agent by external ID: {error_message}")
            raise RuntimeError(f"Failed to delete agent by external ID: {error_message}")

    # Contact methods
    def create_contact(self, data: CreateContactRequest) -> Contact:
        """
        Create a new contact.
        
        Args:
            data: Contact data including accountId, firstName, lastName, etc.
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/contacts"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Create a new dict with all properties from the request
            api_data = data.to_dict()
            
            # Map fields for the API
            if 'accountId' in api_data:
                api_data['customerId'] = api_data.pop('accountId')
            if 'accountExternalId' in api_data:
                api_data['customerExternalId'] = api_data.pop('accountExternalId')
            
            # Log the request data for debugging
            logger.debug(f"Creating contact with data: {json.dumps(api_data, indent=2)}")
            
            response = requests.post(url, headers=headers, json=api_data)
            
            # Try to get detailed error information
            if not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', str(response.text))
                    error_details = error_data.get('error', {}).get('details', {})
                    if error_details:
                        error_message += f"\nDetails: {json.dumps(error_details, indent=2)}"
                except json.JSONDecodeError:
                    error_message = f"Server returned {response.status_code}: {response.text}"
                raise RuntimeError(f"Failed to create contact: {error_message}")
            
            response.raise_for_status()
            
            # Map customerId to accountId in the response
            response_data = response.json()['data']
            if 'customerId' in response_data:
                response_data['accountId'] = response_data.pop('customerId')
            
            return Contact.from_dict(response_data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                    error_details = error_data.get('error', {}).get('details', {})
                    if error_details:
                        error_message += f"\nDetails: {json.dumps(error_details, indent=2)}"
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to create contact: {error_message}")
            raise RuntimeError(f"Failed to create contact: {error_message}")

    def get_contact(self, contact_id: str) -> Contact:
        """
        Get a specific contact.
        
        Args:
            contact_id: The contact ID
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/contacts/{contact_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Map customerId to accountId in the response
            response_data = response.json()['data']
            if 'customerId' in response_data:
                response_data['accountId'] = response_data.pop('customerId')
            
            return Contact.from_dict(response_data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to get contact: {error_message}")
            raise RuntimeError(f"Failed to get contact: {error_message}")

    def get_contact_by_external_id(self, external_id: str) -> Contact:
        """
        Get a specific contact by external ID.
        
        Args:
            external_id: The external ID of the contact
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/contacts/external/{external_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Map customerId to accountId in the response
            response_data = response.json()['data']
            if 'customerId' in response_data:
                response_data['accountId'] = response_data.pop('customerId')
            
            return Contact.from_dict(response_data)
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to get contact by external ID: {error_message}")
            raise RuntimeError(f"Failed to get contact by external ID: {error_message}")

    def list_contacts(self, external_id: Optional[str] = None) -> List[Contact]:
        """
        List all contacts for an organization, optionally filtered by external ID.
        
        Args:
            external_id: Optional external ID to filter contacts
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/contacts"
        if external_id:
            url += f"?externalId={external_id}"
            
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Map customerId to accountId in each contact's data
            contacts_data = response.json()['data']
            for contact_data in contacts_data:
                if 'customerId' in contact_data:
                    contact_data['accountId'] = contact_data.pop('customerId')
            
            return [Contact.from_dict(contact) for contact in contacts_data]
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to list contacts: {error_message}")
            raise RuntimeError(f"Failed to list contacts: {error_message}")
        
    def delete_contact(self, contact_id: str) -> str:
        """
        Delete a contact.
        
        Args:
            contact_id: The contact ID
            
        Returns:
            str: Success message if contact was deleted successfully
            
        Raises:
            RuntimeError: If the contact doesn't exist or if there's an error during deletion
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/contacts/{contact_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return "Contact deleted successfully"
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to delete contact: {error_message}")
            raise RuntimeError(f"Failed to delete contact: {error_message}")
    
    def delete_contact_by_external_id(self, external_id: str) -> str:
        """
        Delete a contact by external ID.
        
        Args:
            external_id: The external ID of the contact
            
        Returns:
            str: Success message if contact was deleted successfully
            
        Raises:
            RuntimeError: If the contact doesn't exist or if there's an error during deletion
        """
        url = f"{self.api_url}/api/organizations/{self.ORG}/contacts/external/{external_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return "Contact deleted successfully"
        except requests.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = f"{str(e)} - Response: {e.response.text}"
            logger.error(f"Failed to delete contact by external ID: {error_message}")
            raise RuntimeError(f"Failed to delete contact by external ID: {error_message}")
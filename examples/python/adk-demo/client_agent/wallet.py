# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from abc import ABC, abstractmethod
import os
import time
import uuid
import logging
import requests
import webbrowser
import eth_account
from eth_account.messages import encode_defunct
from Crypto.Hash import keccak

from x402_a2a.types import PaymentPayload, x402PaymentRequiredResponse
from x402_a2a.core.wallet import process_payment_required

class Wallet(ABC):
    """
    An abstract base class for a wallet that can sign payment requirements.
    This interface allows for different wallet implementations (e.g., local, MPC, hardware)
    to be used interchangeably by the client agent.
    """

    @abstractmethod
    def sign_payment(self, requirements: x402PaymentRequiredResponse) -> PaymentPayload:
        """
        Signs a payment requirement and returns the signed payload.
        """
        raise NotImplementedError


class SLAccount:
    """
    SlAccount implementation mimics eth_account.Account interface.
    We use the Silence Laboratories MPC infrastructure for managing transactions.
    """
    
    def __init__(self, agent_token: str, paired_key_vault_url: str):
        """
        Initialize SL account.    
        Args:
            agent_token: Agent token so that mpc wallet can identify/Register any particular agent
            paired_key_vault_url: URL of mpc wallet frontend
        """
        self.agent_token = agent_token
        self.paired_key_vault_url = paired_key_vault_url.rstrip('/')
        self._address = None
        
    @property
    def address(self) -> str:
        """Get the wallet address from agent registration."""
        if self._address is None:
            self._address = self._get_address()
        return self._address

        
    
    def sign_message(self, message_hash, receiver_address=None, amount=None, chain_id=None):
      
        # Ensure message_hash is a hex string
        if isinstance(message_hash, bytes):
            message_hash = message_hash.hex()
        
        if not message_hash.startswith('0x'):
          message_hash = f"0x{message_hash}"      
                      
        sign_request = {
            "agentToken": self.agent_token,
            "hash": message_hash,
            "message": f"Sign payment mendate to address {receiver_address} for {amount} USDC",
            "payload": {
                "receiver": receiver_address,
                "amount": str(amount),
                "chainId": str(chain_id)
            },
            "amount": str(amount) if amount else "0",
            "chainId": str(chain_id)
        }
                
        # Send request to orchestrator
        response = requests.post(
            "https://browserintent-mpc-orchestrator.demo.silencelaboratories.com/api/agent-sign-request",
            json=sign_request,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for phone approval
        )
        
        if response.status_code != 200:
            raise Exception(f"Orchestrator API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if not result.get('success', False):
            raise Exception(f"Sign request failed: {result.get('error', 'Unknown error')}")
        
        # Return the signature directly from the API response
        signature_hex = result.get('signature')
        if not signature_hex:
            raise Exception("No signature received from phone approval")
     
        return signature_hex
    
    def _get_address(self) -> str:
        """Get wallet address from orchestrator API."""
        try:
            response = requests.post(
                f"{self.paired_key_vault_url}/api/agent-status",
                json={"agentToken": self.agent_token},
                timeout=20
            )            
            if response.status_code == 200:
                result = response.json()
                if result.get('valid', False):
                    wallet_address = result.get('walletAddress')
                    if not wallet_address:
                        raise ValueError("No wallet address in API response")
                    return wallet_address
                else:
                    error_msg = result.get('message', 'Unknown error')
                    raise ValueError(f"Agent token not valid: {error_msg}")
            else:
                raise requests.HTTPError(f"API request failed with status {response.status_code}")
                
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to orchestrator API: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error getting wallet address: {str(e)}")
    


class MockLocalWallet(Wallet):
    """
    A mock wallet implementation that uses a hardcoded local private key.
    FOR DEMONSTRATION PURPOSES ONLY. DO NOT USE IN PRODUCTION.
    """

    def sign_payment(self, requirements: x402PaymentRequiredResponse) -> PaymentPayload:
        """
        Signs a payment requirement using x402.exact EIP-3009 signing.
        """
        private_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
        account = eth_account.Account.from_key(private_key)
        
        return process_payment_required(requirements, account)


class SLWallet(Wallet):
    """
    This wallet uses Silence Laboratories MPC infrastructure.
    """
    
    def __init__(self):
        """Initialize the wallet with agent token and paired-key-vault URL."""
        agent_token = os.getenv('AGENT_TOKEN')
        frontend_url = 'https://paired-key-vault.demo.silencelaboratories.com'
        orchestrator_url = 'https://browserintent-mpc-orchestrator.demo.silencelaboratories.com'
        
        if not agent_token:
            # Generate a UUID for the agent token
            agent_token = str(uuid.uuid4())
        
        self.agent_token = agent_token
        self.frontend_url = frontend_url
        self.orchestrator_url = orchestrator_url
        self.sl_account = None
        self._is_registered = False
    
    def _check_registration(self):
        """Check if agent is registered, if not, redirect to registration URL."""
        if self._is_registered:
            return True
        
        # Check if agent is already registered with the API
        if self._is_agent_registered():
            self._is_registered = True
            return True
        
        # If not registered, open registration page
        registration_url = f"{self.frontend_url}/agent-register?agentToken={self.agent_token}"
        webbrowser.open(registration_url)
        
        print("🔗 Registration page opened. Please complete registration in your browser...")
        
        # Poll for registration completion
        max_wait_time = 300  # 5 minutes
        poll_interval = 2    # Check every 2 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            if self._is_agent_registered():
                self._is_registered = True
                return True
            time.sleep(poll_interval)
        
        raise Exception("Registration timeout!")
    
    def _is_agent_registered(self) -> bool:
        """Check if agent is registered."""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/api/agent-status",
                json={"agentToken": self.agent_token},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('valid', False)
        except Exception as e:
            logging.debug(f"Could not check registration status: {str(e)}")
        return False
    
    def sign_payment(self, requirements: x402PaymentRequiredResponse) -> PaymentPayload:
        """
        Signs a payment requirement using SLAccount.
        """
        # First check if agent is registered
        self._check_registration()
        
        if not self.sl_account:
            # Initialize SL account after registration
            try:
                self.sl_account = SLAccount(self.agent_token, self.orchestrator_url)
                self._is_registered = True
                logging.info(f"SL account initialized successfully with wallet: {self.sl_account.address}")
            except ConnectionError as e:
                logging.error(f"Failed to connect to orchestrator: {str(e)}")
                raise Exception(f"Cannot connect to MPC orchestrator. Please check if the service is running: {str(e)}")
            except ValueError as e:
                logging.error(f"Agent authentication failed: {str(e)}")
                raise Exception(f"Agent authentication failed. Please complete registration first: {str(e)}")
            except Exception as e:
                logging.error(f"Unexpected error initializing SL account: {str(e)}")
                raise Exception(f"Failed to initialize SL account: {str(e)}")
        
        payment_option = requirements.accepts[0]
        
        # Create message to sign (same as MockLocalWallet)
        message_to_sign = f"""Chain ID: {payment_option.network}
Contract: {payment_option.asset}
User: {self.sl_account.address}
Receiver: {payment_option.pay_to}
Amount: {payment_option.max_amount_required}
"""
        
        # Sign the message using SL account (same pattern as MockLocalWallet)
        # This will trigger the phone approval flow via orchestrator
        signable_message = encode_defunct(text=message_to_sign)
        
        
        
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(signable_message.body)
        message_hash = keccak_hash.hexdigest()
        
        signature = self.sl_account.sign_message(
            message_hash,  # 32-byte keccak256 hash
            payment_option.pay_to,
            payment_option.max_amount_required,
            payment_option.network
        )

        authorization_payload = {
            "from": self.sl_account.address,
            "to": payment_option.pay_to,
            "value": payment_option.max_amount_required,
            "validAfter": str(int(time.time())),
            "validBefore": str(
                int(time.time()) + payment_option.max_timeout_seconds
            ),
            "nonce": f"0x{uuid.uuid4().hex}",
            "extra": {"message": message_to_sign},
        }

        final_payload = {
            "authorization": authorization_payload,
            "signature": signature, 
        }

        return PaymentPayload(
            x402Version=1,
            scheme=payment_option.scheme,
            network=payment_option.network,
            payload=final_payload,
        )
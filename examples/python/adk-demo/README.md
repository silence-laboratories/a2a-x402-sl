# ADK x402 Payment Protocol Demo

A complete example demonstrating payments using the A2A protocol with Silence Laboratories MPC wallet integration.

The demo consists of two main components:
1.  A **Client Agent** that acts as an orchestrator, delegating tasks and handling the user-facing interaction.
2.  A **Merchant Server** that hosts a specialized agent capable of selling items and processing payments using the x402 protocol.

The reusable, core logic for the x402 protocol is encapsulated in the `x402_a2a` Python library, located in the `python/` directory of the parent repository.

## How to Run the Demo

### Prerequisites
- Python 3.13+
- `uv` (for environment and package management)
- Google API key (you can create one [here](https://ai.google.dev/gemini-api/docs/api-key))
- **Silence Laboratories MPC Wallet** (for SLWallet)
  - You need to create an wallet on the [Silence Laboratories MPC Wallet](https://paired-key-vault.demo.silencelaboratories.com) and setup a wallet,Setup instructions are [here](https://shadowed-grapple-8a1.notion.site/Browser-Intent-S-L-Wallet-Using-Duo-sdk-271fe2c2b4bd8067b7b2cb3e20308eb1).
- **Note**: SLWallet currently only works with mock facilitator (`USE_MOCK_FACILITATOR=true`)

### 1. Setup the Environment
First, sync the virtual environment to install all necessary dependencies, including the local `x402_a2a` library in editable mode.

Run this command from the root of the `a2a-x402` repository:
```bash
uv sync --directory=examples/python/adk-demo
```

Set your Google API key as an environment variable:

> **Warning:** Do not hardcode or commit your API key. The commands below set the variable for the current session only. For persistence, add the command to your shell's startup file (e.g., `~/.bashrc`, `~/.zshrc`).

*   **Linux/macOS:**
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```
*   **Windows (Command Prompt):**
    ```cmd
    set GOOGLE_API_KEY=your_api_key_here
    ```
*   **Windows (PowerShell):**
    ```powershell
    $env:GOOGLE_API_KEY="your_api_key_here"
    ```

### 2. Start the Merchant Agent Server
The merchant server hosts the agent that sells products.

Run this command from the root of the `a2a-x402` repository:
```bash
uv --directory=examples/python/adk-demo run server
```
You should see logs indicating the server is running, typically on `localhost:10000`.

### 3. Start the Client Agent & Web UI
The client agent is an orchestrator that communicates with the merchant. The ADK provides a web interface to interact with it.

Run this command from the root of the `a2a-x402` repository:
```bash
uv --directory=examples/python/adk-demo run adk web --port=8000
```
This will start the ADK web server, usually on `localhost:8000`. Open this URL in your browser to interact with the client agent and start the purchase flow.

### 4. Try the Payment Demo
Once both servers are running and you've navigated to the web UI, you can test the x402 payment flow by selecting the `client_agent` and asking about purchasing an item such as "I want to buy a nike shoes". The client agent will discover available merchants, request payment details, and guide you through the purchase process.

## How It Works
This demo uses the Silence Laboratories MPC wallet to provide secure transaction signing without exposing private keys. The system consists of:

1. **Client Agent** - Orchestrates the payment flow using SLWallet
2. **Server Agent** - Processes payments via x402 protocol
3. **MPC Infrastructure** - Manages secure signing through orchestrator service
4. **MPC Wallet's Phone App** - User's mobile app for transaction approval via push notifications

## Payment Flow

1. **User Request**: Client requests to buy an item (e.g., "I want to buy a nike shoes")

2. **Payment Required**: Server responds with x402 payment-required message containing:
   - Payment amount and currency
   - Receiver address
   - Chain ID and contract details

3. **Agent Registration**: If not already registered, SLWallet automatically:
   - Opens browser to registration page
   - Waits for user to complete agent registration
   - Links agent token to user's MPC wallet

4. **Sign Request**: SLWallet creates signature request and send request to SL Wallet's Phone App:
   - Message hash to sign
   - Payment details (amount, receiver, chain)
   - Agent token

5. **Phone Approval**: MPC infrastructure:
   - Sends push notification to user's registered phone
   - User reviews transaction details on phone
   - User approves or rejects the transaction

6. **Signed Response**: MPC orchestrator returns signed transaction data to SLWallet

7. **Payment Submitted**: Client sends signed payment payload back to server

8. **Payment Confirmed**: Server verifies signature and completes the purchase

This flow ensures secure payments without requiring the agent to handle private keys directly, while maintaining user control through phone-based approval.

## Pluggable Components

A key design goal of this demo is to show how core components can be swapped out with real implementations.

### Wallet
The `ClientAgent` does not handle signing directly. Instead, it depends on a `Wallet` interface (`wallet.py`). This makes the signing mechanism fully pluggable.

The demo includes two wallet implementations:

- **`MockLocalWallet`**: Signs transactions using a hardcoded private key (for testing only)
- **`SLWallet`**: Uses Silence Laboratories MPC infrastructure for secure signing(for testing only)

**Wallet Selection**: Control which wallet to use with the `USE_MOCK_WALLET` environment variable:
- `USE_MOCK_WALLET=true`: Uses `MockLocalWallet`
- `USE_MOCK_WALLET=false` or unset: Uses `SLWallet` (default)

**SLWallet Features**:
- Agent registration with SL wallet orchestrator
- Phone-based approval for transactions
- Secure MPC signing without exposing private keys
- Automatic browser registration flow
# Browser-Intent S;L Wallet Demo




## Deployment URLs

Frontend: https://paired-key-vault.demo.silencelaboratories.com/login

Mobile App: [Download APK](https://drive.google.com/file/d/1ekCmcyQXK3BErL6nJ_BoyQpu-wk22yum/view)



## Step-by-Step Demo Guide

### Step 1: Register on the Frontend

**Objective**: Create your account on the web application.

1. Navigate to the [Frontend URL](https://paired-key-vault.demo.silencelaboratories.com/login)
2. Click the **Login/Sign Up** button
3. Enter your email address and create a secure password
4. Complete the registration process

> **Note**: Remember your credentials, you'll need them for the mobile app.

---

### Step 2: Install the Mobile App

**Objective**: Set up the companion mobile application.

1. On your Android device, download the APK from the [App Build link](https://drive.google.com/file/d/1ekCmcyQXK3BErL6nJ_BoyQpu-wk22yum/view)
2. Install the application
3. Open the app and sign in using the same email and password from Step 1

---

### Step 3: Pair Your Wallet

**Objective**: Create and link a new Sepolia wallet between your web and mobile apps.

#### On the Web App:
1. After logging in, click **Start Pairing**
2. A QR code and JSON string will be displayed

#### On Your Phone:
1. Tap **Create New Wallet**
2. Choose one of the following methods:
   - **Scan the QR code** displayed on the web app, OR
   - **Copy and paste the JSON string** from the web app

#### Confirmation:
- A new **Sepolia wallet** will be created
- You'll see the **Public Key** and **Wallet Address** on both devices
- **Pairing complete!** Your wallet is now ready for transactions

---

### Step 4: Create and Sign a Transaction

**Objective**: Send a test transaction with phone-based approval.

#### Initiate Transaction (Web):
1. On the web app, click **Create Transaction**
2. Fill in the transaction details:
   - **Recipient Address**: The destination wallet address
   - **Value**: Amount to send (in testnet tokens)
   - **Description**: Optional note about the transaction
3. Click **Create Transaction**

#### Approve Transaction (Phone):
1. You'll receive a **transaction alert** on your phone
2. Review the transaction details carefully:
   - Recipient address
   - Amount
   - Description
3. Choose to **Approve** or **Reject** the transaction

#### Check Transaction Details (Web):
1. After approval, return to the web app
2. Click **Check Transaction** to fetch the transaction status from the server
3. **Transaction completed!**


---

### Step 5: Multi-Wallet Support (Optional)

**Objective**: Manage multiple wallets with the same account.

You can create and manage multiple wallets using the same credentials.

#### On the Web App:
- Navigate to **Manage Wallets**
- View all your paired wallets
- Create additional wallets as needed

#### On the Phone:
- All your wallets appear under the **Home** tab
- Switch between wallets easily

---

### Step 6: View Transaction History

**Objective**: Review your transaction activity.

#### Transaction History Features:
- Both the **web app** and **mobile app** display transaction history
- View all **Approved** and **Rejected** transactions
- On the phone, access the history via the **Transactions** tab


## Architecture Overview

The demo system consists of three main components:

1. **Frontend Web App**: User interface for wallet management and transaction creation
2. **Mobile App**: Secure signing device with push notification support
3. **MPC Orchestrator**: Handles secure communication between Browser and Mobile.

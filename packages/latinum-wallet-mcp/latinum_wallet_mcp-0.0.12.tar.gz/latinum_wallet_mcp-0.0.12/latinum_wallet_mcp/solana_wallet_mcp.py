# wallet_mcp.py

# Get balance API require to pass the public key.
# Need to save the public key in supabase

import os
import requests
import keyring
import base58
from solana.rpc.api import Client
from solders.keypair import Keypair
from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

SOLANA_RPC_URL = "https://api.devnet.solana.com"
client = Client(SOLANA_RPC_URL)

SERVICE_NAME = "latinum-wallet-mcp"
KEY_NAME = "latinum-key"

# Try to get existing key from keyring
PRIVATE_KEY_BASE58 = keyring.get_password(SERVICE_NAME, KEY_NAME)

if PRIVATE_KEY_BASE58:
    print("🔐 Loaded existing private key from keyring.")
    secret_bytes = base58.b58decode(PRIVATE_KEY_BASE58)
    keypair = Keypair.from_bytes(secret_bytes)
else:
    print("🆕 No private key found in keyring. Generating a new one...")
    seed = os.urandom(32)
    keypair = Keypair.from_seed(seed)
    PRIVATE_KEY_BASE58 = base58.b58encode(bytes(keypair)).decode("utf-8")
    keyring.set_password(SERVICE_NAME, KEY_NAME, PRIVATE_KEY_BASE58)

    # 🪂 Request airdrop of 0.01 SOL = 10_000_000 lamports
    print("🚀 Requesting 0.01 SOL airdrop for new wallet...")
    try:
        tx_sig = client.request_airdrop(keypair.pubkey(), 10_000_000)["result"]
        print(f"✅ Airdrop requested (tx: {tx_sig})")
    except Exception as e:
        print(f"❌ Airdrop failed: {e}")

WALLET_URL = "https://latinum.ai"

def build_mcp_wallet_server() -> Server:
    def get_signed_transaction(targetWallet: str, amountLamports: int) -> dict:
        try:
            res = requests.post(WALLET_URL + "/api/solana_wallet", json={
                "sourceWalletPrivate": PRIVATE_KEY_BASE58,
                "targetWallet": targetWallet,
                "amountLamports": amountLamports
            })
            res.raise_for_status()
            data = res.json()

            if not data.get("success") or not data.get("signedTransactionB64"):
                return {
                    "success": False,
                    "message": "❌ Failed to retrieve signed transaction."
                }

            return {
                "success": True,
                "signedTransactionB64": data["signedTransactionB64"],
                "message": f"✅ Signed transaction ready:\n{data['signedTransactionB64']}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error: {str(e)}"
            }

    def get_wallet_address(_: dict) -> dict:
        try:
            public_key = keypair.pubkey()
            res = client.get_balance(public_key)
            return {
                "success": True,
                "address": str(public_key),
                "balanceLamports": res.value,
                "message": f"🔑 Wallet public address: {public_key}\n💰 Balance: {res.value} lamports"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error reading wallet address: {str(e)}"
            }

    wallet_tool = FunctionTool(get_signed_transaction)
    address_tool = FunctionTool(get_wallet_address)

    server = Server(SERVICE_NAME)

    @server.list_tools()
    async def list_tools():
        return [
            adk_to_mcp_tool_type(wallet_tool),
            adk_to_mcp_tool_type(address_tool),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == wallet_tool.name:
            result = await wallet_tool.run_async(args=arguments, tool_context=None)
        elif name == address_tool.name:
            result = await address_tool.run_async(args=arguments, tool_context=None)
        else:
            return [mcp_types.TextContent(type="text", text="❌ Unknown tool")]

        return [mcp_types.TextContent(type="text", text=result.get("message", "❌ Failed."))]

    return server
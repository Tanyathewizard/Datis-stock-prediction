"""
blockchain/web3_handler.py
──────────────────────────
Python interface to the DATIS smart contract via Web3.py.

Works in three modes:
  1. MOCK mode   – no real blockchain needed (default, great for development/testing)
  2. LOCAL mode  – connects to a local Ganache / Hardhat node (http://127.0.0.1:8545)
  3. TESTNET mode – connects to Sepolia / Goerli via Infura or Alchemy RPC URL

Set environment variables to enable real blockchain:
  DATIS_WEB3_MODE         = "local" | "testnet"  (default: "mock")
  DATIS_RPC_URL           = "http://127.0.0.1:8545" or Infura/Alchemy URL
  DATIS_CONTRACT_ADDRESS  = deployed contract address (0x...)
  DATIS_PRIVATE_KEY       = your wallet private key (never commit this!)
"""

import os
import json
import time
import uuid
import logging
from typing import Optional

logger = logging.getLogger("datis.web3")

# ── Try importing web3; fall back gracefully if not installed ────────────────
try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger.warning("web3 package not installed – running in MOCK mode only.")

# ── Contract ABI (matches contract.sol) ─────────────────────────────────────
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string",  "name": "symbol",             "type": "string"},
            {"internalType": "string",  "name": "prediction",         "type": "string"},
            {"internalType": "uint8",   "name": "confidence",         "type": "uint8"},
            {"internalType": "int256",  "name": "priceAtPrediction",  "type": "int256"},
        ],
        "name": "storePrediction",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "tokenId",            "type": "uint256"},
            {"internalType": "string",  "name": "actualResult",       "type": "string"},
            {"internalType": "int256",  "name": "priceAtResolution",  "type": "int256"},
        ],
        "name": "updateActualResult",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "getPrediction",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "tokenId",            "type": "uint256"},
                    {"internalType": "string",  "name": "symbol",             "type": "string"},
                    {"internalType": "string",  "name": "prediction",         "type": "string"},
                    {"internalType": "uint8",   "name": "confidence",         "type": "uint8"},
                    {"internalType": "uint256", "name": "timestamp",          "type": "uint256"},
                    {"internalType": "int256",  "name": "priceAtPrediction",  "type": "int256"},
                    {"internalType": "string",  "name": "actualResult",       "type": "string"},
                    {"internalType": "int256",  "name": "priceAtResolution",  "type": "int256"},
                    {"internalType": "bool",    "name": "resolved",           "type": "bool"},
                    {"internalType": "address", "name": "submitter",          "type": "address"},
                ],
                "internalType": "struct DatisPredictions.Prediction",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalPredictions",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "symbol", "type": "string"}],
        "name": "getTokensBySymbol",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  Mock In-Memory Store (used when WEB3_MODE=mock or web3 not installed)
# ─────────────────────────────────────────────────────────────────────────────

_mock_store: dict[str, dict] = {}   # token_id → prediction dict


def _mock_token_id() -> str:
    """Generate a deterministic-looking mock token id."""
    return str(uuid.uuid4().int)[:12]


# ─────────────────────────────────────────────────────────────────────────────
#  Web3 Connection
# ─────────────────────────────────────────────────────────────────────────────

def _get_web3() -> Optional["Web3"]:
    """Return a connected Web3 instance, or None if unavailable."""
    if not WEB3_AVAILABLE:
        return None
    rpc_url = os.getenv("DATIS_RPC_URL", "http://127.0.0.1:8545")
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
        # Inject PoA middleware for Goerli / Sepolia / Polygon
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if w3.is_connected():
            logger.info(f"Web3 connected → {rpc_url}")
            return w3
        logger.warning(f"Web3 provider not reachable at {rpc_url}. Falling back to MOCK.")
        return None
    except Exception as exc:
        logger.warning(f"Web3 connection error: {exc}. Falling back to MOCK.")
        return None


def _get_contract(w3: "Web3"):
    """Return the deployed contract instance."""
    address = os.getenv("DATIS_CONTRACT_ADDRESS", "")
    if not address:
        raise ValueError(
            "DATIS_CONTRACT_ADDRESS env var not set. "
            "Deploy contract.sol and set the address."
        )
    checksum = Web3.to_checksum_address(address)
    return w3.eth.contract(address=checksum, abi=CONTRACT_ABI)


def _build_and_send(w3: "Web3", fn) -> str:
    """Sign and broadcast a transaction. Returns the tx hash."""
    private_key = os.getenv("DATIS_PRIVATE_KEY", "")
    if not private_key:
        raise ValueError("DATIS_PRIVATE_KEY env var not set.")

    account = w3.eth.account.from_key(private_key)
    nonce    = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    tx = fn.build_transaction({
        "from":     account.address,
        "nonce":    nonce,
        "gasPrice": gas_price,
        "gas":      300_000,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def connect_wallet() -> dict:
    """
    Return wallet/chain info.
    In MOCK mode returns a simulated wallet address.
    """
    mode = os.getenv("DATIS_WEB3_MODE", "mock").lower()
    if mode == "mock" or not WEB3_AVAILABLE:
        return {
            "mode":    "mock",
            "address": "0xMOCK_WALLET_" + uuid.uuid4().hex[:8].upper(),
            "chain":   "mock-testnet",
            "status":  "connected (mock)",
        }

    w3 = _get_web3()
    if not w3:
        return {"mode": "mock", "status": "web3 unavailable – mock mode active"}

    private_key = os.getenv("DATIS_PRIVATE_KEY", "")
    if not private_key:
        return {"mode": "read-only", "status": "no private key – read-only mode"}

    account = w3.eth.account.from_key(private_key)
    balance = w3.eth.get_balance(account.address)
    return {
        "mode":    mode,
        "address": account.address,
        "balance_eth": float(Web3.from_wei(balance, "ether")),
        "chain_id": w3.eth.chain_id,
        "status":  "connected",
    }


def send_prediction_to_chain(
    symbol: str,
    prediction: str,
    confidence: int,
    price: float,
) -> dict:
    """
    Store a prediction on-chain (or in mock store).

    Returns a dict with:
      token_id   – unique identifier for this prediction NFT concept
      tx_hash    – transaction hash (real or simulated)
      mode       – "mock" | "live"
    """
    mode = os.getenv("DATIS_WEB3_MODE", "mock").lower()
    price_int = int(price * 100)  # store as integer cents

    # ── Mock path ──────────────────────────────────────────────────────────
    if mode == "mock" or not WEB3_AVAILABLE:
        token_id = _mock_token_id()
        _mock_store[token_id] = {
            "token_id":           token_id,
            "symbol":             symbol.upper(),
            "prediction":         prediction,
            "confidence":         confidence,
            "timestamp":          int(time.time()),
            "price_at_prediction": price,
            "actual_result":      "PENDING",
            "price_at_resolution": None,
            "resolved":           False,
            "submitter":          "0xMOCK",
            "tx_hash":            "0xMOCK_TX_" + uuid.uuid4().hex[:16],
        }
        return {
            "token_id": token_id,
            "tx_hash":  _mock_store[token_id]["tx_hash"],
            "mode":     "mock",
            "status":   "stored (mock)",
        }

    # ── Live path ──────────────────────────────────────────────────────────
    w3       = _get_web3()
    contract = _get_contract(w3)
    fn       = contract.functions.storePrediction(
        symbol.upper(), prediction, confidence, price_int
    )
    tx_hash = _build_and_send(w3, fn)

    # Wait for receipt to get the token id from event logs
    receipt  = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    logs     = contract.events.PredictionStored().process_receipt(receipt)
    token_id = str(logs[0]["args"]["tokenId"]) if logs else "unknown"

    return {
        "token_id": token_id,
        "tx_hash":  tx_hash,
        "mode":     "live",
        "status":   "stored on-chain",
        "block":    receipt.blockNumber,
    }


def update_result_on_chain(
    token_id: str,
    actual_result: str,
    resolution_price: float,
) -> dict:
    """
    Update the outcome of a stored prediction.
    actual_result should be "CORRECT" or "INCORRECT".
    """
    mode = os.getenv("DATIS_WEB3_MODE", "mock").lower()
    price_int = int(resolution_price * 100)

    # ── Mock path ──────────────────────────────────────────────────────────
    if mode == "mock" or not WEB3_AVAILABLE:
        if token_id not in _mock_store:
            return {"error": f"Token {token_id} not found in mock store"}
        _mock_store[token_id]["actual_result"]       = actual_result
        _mock_store[token_id]["price_at_resolution"] = resolution_price
        _mock_store[token_id]["resolved"]            = True
        return {
            "token_id":      token_id,
            "actual_result": actual_result,
            "tx_hash":       "0xMOCK_UPDATE_" + uuid.uuid4().hex[:16],
            "mode":          "mock",
            "status":        "updated (mock)",
        }

    # ── Live path ──────────────────────────────────────────────────────────
    w3       = _get_web3()
    contract = _get_contract(w3)
    fn       = contract.functions.updateActualResult(
        int(token_id), actual_result, price_int
    )
    tx_hash = _build_and_send(w3, fn)
    receipt  = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    return {
        "token_id":      token_id,
        "actual_result": actual_result,
        "tx_hash":       tx_hash,
        "mode":          "live",
        "status":        "updated on-chain",
        "block":         receipt.blockNumber,
    }


def read_prediction_history() -> list[dict]:
    """
    Return all stored predictions (from mock store or on-chain).
    """
    mode = os.getenv("DATIS_WEB3_MODE", "mock").lower()

    if mode == "mock" or not WEB3_AVAILABLE:
        return list(_mock_store.values())

    w3       = _get_web3()
    contract = _get_contract(w3)
    total    = contract.functions.totalPredictions().call()
    results  = []
    for i in range(total):
        p = contract.functions.getPrediction(i).call()
        results.append({
            "token_id":            str(p[0]),
            "symbol":              p[1],
            "prediction":          p[2],
            "confidence":          p[3],
            "timestamp":           p[4],
            "price_at_prediction": p[5] / 100,
            "actual_result":       p[6],
            "price_at_resolution": p[7] / 100 if p[8] else None,
            "resolved":            p[8],
            "submitter":           p[9],
        })
    return results


def get_prediction_by_token(token_id: str) -> Optional[dict]:
    """Fetch a single prediction by its token id."""
    mode = os.getenv("DATIS_WEB3_MODE", "mock").lower()

    if mode == "mock" or not WEB3_AVAILABLE:
        return _mock_store.get(token_id)

    w3       = _get_web3()
    contract = _get_contract(w3)
    try:
        p = contract.functions.getPrediction(int(token_id)).call()
        return {
            "token_id":            str(p[0]),
            "symbol":              p[1],
            "prediction":          p[2],
            "confidence":          p[3],
            "timestamp":           p[4],
            "price_at_prediction": p[5] / 100,
            "actual_result":       p[6],
            "price_at_resolution": p[7] / 100 if p[8] else None,
            "resolved":            p[8],
            "submitter":           p[9],
        }
    except Exception:
        return None

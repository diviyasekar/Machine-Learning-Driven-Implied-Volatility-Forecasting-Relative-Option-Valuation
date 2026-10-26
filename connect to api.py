# ============================================================
# Upstox API v2 - Option Chain Fetcher & Connection Test
# Real-Time Implied Volatility Forecasting & Relative Valuation
# ============================================================

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env", override=True)

UPSTOX_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")


def fetch_option_chain(expiry_date="2026-10-19", instrument_key="NSE_INDEX|Nifty 50"):
    """
    Fetch NIFTY 50 option-chain data for a specific expiry date from Upstox API v2.
    
    Parameters:
    -----------
    expiry_date : str
        Target contract expiry in 'YYYY-MM-DD' format (e.g., '2026-10-19').
    instrument_key : str
        Underlying instrument key (default: 'NSE_INDEX|Nifty 50').
        
    Returns:
    --------
    list[dict]: List of option contract data for both CE and PE strikes.
    """
    if not UPSTOX_TOKEN:
        raise ValueError(
            "UPSTOX_ACCESS_TOKEN not found! Please create a .env file based on .env.example."
        )

    url = "https://api.upstox.com/v2/option/chain"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {UPSTOX_TOKEN}"
    }

    params = {
        "instrument_key": instrument_key,
        "expiry_date": expiry_date
    }

    print(f"Connecting to Upstox API for {instrument_key} (Expiry: {expiry_date})...")
    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "success":
        raise RuntimeError(f"Upstox API returned non-success status: {payload}")

    return payload.get("data", [])


if __name__ == "__main__":
    print("=" * 60)
    print("UPSTOX OPTION CHAIN API CONNECTION TEST")
    print("=" * 60)

    if not UPSTOX_TOKEN:
        print("[!] No UPSTOX_ACCESS_TOKEN detected in environment or .env file.")
        print("[i] Copy .env.example to .env and set your token to enable live streaming.")
        sys.exit(0)

    try:
        contracts = fetch_option_chain()
        print(f"[✓] Connection successful! Retrieved {len(contracts)} contracts.")
        if contracts:
            sample = contracts[0]
            print(f"[i] Sample strike: {sample.get('strike_price')} | Spot: {sample.get('underlying_spot_price')}")
    except Exception as e:
        print(f"[x] Error querying Upstox API: {e}")

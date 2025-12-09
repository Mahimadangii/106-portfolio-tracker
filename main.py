"""
Portfolio Tracker App
Author: Mahima Dangi (Roll No. 106) 

Description:
Tracks cryptocurrency portfolio value in real-time using CoinGecko's API.
"""

import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment settings
load_dotenv()
CURRENCY = os.getenv("CURRENCY", "usd").lower()

# Mapping crypto symbols to CoinGecko API coin IDs
COIN_ID_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "ltc": "litecoin",
    "doge": "dogecoin",
    "xrp": "ripple",
    "ada": "cardano",
    "sol": "solana",
    "bnb": "binancecoin",
    "matic": "matic-network"
}


# CLASS: CryptoAsset -> Represents single crypto entry
class CryptoAsset:
    def __init__(self, symbol: str, amount: float, coin_id: str):
        self.__symbol = symbol.upper()
        self.__amount = float(amount)
        self.__coin_id = coin_id
        self.__price = None  

    # Getters
    def get_symbol(self):
        return self.__symbol

    def get_amount(self):
        return self.__amount

    def get_coin_id(self):
        return self.__coin_id

    def get_price(self):
        return self.__price

    # Setter
    def set_price(self, price: float):
        try:
            self.__price = float(price)
        except (TypeError, ValueError):
            self.__price = None

    # Calculate total value
    def get_total_value(self):
        if self.__price is None:
            return 0.0
        return self.__amount * self.__price

    # Convert to dictionary for saving to JSON
    def to_dict(self):
        return {
            "symbol": self.__symbol,
            "amount": self.__amount,
            "price": self.__price if self.__price is not None else "N/A",
            "total_value": self.get_total_value()
        }


# CLASS: PortfolioTracker -> Main logic + API fetch
class PortfolioTracker:
    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

    def __init__(self, currency="usd"):
        self.currency = currency.lower()
        self.assets = []

    def add_asset(self, symbol, amount):
        symbol_lower = symbol.lower()

        if symbol_lower not in COIN_ID_MAP:
            print(f"⚠ Unknown cryptocurrency symbol: {symbol}")
            return

        coin_id = COIN_ID_MAP[symbol_lower]
        asset = CryptoAsset(symbol, amount, coin_id)
        self.assets.append(asset)

        print(f"✔ Added {amount} {symbol.upper()} to portfolio.")

    def fetch_prices(self):
        if not self.assets:
            print("⚠ No assets added yet.")
            return

        # Build unique comma-separated ids
        ids = ",".join({asset.get_coin_id() for asset in self.assets})

        try:
            response = requests.get(
                self.BASE_URL,
                params={"ids": ids, "vs_currencies": self.currency},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            for asset in self.assets:
                price = data.get(asset.get_coin_id(), {}).get(self.currency)
                if price is not None:
                    asset.set_price(price)
                else:
                    asset.set_price(None)
                    print(f"⚠ Could not fetch price for {asset.get_symbol()}")

        except requests.exceptions.ConnectionError:
            print("❌ No internet connection.")
        except requests.exceptions.HTTPError as err:
            print(f"❌ API request error: {err}")
        except Exception as e:
            print(f"❌ Unknown error: {e}")

    def display(self):
        if not self.assets:
            print("⚠ Portfolio is empty.")
            return 0.0

        cur = self.currency.upper()
        print("\n📊 Portfolio Value Summary")
        print("-" * 70)
        print(f"{'Symbol':<10}{'Amount':<18}{f'Price ({cur})':<18}{'Total ('+cur+')':<18}")
        print("-" * 70)

        total = 0.0

        for asset in self.assets:
            price = asset.get_price()
            row_total = asset.get_total_value()
            total += row_total

            price_display = f"{price:.6f}" if price is not None else "N/A"
            amount_display = f"{asset.get_amount():.6f}"

            print(f"{asset.get_symbol():<10}{amount_display:<18}{price_display:<18}{row_total:<18.6f}")

        print("-" * 70)
        print(f"{'TOTAL PORTFOLIO VALUE:':<40}{total:.6f} {cur}")
        print("-" * 70)

        return total

    def save_snapshot(self):
        filename = f"portfolio_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        snapshot = {
            "currency": self.currency.upper(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assets": [asset.to_dict() for asset in self.assets]
        }

        try:
            with open(filename, "w") as file:
                json.dump(snapshot, file, indent=4)
            print(f"✔ Snapshot saved as {filename}")
        except Exception as e:
            print(f"❌ Failed to save snapshot: {e}")


# MAIN PROGRAM
def main():
    print("📊 Welcome to Portfolio Tracker App\n")

    tracker = PortfolioTracker(currency=CURRENCY)

    while True:
        symbol = input("Enter cryptocurrency (e.g., BTC, ETH) or 'done' to finish: ").strip()

        if symbol.lower() == "done":
            break

        try:
            amount = float(input(f"Enter amount of {symbol.upper()}: ").strip())
            if amount > 0:
                tracker.add_asset(symbol, amount)
            else:
                print("⚠ Amount must be positive.")
        except ValueError:
            print("⚠ Invalid amount entered.")

    print("\n🔄 Fetching live prices...")
    tracker.fetch_prices()

    tracker.display()

    if input("\nSave portfolio snapshot? (y/n): ").lower() == "y":
        tracker.save_snapshot()

    print("\n🎉 Thank you for using Portfolio Tracker!")


if __name__ == "__main__":
    main()

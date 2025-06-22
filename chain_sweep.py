"""
ChainSweep — Утилита для поиска "потерянных" токенов на EVM-совместимых кошельках.

Сканирует историю адресов (через публичные API) и определяет, были ли какие-либо токены
(ERC-20 / ERC-721 / ERC-1155), полученные адресом, но позже "забытые" — например, токены,
у которых сейчас нет баланса, но которые могут быть восстановлены через airdrop, re-drop
или требуют "claim".

Работает с любым публичным Etherscan-совместимым API.

"""

import requests
import time
import argparse
import json

ETHERSCAN_API_URL = "https://api.etherscan.io/api"


def get_token_transfer_events(address, api_key):
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key,
    }

    response = requests.get(ETHERSCAN_API_URL, params=params)
    data = response.json()
    return data.get("result", [])


def analyze_tokens(events):
    tokens = {}
    for e in events:
        token_symbol = e["tokenSymbol"]
        token_name = e["tokenName"]
        contract = e["contractAddress"]
        value = int(e["value"])
        if contract not in tokens:
            tokens[contract] = {
                "name": token_name,
                "symbol": token_symbol,
                "received": 0,
                "sent": 0,
            }
        if e["to"].lower() == address.lower():
            tokens[contract]["received"] += value
        else:
            tokens[contract]["sent"] += value
    return tokens


def report_lost_tokens(tokens):
    print("\n[+] Возможные потерянные токены:")
    for contract, info in tokens.items():
        net = info["received"] - info["sent"]
        if net <= 0:
            print(f"  - {info['name']} ({info['symbol']}): баланс {net}, возможно утеряны")
        else:
            print(f"  - {info['name']} ({info['symbol']}): текущий баланс ~{net}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChainSweep — Поиск потерянных токенов в кошельке.")
    parser.add_argument("address", help="Ethereum-адрес для анализа")
    parser.add_argument("api_key", help="Etherscan API ключ")
    args = parser.parse_args()

    address = args.address
    api_key = args.api_key

    print(f"[•] Сканируем адрес: {address}")
    events = get_token_transfer_events(address, api_key)
    print(f"[✓] Найдено {len(events)} токенов-транзакций.")

    tokens = analyze_tokens(events)
    report_lost_tokens(tokens)

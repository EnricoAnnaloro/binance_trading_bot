#!/bin/bash python3
from http import client
import sys
import config
import argparse
from binance.spot import Spot


accepted_coin_ids = ["BTCEUR", "ETHEUR", "DOGEEUR"]
available_ratio_compared_to_pay = 3


def kill(error_message="Unkown"):
    print("something went wrong")
    print(error_message)
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Define the coin and the " "amount of eur to spend"
    )

    parser.add_argument(
        "--coin",
        required=True,
        type=str,
        choices=accepted_coin_ids,
        help="Name of the coin to buy. " "e.g. BTCEUR, ETHEUR, ...",
    )

    parser.add_argument(
        "--pay",
        required=True,
        type=int,
        choices=[25, 30, 35, 40, 45, 50],
        help="Euros to spend in transaction",
    )

    args = parser.parse_args()
    return args


def retrieve_api_keys():
    api_key = config.API_KEY
    secret_key = config.SECRET_KEY

    return api_key, secret_key


def set_up_client():
    api_key, secret_key = retrieve_api_keys()

    if not api_key or not secret_key:
        kill()

    client = Spot(api_key, secret_key)

    return client


def retrieve_last_price(client, coin_id):
    """
    Function to retrieve the last closed price for a specific coin
    from Binance server.

    Uses the klines function which returns a list of candlestick data
    [
        Open time
        Open
        High
        Low
        Close
        Volume
        Close time
        Quote asset volume
        Number of trades
        Taker buy base asset volume
        Taker buy quote asset volume
        Ignore
    ]

    Input: client (binance.spot.Spot)
           coin_id (str) - e.g. BTCEUR, ETHEUR, ....

    Output: last_price (int) - last minute closed price for coin_id
    """
    klines = client.klines(coin_id, "1m", limit=5)
    return float(klines[-1][4])


if __name__ == "__main__":
    args = parse_args()
    client = set_up_client()

    last_price = retrieve_last_price(client=client, coin_id=args.coin)
    quantity_to_buy = round(args.pay / last_price, 5)

    try:
        print(f"Buying coin: {args.coin}")
        print(f"Last price: {last_price}")
        print(f"Quantity to buy: {quantity_to_buy}")
        transaction = client.new_order_test(
            symbol=args.coin, side="BUY", type="MARKET", quantity=quantity_to_buy
        )
        print(f"Transaction succesful: {transaction}")

    except Exception as e:
        kill(e)

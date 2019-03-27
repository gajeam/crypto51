import datetime
import json
import requests
import config
import csv

from apis.marketcap import MarketCap
from apis.wtm import WTM
from apis.nicehash import NiceHash
from apis.hashstats import HashStats
from libs import common

if __name__ == '__main__':

    with open('data/whitelist.csv') as csvfile:
        whitelist = list(csv.reader(csvfile))[0]

    nh = NiceHash()
    mc = MarketCap(whitelist)
    hashstats = HashStats()
    wtm = WTM(whitelist)
    coins = wtm.get_coin_data()
    allcoins = []
    btc_price = requests.get('https://whattomine.com/coins/1.json').json()['exchange_rate']

    # Iterate through coins on WTM that's not 'lagging'
    for coin in coins:
        coin_id = coins[coin]['id']
        coin_name = coins[coin]['name']
        coin_symbol = coins[coin]['symbol']
        coin_hashrate = coins[coin]['hashrate']
        coin_marketcap = coins[coin]['marketcap']
        coin_algorithm = coins[coin]['algorithm']
        coin_exchange_rate = coins[coin]['exchange_rate']

        # Certain coins have invalid hash rates or other values, so we skip them
        if coin_symbol in config.coin_blacklist:
            continue

        # Get mining details from WTM
        # Details are: hash_rate, algorithm
        cost = nh.get_cost_global(coin_algorithm, coin_hashrate)
        nh_hash_ratio = nh.get_hash_percentage(coin_algorithm, coin_hashrate);
        coin_algo_index = nh._get_algorithm_index(coin_algorithm)
        # Skip coins that NiceHash doesn't support
        if cost is None or cost == '?':
            print("!!! Skipping {} because of {}".format(coin_symbol, coin_algorithm))
            continue

        # TODO: Add this to the coin blacklist.
        if coin_name == 'Bitgem':
            continue

        rentable_capacity = nh.get_capacity(coin_algorithm)
        rentable_price_btc = nh.get_algorithm_price(coin_algorithm)

        coin_algorithm_type = mc.get_algorithm_type(coin_algorithm)
        coin_market_cap_order = mc.get_coin_market_cap_order(coin_name)
        coin_total_wattage = mc.get_total_wattage(coin_algorithm, coin_hashrate)

        coin_mining_sd = hashstats.get_mining_shift_relative_sd(coin_algo_index)
        coin_mining_daily_mean = hashstats.get_mining_daily_mean(coin_algo_index)
        allcoins.append({
            'symbol': coin_symbol,
            'name': coin_name,
            'algorithm': coin_algorithm,
            'algo_index': coin_algo_index,
            'algo_type': coin_algorithm_type,
            'market_cap': coin_marketcap,
            'market_cap_pretty': common.get_pretty_money(coin_marketcap),
            'market_cap_order': coin_market_cap_order,
            'hash_rate': coin_hashrate,
            'hash_rate_pretty': common.get_pretty_hash_rate(coin_hashrate),
            'total_wattage': coin_total_wattage,
            'mining_daily_avg': coin_mining_daily_mean,
            'mining_sd': coin_mining_sd,
            # 'network_vs_rentable_ratio': nh_hash_ratio,
            # 'rentable_capacity': rentable_capacity,
            # 'rentable_capacity_pretty': common.get_pretty_hash_rate(rentable_capacity),
            # 'rentable_price_btc': rentable_price_btc,
            # 'rentable_price_units': nh.get_units(coin_algorithm),
            # 'rentable_price_usd_hour': '${:,.2f}'.format(rentable_price_btc * btc_price / 24.0),
            'attack_hourly_cost': cost * btc_price / 24.0 if cost != 0 else '?',
            'attack_hourly_cost_pretty': '${:,.0f}'.format(cost * btc_price / 24.0) if cost != 0 else '?'
        })

    # Sort by rank
    results = {
        'last_updated': datetime.datetime.utcnow().isoformat(),
        'coins': sorted(allcoins, key=lambda k: k['market_cap'], reverse=True)
    }

    with open('../dist/coins.json', 'w') as f:
        json.dump(results, f)

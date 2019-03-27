import json

class MarketCap:
    """Get info on the market cap order from CoinMarketCap
    In the future, this can be hooked into the CoinMarketCap API
    https://coinmarketcap.com/
    """
    def __init__(self, coin_list):
        with open('data/coindata.json', 'r') as f:                
            data = json.load(f)
            self._coin_market_caps = data['coins']
            self._algorithm_types = data['algorithms']
            for coin in coin_list:
                if self._coin_market_caps.get(coin) is None:
                    raise AssertionError('Missing market cap data for {}'.format(coin))

    def get_coin_market_cap_order(self, coin):
        return self._coin_market_caps[coin]['marketcap_order']

    def get_total_wattage(self, algorithm, hashrate):
        watts_used = self._algorithm_types[algorithm]['watts_used']
        miner_hashing = self._algorithm_types[algorithm]['miner_hashing']
        return (hashrate * watts_used)/miner_hashing

    def get_algorithm_type(self, algorithm):
        return self._algorithm_types[algorithm]['type']
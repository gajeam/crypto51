import requests
import json
import pandas

from statistics import mean 
from scipy.stats import variation 

class HashStats:
    def __init__(self):
        # Snapshots every 5 minutes, and we want to average per day
        self._coin_data = {}

    def get_mining_shift_relative_sd(self, algo_index):
        return self._get_data_for_key("relative_sd", algo_index)

    def get_mining_daily_mean(self, algo_index):
        return self._get_data_for_key("daily_mean", algo_index)

    def _get_data_for_key(self, key, algo_index):
        if self._coin_data.get(algo_index) is None:
            self._get_algorithm_data(algo_index)
        return self._coin_data[algo_index][key]

    def _get_algorithm_data(self, algo_index):
        print('Looking up algorithm #{}...'.format(algo_index))
        data  = requests.get('https://api.nicehash.com/stats?algo={}'.format(algo_index))

        str_data = data.content.decode('utf-8')
        str_data = str_data.replace('null([', '')
        str_data = str_data.replace(']);', '')

        first_split = str_data.split('],')
        hash_values = [s.replace('[', '').split(',')[:2] for s in first_split]
        hash_speeds = [float(b) for [a, b] in hash_values]

        interval = 12 * 24
        days_checked = 90 # @GABE change this to determine the amoutn of days checked

        # Reduce it to be a year's worth of data and average it by day
        hash_speeds = hash_speeds[-(interval * days_checked):]
        daily_avg = [mean(hash_speeds[i * interval:(i+1)* interval]) for i in range(days_checked)]

        algo_dict = {"relative_sd": variation(daily_avg),
                     "daily_mean": mean(daily_avg),
                     "algo_index": algo_index,
                     "days_checked": days_checked}
        self._coin_data[algo_index] = algo_dict     
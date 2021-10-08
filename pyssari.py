# -*- coding: utf-8 -*- #

# Ref:
# https://messari.io/api/docs
# https://data.messari.io/api/v1/assets/yfi/metrics/price/time-series?start=2021-01-01&end=2021-02-01&interval=1d

# ---- imports ---- #
import sys
import requests
import argparse
from collections.abc import MutableMapping
from datetime import datetime, timedelta, date

import numpy as np
import pandas as pd


# ---- constants ---- #
BASE_URL = "https://data.messari.io"
API_KEY = "c71aa245-129e-47e3-8bd8-b693e85bc028"
DATE_FMT = "%Y-%m-%d"
TIMEOUT = 30


# ---- helper/convenience functions ---- #
def all_eq(iterator):
    return len(set(iterator)) <= 1

# Only allows for mutually exclusive keys
def merge_dicts(dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out

def valid_date(date_text):
    try:
        datetime.strptime(date_text, DATE_FMT)
    except:
        return False
    return True
        
def maybe_list(x):
    if hasattr(x, '__len__'): return x
    return [x]

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# ---- Main API wrapper class ---- #
class Pyssari:
    """
    Simple class to interact with Messari's API in Python
    """

    def __init__(self, key=None):
        """
        Initialize the Pyssari class object and instantiate a Messari API session.
        key: API key
        """
        self.key = key
        self.session = requests.Session()
        if self.key:
            self.session.headers.update({'x-messari-api-key': key})

    def _send_message(self, method, endpoint, params=None, data=None):
        """
        Send API request.

        Params
        ------
        method : HTTP method (e.g. [get, post, delete])
        endpoint : Endpoint url
        params : HTTP request parameters
        data : string payload (json) for POST

        Returns
        -------
        JSON response
        """
        url = BASE_URL + endpoint
        response = self.session.request(
            method, url, params=params, data=data, timeout=TIMEOUT
        )
        return response.json()

    def _get(self, endpoint, params=None):
        """
        Fetch API request

        Params
        ------
        endpoint : Endpoint url
        params : HTTP request parameters

        Returns
        -------
        JSON response
        """
        return self._send_message('GET', endpoint, params=params)

    def get_asset_timeseries(self, asset_key, metric_id, **params):
        """
        Retrieve historical timeseries data for an asset by key.

        Endpoint : GET /api/v1/assets/{assetKey}/metrics/{metric_id}/time-series

        asset_key : This "key" can be the asset's ID (unique), slug (unique),
                or symbol (non-unique)
        metric_id : specifies which timeseries will be returned.
        query_params : dict of query parameters to filter the list
        
        Returns: 
        -------
        JSON response
        """
        path = '/api/v1/assets/{}/metrics/{}/time-series'.format(asset_key, metric_id)
        return self._get(path, params=params)

    def get_asset_metrics(self, asset_key, fields=None):
        """
        Get all or any specific number of quantitative metrics for an asset.
        Endpoint: GET /api/v1/assets/{assetKey}/metrics

        Params
        ------
        asset_key : This "key" can be the asset's ID (unique), slug (unique),
                or symbol (non-unique)
        fields : string: pare down the returned fields (comma , separated,
                drill down with a slash /)
        Returns
        -------
        JSON response
        """
        path = '/api/v1/assets/{}/metrics'.format(asset_key)
        return self._get(path, params={'fields': fields})


# ---- High level functions ---- #
def get_asset_price_history(session, 
                            asset_key, 
                            start_date=None, 
                            end_date=None, 
                            columns='close', 
                            interval='1d'):
    """
    Fetch the price history of a specific asset based on id, name, or slug given
    start and end data parameters.

    Params
    ------
    session : instantiated Pyssari API session object.
    asset_key : This "key" can be the asset's ID (unique), slug (unique),
                or symbol (non-unique) 
    start_date : string - date to begin timeseries (e.g. 2020-01-17)
    end_date : string - date to end timeseries (e.g. 2021-10-01)
    columns : string value, must be one of ['open', 'high', 'low', 'close']
    interval : string value for time granularity ['1w', '1d', '4h', '2h', ...]

    Returns
    -------
     Pandas DataFrame 
    """
    # Default to today as end date
    if not end_date:
        end_date = date.today().strftime(DATE_FMT)
    
    # Default to 1 year ago as start date
    if not start_date:
        start_date = (date.today() - timedelta(days=365)).strftime(DATE_FMT)

    # Assert properly formatted start/end dates
    assert valid_date(start_date)
    assert valid_date(end_date)

    # Fetch timeseries and return array of values
    ts = session.get_asset_timeseries(
        asset_key, 'price', columns=columns, interval=interval, 
        start=start_date, end=end_date
    ).get('data').get('values')
    return ts

def get_assets_price_history_pd(session,
                                list_of_assets,
                                start_date,
                                end_date,
                                columns='close',
                                interval='1d'):
    """
    Get price history from a list of assets as a pandas DataFrame.

    Params
    ------
    session : instantiated Pyssari API session object.
    list_of_assets : list of asset string names, slugs, or ids
    start_date : string - date to begin timeseries (e.g. 2020-01-17)
    end_date : string - date to end timeseries (e.g. 2021-10-01)
    columns : string value, must be one of ['open', 'high', 'low', 'close']
    interval : string value for time granularity ['1w', '1d', '4h', '2h', ...]

    Returns:
    Pandas DataFrame
    """
    # Map over list of asset keys to populate price data from session GET requests
    asset_data = list(
        map(
            lambda key: get_asset_price_history(session,
                key, columns=columns, interval=interval, 
                start_date=start_date, end_date=end_date
            ),
            list_of_assets
        )
    )
    # Extract and format unix time objects for human readability
    time = np.asarray(asset_data[0])[:, 0]
    dates = list(
        map(
            lambda t: datetime.fromtimestamp(
                int(t/1000)).strftime(DATE_FMT), # convert to sec for datetime parsing
            time
        )
    )
    # Extract price data and create dict 
    prep_data = list(
        map(
            lambda x:{x[0]: np.asarray(x[1])[:, 1]},
            zip(list_of_assets, asset_data)
        )
    )
    # Merge list of dictionaries into 1
    data = merge_dicts(prep_data)
    
    # Ensure assets that do not have full range of price data are padded accordingly
    lens = list(
        map(
            lambda x: len(x), data.values()
        )
    )
    max_len = max(lens)
    if not all_eq(lens):
        data = {
            k: np.concatenate([np.zeros(max_len - len(v)), v]) \
             for k,v in data.items()
        }

    # Create and return pandas dataframe
    return pd.DataFrame(data, index=dates)


def get_assets_metrics_pd(session, 
                          list_of_assets=None, 
                          list_of_metrics=None, 
                          flatten_df=True):
    """
    Fetch all metrics from a list of assets and return as a pandas DataFrame.

    Params
    ------
    list_of_assets: list of asset string names, slugs, or ids
    start_date: string - date to begin timeseries (e.g. 2020-01-17)
    end_date: string - date to end timeseries (e.g. 2021-10-01)
    columns: string value, must be one of ['open', 'high', 'low', 'close']
    interval: string value for time granularity ['1w', '1d', '4h', '2h', ...]

    Returns
    -------
    Pandas DataFrame
    """
    D = {}
    for asset in list_of_assets:
        metrics = session.get_asset_metrics(asset)
        data = metrics['data']

        if flatten_df:
            flattened = flatten(data)
            filtered = {
                k: v for k, v in flattened.items() \
                if v is not None
            }
            d = {
                k: v for k, v in filtered.items() \
                if isinstance(v, int) or isinstance(v, float)
            }
            D[asset] = pd.Series(d)
        else:
            D[asset] = pd.Series(data)
    return pd.DataFrame.from_dict(D)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-a','--assets', nargs='+', help='<Required> Set flag', required=True
    )
    parser.add_argument(
        '-s',
        '--start',
        type=lambda s: str(datetime.strptime(s, '%Y-%m-%d'))[:-9]
    )
    parser.add_argument(
        '-e',
        '--end',
        type=lambda s: str(datetime.strptime(s, '%Y-%m-%d'))[:-9]
    )
    parser.add_argument(
        '-f', '--flatten_results', dest='flatten', action='store_true'
    )
    parser.set_defaults(flatten=True)

    args = parser.parse_args()
    print("Parsed arguments:\n", args)

    session = Pyssari()

    price_history = get_assets_price_history_pd(
        session, args.assets, args.start, args.end
    )
    print("\nPandas DataFrame containing asset price history:\n", price_history)

    assets_metrics = get_assets_metrics_pd(
        session, args.assets, flatten_df=args.flatten
    )
    print("\nPandas Dataframe of ALL Asset Metrics:\n", assets_metrics)


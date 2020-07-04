from datetime import datetime
import os

import requests
import pandas as pd

SOURCE_DICT = {
    '': 'https://covidtracking.com/api/v1/states/pa/current.csv'
}

"""
https://covidtracking.com/api/v1/states/pa/current.csv

"""

DATA_DIR = "/tmp/covid-testing"


def dl_csv_data(state):
    """
    https://covidtracking.com/api
    """
    # this doesn't have county-level testing data
    out_dir = os.path.join(DATA_DIR, 'covidtracking', state)
    now_hour = datetime.utcnow().strftime('%Y-%m-%d:%H')
    out_path = os.path.join(out_dir, f'{now_hour}.daily.csv')
    # update once per hour?
    if os.path.exists(out_path):
        return out_path

    url = f'https://covidtracking.com/api/v1/states/{state}/daily.csv'
    r = requests.get(url)
    assert r.status_code == 200

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with open(out_path, 'w') as ofp:
        ofp.write(r.text)
    return out_path


def set_test_rates(df, window):
    totals = df[['totalTestResultsIncrease', 'positiveIncrease']].rolling(window).sum()
    test_rates = totals['positiveIncrease'] / totals['totalTestResultsIncrease']
    df[f'{window}DayRollingTestRate'] = test_rates


def load_test_df(state):
    csv_path = dl_csv_data(state)
    """
    ['date', 'state', 'positive', 'negative', 'pending',
       'hospitalizedCurrently', 'hospitalizedCumulative', 'inIcuCurrently',
       'inIcuCumulative', 'onVentilatorCurrently', 'onVentilatorCumulative',
       'recovered', 'dataQualityGrade', 'lastUpdateEt', 'dateModified',
       'checkTimeEt', 'death', 'hospitalized', 'dateChecked',
       'totalTestsViral', 'positiveTestsViral', 'negativeTestsViral',
       'positiveCasesViral', 'fips', 'positiveIncrease', 'negativeIncrease',
       'total', 'totalTestResults', 'totalTestResultsIncrease', 'posNeg',
       'deathIncrease', 'hospitalizedIncrease', 'hash', 'commercialScore',
       'negativeRegularScore', 'negativeScore', 'positiveScore', 'score',
       'grade']
    """
    df = pd.read_csv(csv_path)
    # oldest to newest
    df = df.reindex(index=df.index[::-1])
    # index by date.
    df.set_index('date', inplace=True)
    # add rolling averages
    for window in (3, 7, 14):
        set_test_rates(df, window)
    return df


if __name__ == '__main__':
    df = load_test_df('pa')
    stuff = df[['totalTestResultsIncrease', 'positiveIncrease', '2DayRollingTestRate', '7DayRollingTestRate']]
    pass

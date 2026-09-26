
import requests 
import pandas as pd
from datetime import date, timedelta 


def get_rates():

    end_date = date.today()
    start_date = end_date - timedelta(days=14)

    url = f"https://api.frankfurter.app/{start_date}..{end_date}"

    params = {
        'from' : 'USD',
        'to' : 'EUR,GBP,CAD'
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    data = response.json()

    rows = []

    for date_value, currencies in data['rates'].items():

        for currency, rate in currencies.items():

            rows.append({
                'date' : date_value,
                'currency' : currency,
                'rate' : rate
            }) 

    df = pd.DataFrame(rows)

    df['date'] = pd.to_datetime(df['date'])

    df = df.sort_values(['date', 'currency']).reset_index(drop=True)

    return df         

def prepare_rates(rates_df):
    rates_df = rates_df.copy()

    mapping = {
        'EUR' : 'Euro',
        'GBP' : 'British Pound',
        'CAD' : 'Canadian Dollar'
    }


    rates_df['currency_name'] = rates_df['currency'].map(mapping)
    rates_df['year_month'] = rates_df['date'].dt.strftime('%Y-%m') 
    
    result = (
        rates_df[rates_df['rate'] > 0.8]
        [['date', 'year_month', 'currency', 'currency_name', 'rate']]
        .sort_values(['date', 'currency'], ascending = [True,True])

    )

    return result 

def save_rates(df):
    file_path = 'rates.csv'

    df.to_csv('rates.csv', index=False, encoding='utf-8')

    return file_path  

def year_month_rates(df):
    file_paths = []

    for year_month, group in df.groupby("year_month"):
        file_path = f"rates_{year_month}.csv"

        group.to_csv(
            file_path,
            index=False,
            encoding="utf-8"
        )

        file_paths.append(file_path)

    return file_paths



    

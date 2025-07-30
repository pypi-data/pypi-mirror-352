import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from .model import StockFundamentals

class FundamentalData:
    """Main class for retrieving SEC fundamental data"""
    
    def __init__(self, email):
        self.headers = {'User-Agent': email}
        self.company_data = self._fetch_company_index()
    
    def _fetch_company_index(self):
        """Retrieve and process company ticker-CIK mapping"""
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        company_df = pd.DataFrame.from_dict(data, orient='index')
        company_df['cik_str'] = company_df['cik_str'].astype(str).str.zfill(10)
        return company_df

    def get_cik(self, ticker):
        """Get CIK number for a given ticker"""
        ticker = ticker.upper()
        result = self.company_data[self.company_data['ticker'] == ticker]
        
        if not result.empty:
            return result.iloc[0]['cik_str']
        raise ValueError(f"Ticker {ticker} not found in TickerMap")

    def get_fundamentals(self, ticker):
        """Get fundamental data for a single ticker"""
        try:
            cik = self.get_cik(ticker)
        except ValueError:
            return None
            
        url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch data for {ticker} (CIK: {cik})")
            return None
        time.sleep(0.2)    
        return StockFundamentals(response.json(), ticker)

    def get_bulk_fundamentals(self, tickers):
        """Get fundamental data for multiple tickers with rate limiting"""
        results = {}
        for ticker in tickers:
            if fundamentals := self.get_fundamentals(ticker):
                results[ticker] = fundamentals
            time.sleep(0.2)
        return results
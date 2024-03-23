from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, MACD
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Choose a set of cryptocurrencies for day trading. These can be adjusted as needed.
        self.tickers = ["BTC-USD", "ETH-USD", "XRP-USD"]
        self.data_list = [Asset(i) for i in self.tickers]

    @property
    def interval(self):
        # Use an interval of 1 hour for day trading, providing a good balance between
        # reaction time and avoiding unnecessary noise in the market data.
        return "1hour"

    @property
    def assets(self):
        # Assets that this strategy will operate on, based on the tickers defined in __init__.
        return self.tickers

    @property
    def data(self):
        # The data needed for the strategy, which in this case is just the list of assets.
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        
        # Loop through each asset in the strategy.
        for ticker in self.tickers:
            rsi = RSI(ticker, data["ohlcv"], length=14)
            ema_short = EMA(ticker, data["ohlcv"], length=12)
            ema_long = EMA(ticker, data["ohlcv"], length=26)
            macd_signal = MACD(ticker, data["ohlcv"], fast=12, slow=26)["signal"]
            
            # Ensure we have enough data points to make a decision
            if rsi is not None and len(rsi) > 0 and len(ema_short) > 0 and len(ema_long) > 0:
                current_rsi = rsi[-1]
                macd_current = ema_short[-1] - ema_long[-1]
                macd_signal_current = macd_signal[-1]
                
                # Oversold RSI conditions suggesting a buy, but check if MACD confirms the potential upward trend.
                if current_rsi < 30 and macd_current > macd_signal_current:
                    # Full allocation to the asset
                    allocation_dict[ticker] = 1.0 / len(self.tickers)
                else:
                    # No allocation as conditions are not met
                    allocation_dict[ticker] = 0
            else:
                # Default to no allocation if not enough data is present
                allocation_dict[ticker] = 0
                
        # The TargetAllocation object ensures the allocations adhere to the required structure and constraints.
        return TargetAllocation(allocation_dict)
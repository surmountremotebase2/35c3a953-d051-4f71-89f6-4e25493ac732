from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # The assets we are interested in trading
        self.tickers = ["DOGE", "SHIB"]
        self.sma_length = 20  # Length of the SMA window

    @property
    def interval(self):
        # Using daily data for our strategy
        return "1day"

    @property
    def assets(self):
        # Defines the assets to consider in this strategy
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        
        # Loop through each ticker to determine the allocation
        for ticker in self.tickers:
            # Calculate the SMA for the ticker
            sma_values = SMA(ticker, data["ohlcv"], self.sma_length)
            if sma_values is None or len(sma_values) < self.sma_length:
                log(f"Insufficient data for {ticker}")
                continue  # Skip this iteration if there's not enough data
            
            current_price = data["ohlcv"][-1][ticker]['close']
            sma_current = sma_values[-1]
            
            # If current price is above the SMA, consider it a buying signal
            if current_price > sma_current:
                allocation_dict[ticker] = 0.5  # Allocate 50% of the portfolio to this asset
                log(f"Buying signal for {ticker} at price: {current_price}")
            # If current price is below the SMA, consider it a selling signal
            elif current_price < sma_current:
                allocation_dict[ticker] = 0  # Sell off the asset
                log(f"Selling signal for {ticker} at price: {current_price}")
            else:
                # If the current price is very close to the SMA, hold the position
                allocation_dict[ticker] = allocation_dict.get(ticker, 0)
                log(f"Holding position for {ticker}")

        # Return the target allocations for each asset
        return TargetAllocation(allocation_dict)
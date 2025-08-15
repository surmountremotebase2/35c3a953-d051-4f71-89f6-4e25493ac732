from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):

    def __init__(self):
        # Assuming high-volume stock for day trading (e.g., 'AAPL')
        self.ticker = "AAPL"

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        # Using 5min intervals for intra-day trading signals
        return "5min"

    def run(self, data):
        ohlcv = data["ohlcv"]
        # Get RSI and MACD for the ticker
        rsi_values = RSI(self.ticker, ohlcv, 14)  # 14 periods for RSI
        macd_values = MACD(self.ticker, ohlcv, fast=12, slow=26)  # Fast=12, Slow=26 for MACD

        allocation = {self.ticker: 0}  # Default to 0 (out of market)

        if not rsi_values or not macd_values or len(rsi_values) < 2 or len(macd_values["MACD"]) < 2:
            # Not enough data
            return TargetAllocation(allocation)
        
        current_rsi = rsi_values[-1]
        previous_rsi = rsi_values[-2]

        current_macd = macd_values["MACD"][-1]
        current_signal = macd_values["signal"][-1]
        previous_macd = macd_values["MACD"][-2]
        previous_signal = macd_values["signal"][-2]

        # Buy condition: RSI crosses above 30 and MACD crosses above the signal line
        if current_rsi > 30 and previous_rsi <= 30 and current_macd > current_signal and previous_macd <= previous_signal:
            allocation[self.ticker] = 1  # Go long on AAPL

        # Exit condition: RSI above 70 or MACD crosses below the signal line (for simplicity, not handling short positions)
        if current_rsi > 70 or (current_macd < current_signal and previous_macd >= previous_signal):
            allocation[self.ticker] = 0  # Exit AAPL

        log(f"Allocating {allocation[self.ticker]} to {self.ticker}")

        return TargetAllocation(allocation)

# Note: Trading involves risk and this strategy does not guarantee profits. 
# Always start with backtesting and small capital and consider transaction costs.
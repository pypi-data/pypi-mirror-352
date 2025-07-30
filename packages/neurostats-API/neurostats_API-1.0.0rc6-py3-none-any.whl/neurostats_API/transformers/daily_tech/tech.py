from .base import BaseDailyTransformer
import inspect
import pandas as pd
from .utils import TechProcessor


class DailyTechTransformer(BaseDailyTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)

        self.basic_indexes = [
            'SMA5', 'SMA20', 'SMA60', 'EMA5', 'EMA20', 'EMA40', 'EMA12',
            'EMA26', 'RSI7', 'RSI14', 'RSI21', 'MACD', 'Signal Line',
            'Middle Band', 'Upper Band', 'Lower Band', '%b', 'ATR', 'BBW',
            'EMA Cycle', 'EMA Cycle Instructions', 'Day Trading Signal'
        ]

        self.fetched_data = None
        self.daily_index = None
        self.weekly_index = None
        self.monthly_index = None
        self.quarterly_index = None
        self.yearly_index = None
    
    def process_transform(self, fetched_data):
        self.fetched_data = pd.DataFrame(fetched_data)

        self.daily_index = TechProcessor.cal_basic_index(
            self.fetched_data
        )
    
    def _check_daily_index(self):
        """
        檢查 daily_index 是否已經計算。
        如果 daily_index 為 None，則藉由 inspect 模組取得呼叫該函式的 caller，
        並拋出錯誤訊息，提示先呼叫 process_transform(fetched_data)
        再呼叫對應的函數（例如 get_weekly()）。
        """
        if self.daily_index is None:
            # 取得呼叫此 _check_daily_index 的函數名稱
            caller_name = inspect.stack()[1].function
            raise ValueError(f"Please call process_transform(fetched_data) before accessing {caller_name}()")

    def _get_resampled(self, period: str):
        """
        根據指定時間間隔對 daily_index 進行重採樣。
        """
        self._check_daily_index()  # 如果 daily_index 尚未計算，會拋出錯誤
        return TechProcessor.resample(
            self.daily_index,
            period=period,
            technical_indicators=self.basic_indexes
        )
    
    def get_daily(self):
        """
        回傳日線
        """
        self._check_daily_index() 
        return self.daily_index

    def get_weekly(self):
        """
        回傳週線資料。
        """
        return self._get_resampled('W')

    def get_monthly(self):
        """
        回傳月線資料。
        """
        return self._get_resampled('ME')

    def get_quarterly(self):
        """
        回傳季線資料。
        """
        return self._get_resampled('QE')
    
    def get_yearly(self):
        """
        回傳年線資料
        """
        return self._get_resampled("YE")
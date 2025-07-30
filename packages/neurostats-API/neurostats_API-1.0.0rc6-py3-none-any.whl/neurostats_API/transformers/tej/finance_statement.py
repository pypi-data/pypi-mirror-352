from .base import BaseTEJTransformer
from neurostats_API.utils import StatsProcessor, NoCompanyError, NoDataError
import pandas as pd


class TEJFinanceStatementTransformer(BaseTEJTransformer):

    def __init__(self, ticker, company_name, zone, target_column="Q"):
        super().__init__(ticker, company_name, zone)
        self.target_column = target_column

        index_files = [
            "tej_db/tej_db_index.yaml", "tej_db/tej_db_thousand_index.yaml",
            "tej_db/tej_db_percent_index.yaml", "tej_db/tej_db_skip_index.yaml"
        ]

        self.index_dict, self.thousand_dict, self.percent_dict, skip_index_dict = [
            StatsProcessor.load_yaml(file) for file in index_files
        ]

        self.check_index = set(self.index_dict.get("TWN/AINVFQ1", []))
        self.skip_index = set(
            self.percent_dict.get("TWN/AINVFQ1", []) + skip_index_dict.get("TWN/AINVFQ1", [])
        )
        self.thousand_index_list = list(
            self.thousand_dict.get("TWN/AINVFQ1", [])
        )
        self.percent_index_list = list(self.percent_dict.get("TWN/AINVFQ1", []))

    def process_transform(
        self,
        fetched_data,
        start_date,
        fetch_mode='QoQ',
        use_cal=True,
        indexes=None
    ):
        if (not fetched_data):
            raise NoDataError(f"No data found in collection: TEJ_finance_statement, ticker={self.ticker}")

        target_season = fetched_data[-1]['season']
        start_col = self._find_start_season(fetched_data, start_date)
        fetched_data = self._process_data_to_tej_format(
            fetched_data, target_key=self.target_column
        )

        if (indexes):
            fetched_data = pd.DataFrame.from_dict(fetched_data)
            fetched_data = fetched_data.loc[indexes, :]
            fetched_data = fetched_data.to_dict()

        if (fetch_mode == 'QoQ'):
            data = self._get_QoQ_data(data=fetched_data, use_cal=use_cal)
            data = data.iloc[:, start_col:]
        else:
            data = self._get_YoY_data(
                data=fetched_data, target_season=target_season, use_cal=use_cal
            )

            data = data.iloc[:, start_col:]
            target_season_col = data.columns.str.endswith(f"{target_season}")
            data = data.loc[:, target_season_col]

        return data

    def _find_start_season(self, fetched_data, start_date):
        """
        找出開始的年或季度所在的index
        """
        start_year = start_date.year
        start_season = (start_date.month - 1 // 3) + 1

        start_col = 0
        for data in fetched_data:
            if ((start_year, start_season) < (data['year'], data['season'])):
                break
            else:
                start_col += 1

        return start_col

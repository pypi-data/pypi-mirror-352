from sports_prediction_framework.datawrapper.DataWrapper import DataWrapper
from sports_prediction_framework.datawrapper.DataHandler import DataHandler


class MatchWrapper(DataWrapper):
    """
    Specialized wrapper for match-based data. Inherits from `DataWrapper` and provides
    additional functionality specific to sports matches.

    Attributes:
        name_columns (list[str]): Columns indicating team names (e.g., Home, Away).
        name_id_columns (list[str]): Columns indicating team IDs (e.g., HID, AID).
        score_columns (list[str]): Columns indicating match scores (e.g., HS, AS).
        result_column (list[str]): Column containing match results (e.g., WDL).
        prediction_columns (list[int]): Prediction column labels corresponding to match outcomes.
    """

    name_columns = ['Home', 'Away']
    name_id_columns = ['HID', 'AID']
    score_columns = ['HS', 'AS']
    result_column = ['WDL']
    prediction_columns = [1, 0, 2]
    odds_columns = ['odds_1',  'odds_X',  'odds_2']

    def __init__(self, data_handler: DataHandler, home_advantage):
        """
        Initialize a MatchWrapper.

        Args:
            data_handler (DataHandler): Object that holds and manages the match DataFrame.
            home_advantage (Any): Information or value to apply a home advantage modifier.
        """
        super().__init__(data_handler, home_advantage)
        self.total_set_of_teams = self.get_set_of_teams()
        self.total_number_of_teams = len(self.total_set_of_teams)
        self.total_set_of_teams_ids = set()


    def __str__(self):
        # All column groups combined
        column_groups = (
            ['Date']+
            self.name_columns +
            self.name_id_columns +
            self.score_columns +
            self.result_column +
            self.odds_columns +
            self.prediction_columns


        )

        # Filter only existing columns
        existing_columns = [col for col in column_groups if col in self.get_dataframe().columns]

        if not existing_columns:
            return "No matching columns found."

        return str(self.get_dataframe()[existing_columns])

    def set_after_compute_values(self):
        """
        Recomputes and updates the total set and number of teams
        after modifications to the DataFrame.
        """
        self.total_set_of_teams = self.get_set_of_teams()
        self.total_number_of_teams = len(self.total_set_of_teams)

    def get_set_of_teams(self):
        """
        Returns a set of all team names present in the DataFrame.

        Returns:
            set: Unique team names from 'Home' and 'Away' columns.
        """
        return set(self.data_handler.dataframe['Home']).union(
            set(self.data_handler.dataframe['Away'])
        )

    def get_set_of_teams_ids(self):
        """
        Returns a set of all team IDs present in the DataFrame.

        Returns:
            set: Unique team IDs from 'HID' and 'AID' columns.
        """
        return set(self.data_handler.dataframe['HID']).union(
            set(self.data_handler.dataframe['AID'])
        )

    def get_labels(self):
        """
        Retrieves the target labels for training or evaluation.

        Returns:
            pandas.Series: Series containing match outcomes (WDL).
        """
        return self.get_dataframe()['WDL']

from sports_prediction_framework.datawrapper.DataWrapper import DataWrapper
from sports_prediction_framework.datawrapper.DataHandler import DataHandler
import pandas as pd


class LeagueWrapper(DataWrapper):
    """
    Specialized wrapper for handling data grouped by leagues. Inherits from `DataWrapper`
    and provides additional league-level aggregation utilities.

    Attributes:
        league_column (str): The name of the column representing the league.
        number_of_teams_by_leagues (dict): A mapping from league names to the number of teams.
        total_number_of_leagues (int): Total number of unique leagues in the dataset.
    """

    league_column = 'League'

    def __init__(self, data_handler: DataHandler, home_advantage):
        """
        Initialize a LeagueWrapper.

        Args:
            data_handler (DataHandler): DataHandler object containing league-based match data.
            home_advantage (Any): Value or flag representing home advantage.
        """
        super().__init__(data_handler, home_advantage)
        self.number_of_teams_by_leagues = {}
        self.total_number_of_leagues = 0

    def set_after_compute_values(self):
        """
        Recomputes league metadata, including the number of teams per league
        and the total number of leagues.
        """
        self.number_of_teams_by_leagues = self.get_number_of_teams_by_league()
        self.total_number_of_leagues = len(self.get_leagues())

    def get_leagues(self):
        """
        Retrieves the list of unique leagues in the dataset.

        Returns:
            numpy.ndarray: An array of unique league names.
        """
        return pd.unique(self.get_dataframe()[self.league_column])

    def get_number_of_teams_by_league(self):
        """
        Calculates the number of unique teams in each league.

        Returns:
            dict: A dictionary mapping league names to the count of unique teams.
        """
        dict = {}
        for league, group_values in self.get_dataframe().groupby([self.league_column]):
            dict[league] = len(set(group_values['Home']).union(set(group_values['Away'])))
        return dict

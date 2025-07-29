from sports_prediction_framework.datawrapper.DataWrapper import DataWrapper
from sports_prediction_framework.datawrapper.DataHandler import DataHandler


class RaceWrapper(DataWrapper):
    """
    Specialized wrapper for race-based or individual-player events. Inherits from `DataWrapper`
    and provides identifiers relevant to player-based competitions.

    Attributes:
        name_columns (list[str]): Column(s) representing player names.
        name_id_columns (list[str]): Column(s) representing player IDs.
        rank_column (list[str]): Column(s) representing player rankings or positions.
    """

    name_columns = ['Player']
    name_id_columns = ['PID']
    rank_column = ['Rank']

    def __init__(self, data_handler: DataHandler, home_advantage):
        """
        Initialize a RaceWrapper.

        Args:
            data_handler (DataHandler): Object containing the race or player-based DataFrame.
            home_advantage (Any): Placeholder for compatibility with `DataWrapper`, may be unused.
        """
        super().__init__(data_handler, home_advantage)

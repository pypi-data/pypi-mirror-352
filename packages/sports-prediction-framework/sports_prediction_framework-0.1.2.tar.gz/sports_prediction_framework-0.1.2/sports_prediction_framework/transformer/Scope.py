from abc import ABC, abstractmethod
from datetime import timedelta
from sports_prediction_framework.datawrapper.DataWrapper import DataWrapper
from sports_prediction_framework.utils.AttributeSetter import AttributeSetter
import pandas as pd


class Scope(ABC):
    """
    Abstract base class for data segmentation scopes.

    Defines the interface and common initialization logic for various types of
    scopes used to segment or window datasets (e.g., by season, league, or time).

    Parameters
    ----------
    wrapper : DataWrapper, optional
        Wrapper object providing access to the underlying data.
    parameters : dict, optional
        Dictionary of parameters used to configure the scope.
    """

    def __init__(self, wrapper: DataWrapper = None, parameters=None):
        self.wrapper = wrapper
        self.parameters = parameters
        AttributeSetter.set_attributes(self, parameters)

    def shift(self):
        """
        Move or adjust the scope window/segment forward.

        Intended to be implemented by subclasses.
        """
        pass

    def inside(self):
        """
        Check if the current scope window/segment is still within valid bounds.

        Returns
        -------
        bool
            True if still within bounds, False otherwise.

        Intended to be implemented by subclasses.
        """
        pass

    def reset_state(self):
        """
        Reset the scope to its initial state.

        Intended to be implemented by subclasses.
        """
        pass

    def current_state(self):
        """
        Return the current scope state, typically the segment or window limits.

        Returns
        -------
        tuple
            Typically (column_name, (start_value, end_value)) or similar.

        Intended to be implemented by subclasses.
        """
        pass


class WindowScope(Scope):
    """
    Scope implementation that defines a window on a continuous or ordinal column
    (e.g., season, year), with a fixed size and stride for iteration.

    Parameters
    ----------
    wrapper : DataWrapper, optional
        Data wrapper providing the dataset.
    parameters : dict, optional
        Configuration parameters including:
          - col (str): column name to window on (default 'Season')
          - start (int): starting value of the window (default 2000)
          - max (int): maximum value for the window (default 2005)
          - size (int): size of the window (default 1)
          - stride (int): step size to move the window (default 2)
    """

    default_parameters = {'col': 'Season', 'start': 2000, 'max': 2005, 'size': 1, 'stride': 2}

    def __init__(self, wrapper: DataWrapper = None, parameters=default_parameters):
        super().__init__(wrapper, parameters)
        if self.parameters is not None:
            if 'start' in self.parameters:
                self.start = self.parameters['start']
            elif self.wrapper is not None and self.parameters['col'] is not None:
                self.start = self.wrapper.get_dataframe()[self.parameters['col']].min()
            if 'max' in self.parameters:
                self.max = self.parameters['max']
            elif self.wrapper is not None:
                self.max = self.wrapper.get_dataframe()[self.parameters['col']].max()
            self.orig_start = self.start
            self.orig_size = self.size

    def reset_state(self):
        """
        Reset the window to its original start and size.
        """
        self.start = self.orig_start
        self.size = self.orig_size

    def current_state(self):
        """
        Return the current window range as a tuple with the column and start/end.

        Returns
        -------
        tuple
            (column_name, (start_value, end_value))
        """
        if isinstance(self.start, int) or isinstance(self.size, int):
            return self.col, (self.start, self.start + self.size + timedelta(days=1).days)
        return self.col, (self.start, self.start + self.size + timedelta(days=1))


class ScopeExpander(WindowScope):
    """
    Scope variant that expands the window size by a stride on each shift.

    Methods
    -------
    shift():
        Increase the window size by the stride value.
    inside():
        Returns whether the expanded window end is within the maximum allowed.
    """

    def shift(self):
        """
        Increase the window size by stride.
        """
        self.size += self.stride

    def inside(self):
        """
        Check if the window end is still within max.

        Returns
        -------
        bool
        """
        return self.start + self.size <= self.max


class ScopeRoller(WindowScope):
    """
    Scope variant that rolls the window start forward by the stride on each shift.

    Methods
    -------
    shift():
        Move the window start by stride.
    inside():
        Returns whether the window start is still within the maximum allowed.
    """

    def shift(self):
        """
        Move the window start forward by stride.
        """
        self.start += self.stride

    def inside(self):
        """
        Check if the window start is still within max.

        Returns
        -------
        bool
        """
        return self.start <= self.max


class EnumScope(Scope):
    """
    Scope that iterates over an enumerated list of values for a given column.

    Parameters
    ----------
    wrapper : DataWrapper, optional
        Data wrapper providing access to data.
    parameters : dict, optional
        Configuration including:
          - col (str): column name to filter on (default 'League')
          - enum (list): list of enum values to iterate (default ['GER1'])
    """

    default_parameters = {'col': 'League', 'enum': ['GER1']}
    cur_index = 0

    def __init__(self, wrapper=None, parameters=default_parameters):
        super().__init__(wrapper, parameters)

    def set_parameters_from_wrapper(self, wrapper: DataWrapper):
        """
        Initialize enum list from unique values of the column if not provided.

        Parameters
        ----------
        wrapper : DataWrapper
            Data wrapper to extract unique column values.
        """
        if 'enum' not in self.parameters:
            self.enum = pd.unique(self.wrapper.get_columns(self.col)).tolist()

    def shift(self):
        """
        Advance to the next enum value.
        """
        self.cur_index += 1

    def inside(self):
        """
        Check if the current enum index is within the list bounds.

        Returns
        -------
        bool
        """
        return self.cur_index < len(self.enum)

    def reset_state(self):
        """
        Reset the current enum index to zero.
        """
        self.cur_index = 0

    def current_state(self):
        """
        Return the current enum value as a list for filtering.

        Returns
        -------
        tuple
            (column_name, [current_enum_value])
        """
        return (self.col, [self.enum[self.cur_index]])


class TestingWindowScope(WindowScope):
    """
    Scope for testing windows that depend on a related training window scope.

    Parameters
    ----------
    training_window_scope : WindowScope
        The training window scope to base the testing window on.
    parameters : dict, optional
        Parameters for the testing window scope (default sets 'col' to 'Season', 'size' to 1).
    """

    name = 'testing_window_scope'
    init_parameters = {name: {'col': 'Season', 'size': 1}}

    def __init__(self, training_window_scope: WindowScope, parameters=init_parameters, **kwargs):
        self.training_window_scope = training_window_scope
        super().__init__(parameters=parameters, **kwargs)

    def set_parameters(self, parameters):
        """
        Override to set testing window parameters relative to the training window.

        Parameters
        ----------
        parameters : dict
            Parameters dict (not currently used for custom values).

        Notes
        -----
        This method sets:
          - start: training start + training size + 1
          - max: training max
          - stride: training stride
          - orig_start: initialized to start
          - orig_size: initialized to current size
        """
        if parameters is not None:
            self.start = self.training_window_scope.start + self.training_window_scope.size + 1
            self.max = self.training_window_scope.max
            self.stride = self.training_window_scope.stride
            self.orig_start = self.start
            self.orig_size = self.size

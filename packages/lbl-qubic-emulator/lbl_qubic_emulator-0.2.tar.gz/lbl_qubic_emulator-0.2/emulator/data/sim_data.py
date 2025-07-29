"""Module for simulation data management in quantum circuits.

This module provides the SimData class for managing and processing simulation data
during quantum circuit emulation.
"""

from abc import ABC, abstractmethod
import numpy as np


class SimData(ABC):
    """Abstract base class for simulation data management.

    This class defines the interface for managing and processing simulation data
    during quantum circuit emulation, including pulse generation and signal processing.
    """

    @abstractmethod
    def __init__(self, container_name, samples_per_clk=1, interp_ratio=1, fpga_clk_freq=500e6, delay=0):
        """Initialize a new SimData instance.

        Parameters
        ----------
        container_name : str
            Name of the data container
        samples_per_clk : int, optional
            Number of samples per clock cycle, default 1
        interp_ratio : int, optional
            Interpolation ratio, default 1
        fpga_clk_freq : float, optional
            FPGA clock frequency in Hz, default 500e6
        delay : int, optional
            Processing delay in clock cycles, default 0
        """
        pass

    @abstractmethod
    def add_pulse(self, amp: int, freq: dict, phase: int, env: np.ndarray, tstart: int, twidth: int):
        """Add a new pulse to the simulation data.

        Parameters
        ----------
        amp : int
            Pulse amplitude
        freq : dict
            Frequency data dictionary
        phase : int
            Pulse phase
        env : np.ndarray
            Envelope data array
        tstart : int
            Start time of pulse
        twidth : int
            Width of pulse
        dc : bool
            Flag indicating if pulse is DC
        """
        pass

    @abstractmethod
    def resolve(self, tend=None):
        """Resolve simulation data up to the specified end time.

        Parameters
        ----------
        tend : int, optional
            End time for resolution, defaults to None

        Returns
        -------
        dict
            Resolved simulation data
        """
        pass

    @abstractmethod
    def insert(self, tstart: int, signal: np.ndarray):
        """Insert a signal into the time series data.

        Parameters
        ----------
        tstart : int
            Start time for signal insertion
        signal : np.ndarray
            Signal data to insert
        """
        pass

    @abstractmethod
    def get(self, name: str):
        """Get simulation data by name.

        Parameters
        ----------
        name : str
            Name of the data to retrieve

        Returns
        -------
        np.ndarray
            Requested simulation data array
        """
        pass

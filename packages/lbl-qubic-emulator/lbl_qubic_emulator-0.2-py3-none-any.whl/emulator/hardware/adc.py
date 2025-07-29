"""Module for analog-to-digital converter (ADC) simulation.

This module provides the ADC class for simulating analog-to-digital conversion
and signal measurement in quantum circuits.
"""

from typing import Dict, Any
import numpy as np
from emulator.data.rf_sim_data import RFSimData

class ADC:
    """Analog-to-digital converter for quantum circuit simulation.

    This class represents an ADC that measures readout resonator responses.
    It stores time series data and processes signals from resonators in the
    DAC class for visualization in the result object.

    Attributes
    ----------
    name : str
        ADC identifier (e.g., 'ADC0')
    channels : Dict[str, Any]
        Dictionary of channels assigned to this ADC, keyed by channel name
    sim_data : SimData
        Simulation data containing time series voltage measurements
    samples_per_clk : int
        Number of samples per clock cycle
    interp_ratio : int
        Interpolation ratio
    """

    def __init__(self, name: str, channels: Dict[str, Any]) -> None:
        """Initialize a new ADC instance.

        Parameters
        ----------
        name : str
            ADC identifier (e.g., 'ADC0')
        channels : Dict[str, Any]
            Dictionary of channels assigned to this ADC
        """
        self.name = name
        self.channels = channels
        self.samples_per_clk = 0
        self.interp_ratio = 0
        self.sim_data = None
        self.set_config(16, 16)


    def set_config(self, samples_per_clk: int, interp_ratio: int) -> None:
        """Set the configuration of the ADC.

        Parameters
        ----------
        samples_per_clk : int
            Number of samples per clock cycle
        interp_ratio : int
            Interpolation ratio
        """
        self.samples_per_clk = samples_per_clk
        self.interp_ratio = interp_ratio
        self.sim_data = RFSimData(self.name, self.samples_per_clk, self.interp_ratio)
        

    def update_data(self, resonator_signal: np.ndarray, tstart: int) -> None:
        """Update ADC signal with new resonator response.

        Parameters
        ----------
        resonator_signal : np.ndarray
            Time series data to add to the ADC signal
        tstart : int
            Start time in clock cycles
        """
        self.sim_data.insert(tstart, resonator_signal)


    def end_sim(self, time_list: np.ndarray) -> None:
        """End the current simulation and finalize data.

        Parameters
        ----------
        time_list : np.ndarray
            List of time points for the simulation
        """
        self.sim_data.resolve(tend=len(time_list)//self.samples_per_clk)
        return [self.sim_data, list(self.channels.keys())]

    def reset(self) -> None:
        """Reset the ADC state."""
        self.sim_data = RFSimData(self.name, samples_per_clk=self.samples_per_clk, interp_ratio=self.interp_ratio)

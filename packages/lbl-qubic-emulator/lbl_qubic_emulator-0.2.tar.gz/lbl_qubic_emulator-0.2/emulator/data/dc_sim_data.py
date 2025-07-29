"""Module for direct current (DC) simulation data management in quantum circuits.

This module provides the DCSimData class for managing and processing DC signal
simulation data during quantum circuit emulation, including voltage levels and
timing information.
"""

import numpy as np
from emulator.data.sim_data import SimData

class DCSimData(SimData):
    """Class for managing DC signal simulation data in quantum circuits.

    This class handles the storage and processing of DC signal data, including
    voltage levels, timing information, and pulse generation. It maintains
    continuous voltage levels between pulses and handles DC signal transitions.

    Attributes
    ----------
    name : str
        Name of the DC signal container
    pulses : list
        List of DC pulse data dictionaries containing amplitude and timing info
    sim_data : dict
        Dictionary containing time series data arrays for voltage and timing
    fpga_clk_freq : float
        FPGA clock frequency in Hz
    delay : int
        Processing delay in clock cycles
    curr_time : int
        Current simulation time in clock cycles
    curr_voltage : int
        Current voltage level
    fully_resolved : bool
        Flag indicating if all data is resolved
    """

    def __init__(self, container_name, samples_per_clk=1, interp_ratio=1, fpga_clk_freq=500e6, delay=0):
        """Initialize a new DCSimData instance.

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
        self.name = container_name
        self.amp_normalization_factor = 32767
        self.pulses = []
        self.sim_data = {'time': [], 'voltage': [], 'voltage_imag': [], 'envelope': []}
        self.fpga_clk_freq = fpga_clk_freq
        self.delay = delay
        self.curr_time = 0
        self.curr_voltage = 0
        self.fully_resolved = False

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
        """
        new_pulse = {'amp': amp,
                     'tstart': tstart
                    }
        self.pulses.append(new_pulse)

    def resolve(self, tend=None):
        """Resolve simulation data up to the specified end time.

        Parameters
        ----------
        tend : int, optional
            End time for resolution, defaults to None. If None, the SimData will resolve to the
            last pulse in the pulses list

        Returns
        -------
        dict
            Resolved simulation data
        """
        if tend is None:
            raise ValueError("tend must be specified for DCSimData")

        if not self.fully_resolved:
            if isinstance(self.sim_data['time'], np.ndarray):
                self.sim_data['time'] = self.sim_data['time'].tolist()
                self.sim_data['voltage'] = self.sim_data['voltage'].tolist()
                self.sim_data['voltage_imag'] = self.sim_data['voltage_imag'].tolist()
                self.sim_data['envelope'] = self.sim_data['envelope'].tolist()

            while self.curr_time < tend:
                if len(self.pulses) != 0:
                    curr_pulse = self.pulses.pop(0)
                    next_time = min(curr_pulse['tstart'], tend)
                    next_voltage = curr_pulse['amp']
                else:
                    next_time = tend
                    next_voltage = self.curr_voltage
                added_time = next_time - self.curr_time
                dc_voltage = self.curr_voltage / self.amp_normalization_factor
                self.sim_data['voltage'].extend([dc_voltage] * added_time)
                self.sim_data['time'].extend(np.arange(self.curr_time, next_time))
                self.curr_time = next_time
                self.curr_voltage = next_voltage

        self.sim_data['time'] = np.array(self.sim_data['time'])
        self.sim_data['voltage'] = np.array(self.sim_data['voltage'])
        self.sim_data['voltage_imag'] = np.array(self.sim_data['voltage_imag'])
        self.sim_data['envelope'] = np.array(self.sim_data['envelope'])
        return self.sim_data

    def insert(self, tstart: str, signal: np.ndarray):
        """Insert a signal into the time series data.

        Parameters
        ----------
        tstart : int
            Start time for signal insertion
        signal : np.ndarray
            Signal data to insert
        """
        length = len(self.sim_data['time'])
        if isinstance(self.sim_data['time'], np.ndarray):
            self.sim_data['time'] = self.sim_data['time'].tolist()
            self.sim_data['voltage'] = self.sim_data['voltage'].tolist()
            self.sim_data['voltage_imag'] = self.sim_data['voltage_imag'].tolist()
            self.sim_data['envelope'] = self.sim_data['envelope'].tolist()

        if length < tstart + len(signal):
            buffer_len = tstart + len(signal) - length
            self.sim_data['time'].extend(length/16 + (np.arange(buffer_len) / 16))
            self.sim_data['voltage'].extend(np.zeros(buffer_len))
            self.sim_data['voltage_imag'].extend(np.zeros(buffer_len, dtype=np.complex128))
            self.sim_data['envelope'].extend(np.zeros(buffer_len))

        self.sim_data['voltage'][tstart:tstart + len(signal)] += signal
        self.sim_data['time'] = np.array(self.sim_data['time'])
        self.sim_data['voltage'] = np.array(self.sim_data['voltage'])
        self.sim_data['voltage_imag'] = np.array(self.sim_data['voltage_imag'])
        self.sim_data['envelope'] = np.array(self.sim_data['envelope'])

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
        return self.sim_data[name]

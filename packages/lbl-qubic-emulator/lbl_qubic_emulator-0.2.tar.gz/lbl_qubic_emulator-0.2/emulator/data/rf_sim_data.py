"""Module for simulation data management in quantum circuits.

This module provides the SimData class for managing and processing simulation data
during quantum circuit emulation.
"""

from typing import Dict, Any
import numpy as np
from emulator.data.sim_data import SimData

class RFSimData(SimData):
    """Class for managing simulation data during quantum circuit emulation.

    This class handles the storage and processing of simulation data including
    time series, voltages, and envelopes for quantum circuit components.

    Attributes
    ----------
    name : str
        Name of the data container
    pulses : list
        List of pulse data dictionaries
    sim_data : dict
        Dictionary containing time series data arrays
    samples_per_clk : int
        Number of samples per clock cycle
    interp_ratio : int
        Interpolation ratio for signal processing
    fpga_clk_freq : float
        FPGA clock frequency in Hz
    delay : int
        Processing delay in clock cycles
    curr_time : int
        Current simulation time
    fully_resolved : bool
        Flag indicating if all data is resolved
    """

    def __init__(self, container_name: str, samples_per_clk: int=1, interp_ratio:int =1, fpga_clk_freq:int =500e6, delay: int=0):
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
        self.name = container_name
        self.pulses = []
        self.sim_data = {'time': [], 'voltage': [], 'voltage_imag': [], 'envelope': []}
        self.cw_pulse_data = {
            'pulse': None,
            'beg_clk_cyc': np.complex128(1 + 1j * 0),
            't': 0
        }
        self.samples_per_clk = samples_per_clk
        self.interp_ratio = interp_ratio
        self.fpga_clk_freq = fpga_clk_freq
        self.delay = delay
        self.curr_time = 0
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
                     'freq': freq,
                     'phase': phase,
                     'env': env,
                     'tstart': tstart,
                     'twidth': twidth
                     }
        self.pulses.append(new_pulse)

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
        if not self.fully_resolved:
            if isinstance(self.sim_data['time'], np.ndarray):
                self.sim_data['time'] = self.sim_data['time'].tolist()
                self.sim_data['voltage'] = self.sim_data['voltage'].tolist()
                self.sim_data['voltage_imag'] = self.sim_data['voltage_imag'].tolist()
                self.sim_data['envelope'] = self.sim_data['envelope'].tolist()

            while self.pulses and (tend is None or self.pulses[0]['tstart'] < tend):
                curr_pulse = self.pulses.pop(0)
                buffer_len = (curr_pulse['tstart'] - self.curr_time) * self.samples_per_clk
                self.sim_data['time'].extend((self.curr_time + (np.arange(buffer_len) / self.samples_per_clk)).tolist())
                self.sim_data['voltage'].extend(np.zeros(buffer_len))
                self.sim_data['voltage_imag'].extend(np.zeros(buffer_len, dtype=np.complex128))
                self.sim_data['envelope'].extend(np.zeros(buffer_len))
                self.curr_time += curr_pulse['tstart'] - self.curr_time

                if len(curr_pulse['env']) != self.samples_per_clk: # Regular RF pulse
                    self.calculate_pulse_data(curr_pulse)
                else: # CW pulse
                    if curr_pulse['twidth'] == 0:
                        if len(self.pulses) != 0:
                            next_pulse_tstart = min(self.pulses[0]['tstart'], tend)
                        else:
                            next_pulse_tstart = tend
                    else:
                        next_pulse_tstart = curr_pulse['tstart'] + curr_pulse['twidth']
                    
                    self.cw_pulse_data['pulse'] = curr_pulse
                    self.cw_pulse_data['beg_clk_cyc'] = np.complex128(1 + 1j * 0)
                    self.cw_pulse_data['t'] = 0

                    self.calculate_cw_pulse_data(curr_pulse, next_pulse_tstart)
                    
                    if self.curr_time != tend:
                        self.cw_pulse_data['pulse'] = None
                        self.cw_pulse_data['beg_clk_cyc'] = np.complex128(1 + 1j * 0)
                        self.cw_pulse_data['t'] = 0
                    else:
                        self.cw_pulse_data['pulse']['tstart'] = self.curr_time
                        self.pulses.insert(0, self.cw_pulse_data['pulse'])
                    

            if tend is not None and self.curr_time < tend:
                buffer_len = (int)((tend - self.curr_time) * self.samples_per_clk)
                self.sim_data['time'].extend((self.curr_time + (np.arange(buffer_len) / self.samples_per_clk)).tolist())
                self.sim_data['voltage'].extend(np.zeros(buffer_len))
                self.sim_data['voltage_imag'].extend(np.zeros(buffer_len, dtype=np.complex128))
                self.sim_data['envelope'].extend(np.zeros(buffer_len))
                self.curr_time += int(buffer_len / self.samples_per_clk)

            self.sim_data['time'] = np.array(self.sim_data['time'])
            self.sim_data['voltage'] = np.array(self.sim_data['voltage'])
            self.sim_data['voltage_imag'] = np.array(self.sim_data['voltage_imag'])
            self.sim_data['envelope'] = np.array(self.sim_data['envelope'])
        return self.sim_data

    def calculate_pulse_data(self, curr_pulse: Dict[str, Any]):
        """Calculate and store pulse data for a given pulse.

        Parameters
        ----------
        curr_pulse : dict
            Dictionary containing pulse parameters including amplitude, frequency, phase,
            envelope, start time, and width
        """
        beg_clk_cycle = np.complex128(1 + 1j * 0)
        curr_cyc = np.complex128(1 + 1j * 0)
        w = 2.0 * np.pi * ((curr_pulse['freq']['freq'][0] % self.fpga_clk_freq) / self.fpga_clk_freq)
        for t in range((int)(self.samples_per_clk * curr_pulse['twidth'])):
            if t == 0:
                phi_init = w * (curr_pulse['tstart'] + self.delay) + (curr_pulse['phase'])
                beg_clk_cycle *= np.complex128(np.cos(phi_init) + 1j * np.sin(phi_init))
                curr_cyc = beg_clk_cycle / np.abs(beg_clk_cycle)
                self.curr_time += 1
            elif t % self.samples_per_clk == 0:
                beg_clk_cycle *= np.complex128(np.cos(w) + 1j * np.sin(w))
                curr_cyc = beg_clk_cycle / np.abs(beg_clk_cycle)
                self.curr_time += 1
            else:
                freq_iq = curr_pulse['freq']['iq15'][0][(t - 1) % self.samples_per_clk]
                freq_iq /= np.abs(freq_iq)
                curr_cyc = freq_iq * beg_clk_cycle

            v = curr_cyc * (curr_pulse['env'][(int)(t / self.interp_ratio)]) * (curr_pulse['amp'])
            self.sim_data['time'].append(curr_pulse['tstart'] + (t/self.samples_per_clk))
            self.sim_data['voltage'].append(v.real)
            self.sim_data['voltage_imag'].append(v)
            self.sim_data['envelope'].append((curr_pulse['env'][(int)(t / self.interp_ratio)]))

    def calculate_cw_pulse_data(self, curr_pulse: Dict[str, Any], next_pulse_tstart: int):
        """Calculate and store continuous wave pulse data between current and next pulse.

        Parameters
        ----------
        curr_pulse : dict
            Dictionary containing current pulse parameters
        next_pulse_tstart : int
            Start time of the next pulse
        """
        beg_clk_cycle = self.cw_pulse_data['beg_clk_cyc']
        curr_cyc = np.complex128(1 + 1j * 0)
        w = 2.0 * np.pi * ((curr_pulse['freq']['freq'][0] % self.fpga_clk_freq) / self.fpga_clk_freq)
        tstart = self.cw_pulse_data['t']
        for t in range((int)(self.samples_per_clk * (next_pulse_tstart - self.curr_time)) + tstart):
            if t == 0:
                phi_init = w * (curr_pulse['tstart'] + self.delay) + (curr_pulse['phase'])
                beg_clk_cycle *= np.complex128(np.cos(phi_init) + 1j * np.sin(phi_init))
                curr_cyc = beg_clk_cycle / np.abs(beg_clk_cycle)
                self.curr_time += 1
                self.cw_pulse_data['beg_clk_cyc'] = beg_clk_cycle
            elif t % self.samples_per_clk == 0:
                beg_clk_cycle *= np.complex128(np.cos(w) + 1j * np.sin(w))
                curr_cyc = beg_clk_cycle / np.abs(beg_clk_cycle)
                self.curr_time += 1
                self.cw_pulse_data['beg_clk_cyc'] = beg_clk_cycle
            else:
                freq_iq = curr_pulse['freq']['iq15'][0][(t - 1) % self.samples_per_clk]
                freq_iq /= np.abs(freq_iq)
                curr_cyc = freq_iq * beg_clk_cycle

            v = curr_cyc * (curr_pulse['amp']) * curr_pulse['env'][t % (self.samples_per_clk // self.interp_ratio)]
            self.sim_data['time'].append(curr_pulse['tstart'] + (t/self.samples_per_clk))
            self.sim_data['voltage'].append(v.real)
            self.sim_data['voltage_imag'].append(v)
            self.sim_data['envelope'].append(1.0)
            self.cw_pulse_data['t'] += 1

    def insert(self, tstart: int, signal: np.ndarray):
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

        if length < tstart*self.samples_per_clk + len(signal):
            buffer_len = tstart*self.samples_per_clk + len(signal) - length
            self.sim_data['time'].extend(length/16 + (np.arange(buffer_len) / 16))
            self.sim_data['voltage'].extend(np.zeros(buffer_len))
            self.sim_data['voltage_imag'].extend(np.zeros(buffer_len, dtype=np.complex128))
            self.sim_data['envelope'].extend(np.zeros(buffer_len))

        self.sim_data['voltage'][tstart*self.samples_per_clk:tstart*self.samples_per_clk + len(signal)] += signal
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

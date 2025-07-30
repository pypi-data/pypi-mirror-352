"""Module for digital-to-analog converter (DAC) simulation.

This module provides the DAC class for simulating digital-to-analog conversion
and signal generation in quantum circuits.
"""

from typing import Dict, List, Any, Tuple
from emulator.hardware.resonator import Resonator
from emulator.data.rf_sim_data import RFSimData
from emulator.config.hardware_config import HWConfig
from emulator.config.qubit_config import QubitConfig
from emulator.channels.channel import Channel
import numpy as np

class DAC:
    """Digital-to-analog converter for quantum circuit simulation.

    This class represents a DAC that combines and processes signals from multiple
    channels according to the DSP configuration. It handles signal summation and
    visualization of the combined output.

    Attributes
    ----------
    name : str
        DAC identifier (e.g., 'DAC0')
    channels : Dict[str, Channel]
        Dictionary of channels assigned to this DAC, keyed by channel name
    active : bool
        Whether the DAC has any channels assigned
    resonators : Dict[str, Resonator]
        Dictionary mapping resonator names to Resonator objects for ADC response
    samples_per_clk : int
        Number of samples per clock cycle for the assigned channels
    sim_data : SimData
        Simulation data containing summed voltages from all channels
    """

    def __init__(self, name: str, channels: Dict[str, Channel],
                hwconfig: HWConfig, qubitconfig: QubitConfig) -> None:
        """Initialize a new DAC instance.

        Parameters
        ----------
        name : str
            DAC identifier (e.g., 'DAC0')
        channels : Dict[str, Any]
            Dictionary of channels assigned to this DAC
        hwconfig : HWConfig
            Hardware configuration object
        qubitconfig : QubitConfig
            Qubit and resonator configuration object
        """
        self.name = name
        self.channels = channels
        self.active = len(self.channels)

        self.resonators = {}
        for chan in self.channels:
            if 'rdrv' in self.channels[chan].name:
                res_name = self.channels[chan].name[1]
                self.resonators[res_name] = Resonator(f"R{res_name}",
                                                      hwconfig,
                                                      qubitconfig)

        if len(self.channels) != 0:
            spc_list = []
            for chan in self.channels.values():
                if 'samples_per_clk' in chan.chanconfig.elem_params:
                    spc_list.append(chan.chanconfig.elem_params['samples_per_clk'])
            self.samples_per_clk = spc_list[0]
            all_same = all(spc == self.samples_per_clk for spc in spc_list)
            assert (all_same), (
                "All channels in the same DAC must have the same samples_per_clk value. "
                "These values can be changed in the hardware configuration file."
            )
            intr_list = []
            for chan in self.channels.values():
                if 'interp_ratio' in chan.chanconfig.elem_params:
                    intr_list.append(chan.chanconfig.elem_params['interp_ratio'])
            self.interp_ratio = intr_list[0]
            all_same = all(interp == self.interp_ratio for interp in intr_list)
            assert (all_same), (
                "All channels in the same DAC must have the same interp_ratio value. "
                "These values can be changed in the hardware configuration file."
            )
        else:
            self.samples_per_clk = 1
            self.interp_ratio = 1

        self.sim_data = RFSimData(self.name, self.samples_per_clk, self.interp_ratio, hwconfig.freq)


    def update_data(self, time: int) -> None:
        """Update DAC data at the current simulation time.

        Parameters
        ----------
        time : int
            Current simulation time in clock cycles
        """
        if not self.active:
            return

        self.sim_data.resolve(time)
        self.sim_data.sim_data['voltage'] = np.zeros(len(self.sim_data.sim_data['voltage']))
        self.sim_data.sim_data['voltage_imag'] = np.zeros(len(self.sim_data.sim_data['voltage_imag']),
                                                          dtype=np.complex128)

        for chan in self.channels:
            self.channels[chan].resolve(time)
            chan_sim_data = self.channels[chan].sim_data.sim_data
            self.sim_data.sim_data['voltage'] += chan_sim_data['voltage']
            self.sim_data.sim_data['voltage_imag'] += chan_sim_data['voltage_imag']
        self.sim_data.sim_data['time'] = np.arange(len(self.sim_data.sim_data['voltage'])) / self.samples_per_clk


    def get_resonator_response(self, chan: str, tstart: int, twidth: int,
                             measurement: Dict[str, int]) -> np.ndarray:
        """Get resonator response for a channel.

        Parameters
        ----------
        chan : str
            Channel name
        tstart : int
            Start time in clock cycles
        twidth : int
            Pulse width in clock cycles
        measurement : Dict[str, int]
            Measurement values

        Returns
        -------
        np.ndarray
            Resonator response signal
        """
        for channel in self.channels:
            if self.channels[channel].name == chan:
                full_signal = self.channels[channel].sim_data.get('voltage')
                tstart *= self.samples_per_clk
                twidth *= self.samples_per_clk
                measurement_signal = full_signal[tstart:tstart+twidth]
                break

        adc_signal = np.array([])
        for _, resonator in self.resonators.items():
            if len(adc_signal) == 0:
                res_name = resonator.name
                adc_signal = resonator.generate_response_pulse(measurement_signal, 
                                                            measurement[f"Q{int(res_name[1])}"])
            else:
                res_name = resonator.name
                resonator_response = resonator.generate_response_pulse(measurement_signal, 
                                                                measurement[f"Q{int(res_name[1])}"])
                response_length = len(resonator_response)
                adc_length = len(adc_signal)
                if response_length > adc_length:
                    adc_signal = np.pad(adc_signal, (0, response_length - adc_length), mode='constant')
                elif response_length < adc_length:
                    resonator_response = np.pad(resonator_response, (0, adc_length - response_length), mode='constant')
                adc_signal += resonator_response
        return adc_signal


    def end_sim(self) -> Tuple[RFSimData, List[str]]:
        """End the current simulation and finalize data."""
        return [self.sim_data, list(self.channels.keys())]


    def reset(self) -> None:
        """Reset the DAC state."""
        self.sim_data = RFSimData(self.name, samples_per_clk=self.samples_per_clk, interp_ratio=self.interp_ratio)

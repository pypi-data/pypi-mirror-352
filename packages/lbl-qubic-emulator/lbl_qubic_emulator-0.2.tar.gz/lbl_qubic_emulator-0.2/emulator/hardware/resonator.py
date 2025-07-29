"""
Module for resonator simulation in quantum circuits.

This module provides the Resonator class for modeling resonator behavior and its
response to readout pulses in quantum circuits.
"""
from typing import List
import numpy as np
from emulator.config.hardware_config import HWConfig
from emulator.config.qubit_config import QubitConfig

class Resonator:
    """
    Model a resonator and its response to readout pulses.

    This class simulates a resonator's behavior by applying a Lorentzian delay
    to input signals and generating corresponding output signals.

    Attributes
    ----------
        name : str
            The name of this resonator
        quality_factor : int
            Quality factor of the readout resonator
        parameters : List[float]
            List of parameters for calculating resonator impulse response:
            [sqrt_term, amp0, amp1, w0, w1]
            where:
            - sqrt_term = np.sqrt(1 - 1/(4*Q**2))
            - amp0 = w0 / sqrt_term 
            - amp1 = w1 / sqrt_term
        delay : int
            The delay in FPGA clock cycles from the initial DAC input to the ADC output
    """

    def __init__(self, name: str, hwconfig: HWConfig, qubitconfig: QubitConfig) -> None:
        """
        Initialize a new resonator with the given configuration.

        Parameters
        ----------
            name : str
                The name of this resonator
            hwconfig : HWConfig
                Configuration object containing resonator response latency information
            qubitconfig : QubitConfig
                Configuration object containing quality factor and omega values

        Warns
        -----
            Warning
                If quality factor is not specified in the configuration
        """
        self.name = name

        self.quality_factor = qubitconfig.resonators[name].Q
        res_freq0 = qubitconfig.resonators[self.name].resonant_frequency_0
        omega0 = 2 * np.pi * (res_freq0 / 500e6)
        res_freq1 = qubitconfig.resonators[self.name].resonant_frequency_1
        omega1 = 2 * np.pi * (res_freq1 / 500e6)


        self.parameters = []
        self.parameters.append(np.sqrt(1 - 1/(4 * self.quality_factor**2)))
        self.parameters.append(omega0 / self.parameters[0])
        self.parameters.append(omega1 / self.parameters[0])
        self.parameters.append(omega0)
        self.parameters.append(omega1)

        self.delay = hwconfig.adc_response_latency


    def generate_response_pulse(self, chan_signal: List[float], measurement: int = 0) -> np.ndarray:
        """
        Generate resonator response to an input signal.

        Parameters
        ----------
            chan_signal : List[float]
                Input signal from the channel
            measurement : int, optional
                Measurement value (0 or 1), defaults to 0

        Returns
        -------
            np.ndarray
                Resonator response signal
        """
        if measurement == 0:
            sqrt_term = self.parameters[0]
            amp = self.parameters[1]
            w = self.parameters[3]
            epsilon = 0.01 * amp
            time_length = max((int)((2*self.quality_factor/w) * np.log(amp / epsilon) * 16), len(chan_signal))
            t = np.arange(time_length) / 16
            if time_length > len(chan_signal):
                pad = np.zeros(time_length - len(chan_signal))
                chan_signal = np.concatenate((chan_signal, pad))
            h = amp * np.exp(-w * t/(2 * self.quality_factor)) * np.sin(w * sqrt_term * t)
            convolution = np.convolve(h, chan_signal, 'full')
        elif measurement == 1:
            sqrt_term = self.parameters[0]
            amp = self.parameters[2]
            w = self.parameters[4]
            epsilon = 0.01 * amp
            time_length = max((int)((2*self.quality_factor/w) * np.log(amp / epsilon) * 16), len(chan_signal))
            t = np.arange(time_length) / 16
            if time_length > len(chan_signal):
                pad = np.zeros(time_length - len(chan_signal))
                chan_signal = np.concatenate((chan_signal, pad))
            h = amp * np.exp(-w * t/(2 * self.quality_factor)) * np.sin(w * sqrt_term * t)
            convolution = np.convolve(h, chan_signal, 'full')
        else:
            raise ValueError(f"Invalid measurement value: measurement = {measurement}")
        
        return convolution


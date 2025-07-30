"""Module for channel simulation in quantum circuits.

This module provides the Channel class for generating and managing RF pulses
during quantum circuit simulation.
"""

from typing import Optional
import numpy as np
import distproc.asmparse as ps
from emulator.config.channel_config import ChannelConfig
from emulator.config.hardware_config import HWConfig
import emulator.parsers.command_parser as cp
from emulator.data.rf_sim_data import RFSimData
from emulator.channels.channel import Channel

class RFChannel(Channel):
    """Channel for generating RF pulses in quantum circuits.

    This class represents a signal-generating channel controlled by a core.
    It handles pulse generation, visualization, and data export to VCD files.

    Attributes
    ----------
    amp_normalization_factor : int
        Factor to normalize amplitudes (2^15 - 1 = 32767)
    phase_normalization_factor : float
        Factor to convert phase integers to radians (π/2^16)
    fpga_clk_freq : int
        FPGA clock frequency in Hz
    cordic_delay : int
        FPGA-specific CORDIC calculation latency in clock cycles
    phasein_delay : int
        FPGA-specific phase input latency in clock cycles
    qclk_delay : int
        FPGA-specific quarter clock latency in clock cycles
    cstrobe_delay : int
        FPGA-specific clock strobe latency in clock cycles
    phase_rst_delay : int
        FPGA-specific phase reset latency in clock cycles
    chanconfig : ChannelConfig
        Channel configuration parameters
    name : str
        Unique channel identifier
    sim_data : SimData
        Simulation data for the channel
    env_buffer : Optional[np.ndarray]
        Envelope buffer data
    freq_buffer : Optional[np.ndarray]
        Frequency buffer data
    """

    def __init__(self, name: str, chanconfig: ChannelConfig,
                hwconfig: HWConfig) -> None:
        """Initialize a new channel instance.

        Parameters
        ----------
        name : str
            Unique channel identifier
        chanconfig : ChannelConfig
            Channel configuration parameters
        hwconfig : HWConfig
            Hardware configuration object
        """
        self.amp_normalization_factor = 32767
        self.phase_normalization_factor = np.pi / 65536
        self.fpga_clk_freq = hwconfig.freq
        self.chanconfig = chanconfig

        self.cordic_delay = hwconfig.cordic_delay
        self.phasein_delay = hwconfig.phasein_delay
        self.qclk_delay = hwconfig.qclk_delay
        self.cstrobe_delay = hwconfig.cstrobe_delay
        self.phase_rst_delay = hwconfig.phase_rst_delay

        self.name = name
        self.env_buffers = []
        self.freq_buffers = []
        delay = self.cstrobe_delay + self.qclk_delay + self.phasein_delay - self.phase_rst_delay
        self.sim_data = RFSimData(self.name,
                                  self.chanconfig.elem_params['samples_per_clk'],
                                  self.chanconfig.elem_params['interp_ratio'],
                                  self.fpga_clk_freq,
                                  delay)



    def load_env_buffer(self, env_bin: bytes) -> None:
        """Load envelope buffer data.

        Parameters
        ----------
        env_bin : bytes
            Binary envelope data
        """
        if len(env_bin) != 0:
            parsed_array = ps.envparse(env_bin)
            for val in parsed_array:
                assert val / self.amp_normalization_factor <= 1, "Envelope must be normalized"
            self.env_buffers.append(parsed_array)


    def load_freq_buffer(self, freq_bin: bytes) -> None:
        """Load frequency buffer data.

        Parameters
        ----------
        freq_bin : bytes
            Binary frequency data
        """
        self.freq_buffers.append(cp.parse_freq(freq_bin, self.fpga_clk_freq))


    def add_pulse(self, freq: int, amp: int, phase: int, tstart: int,
                 twidth: int, env: int) -> None:
        """Add a pulse to the channel.

        Parameters
        ----------
        freq : int
            Pulse frequency
        amp : int
            Pulse amplitude
        phase : int
            Pulse phase
        tstart : int
            Start time in clock cycles
        twidth : int
            Pulse width in clock cycles
        env : int
            Envelope identifier
        """
        amp /= self.amp_normalization_factor
        freq = self.freq_buffers[freq]
        phase *= self.phase_normalization_factor
        env = self.env_buffers[env] / self.amp_normalization_factor
        self.sim_data.add_pulse(amp, freq, phase, env, tstart, twidth)


    def resolve(self, time: Optional[int] = None) -> None:
        """Resolve channel data up to the given time.

        Parameters
        ----------
        time : Optional[int], optional
            Time to resolve to, defaults to None (use current time)
        """
        return self.sim_data.resolve(time)


    def end_sim(self) -> None:
        """End the current simulation and finalize data."""
        return_env_buffers = list(self.env_buffers)
        return_freq_buffers = list(self.freq_buffers)

        self.env_buffers = []
        self.freq_buffers = []

        return self.sim_data, return_env_buffers, return_freq_buffers


    def reset(self) -> None:
        """Reset the channel state."""
        delay = self.cstrobe_delay + self.qclk_delay + self.phasein_delay - self.phase_rst_delay
        self.sim_data = RFSimData(self.name,
                        self.chanconfig.elem_params['samples_per_clk'],
                        self.chanconfig.elem_params['interp_ratio'],
                        self.fpga_clk_freq,
                        delay)


    def get_real_freq(self, freq_id: int) -> int:
        """Get actual frequency from frequency ID.

        Parameters
        ----------
        freq_id : int
            Frequency identifier

        Returns
        -------
        int
            Actual frequency value
        """
        iq = self.freq_buffers[freq_id]['iq15'][0]
        angles = []

        for offset in iq:
            r = offset.real
            i = offset.imag

            if r == 0 and i > 0: # + y-axis
                angles.append((float)(np.pi/2))
            elif r == 0 and i < 0: # - y-axis
                angles.append((float)(np.pi/2))
            elif i == 0 and r < 0: # - x-axis
                angles.append(np.pi)
            elif i == 0 and r > 0: # + x-axis
                angles.append(0.0)
            elif r < 0 and i < 0: #QIII
                angles.append((float)(np.arctan(i/r) * (180/np.pi) + 180))
            elif r < 0 and i > 0: #QII
                angles.append((float)(np.arctan(i/r) * (180/np.pi) + 180))
            elif r > 0 and i < 0: #QIV
                angles.append((float)(np.arctan(i/r) * (180/np.pi) + 360))
            else: #QI
                angles.append((float)(np.arctan(i/r) * (180/np.pi)))
        cycles = 0
        for i in range(0, len(angles) - 1):
            if (angles[i+1] - angles[i]) < 0:
                cycles += 1
        return cycles * 500e6 + self.freq_buffers[freq_id]['freq'][0]

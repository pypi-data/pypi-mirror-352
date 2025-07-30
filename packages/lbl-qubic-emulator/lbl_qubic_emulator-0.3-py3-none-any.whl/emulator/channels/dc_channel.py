"""DC channel module for quantum circuit emulation.

This module provides the DCChannel class for handling direct current signal
generation and processing in quantum circuit simulations. It implements the
Channel interface for DC-specific functionality, managing voltage levels and
DC pulse generation.
"""

from typing import Optional
from emulator.config.channel_config import ChannelConfig
from emulator.config.hardware_config import HWConfig
from emulator.channels.channel import Channel
from emulator.data.dc_sim_data import DCSimData

class DCChannel(Channel):
    """Direct current (DC) channel implementation for quantum circuit emulation.

    This class handles DC signal generation and processing in the quantum circuit
    emulator. It manages voltage levels, DC pulse generation, and signal simulation
    for DC channels, providing a simplified interface compared to RF channels.

    Attributes
    ----------
    amp_normalization_factor : int
        Factor used to normalize amplitude values (32767)
    fpga_clk_freq : float
        FPGA clock frequency in Hz
    chanconfig : ChannelConfig
        Channel configuration parameters
    name : str
        Name of the DC channel
    sim_data : DCSimData
        Simulation data container for DC signals
    """

    def __init__(self, name: str, chanconfig: ChannelConfig, hwconfig: HWConfig) -> None:
        """Initialize a new DC channel instance.

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
        self.fpga_clk_freq = hwconfig.freq
        self.chanconfig = chanconfig
        self.name = name

        self.sim_data = DCSimData(self.name, 0, 0, self.fpga_clk_freq, 0)

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
        self.sim_data.add_pulse(amp, None, None, None, tstart, None)

    def load_env_buffer(self, env_bin: bytes) -> None:
        """Load envelope buffer data.

        Parameters
        ----------
        env_bin : bytes
            Binary envelope data
        """
        raise NotImplementedError("DC channels do not support envelope buffers")

    def load_freq_buffer(self, freq_bin: bytes) -> None:
        """Load frequency buffer data.

        Parameters
        ----------
        freq_bin : bytes
            Binary frequency data
        """
        raise NotImplementedError("DC channels do not support frequency buffers")

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
        return_env_buffers = []
        return_freq_buffers = []

        return self.sim_data, return_env_buffers, return_freq_buffers

    def reset(self) -> None:
        """Reset the channel state."""
        self.sim_data = DCSimData(self.name, 0, 0, self.fpga_clk_freq, 0)


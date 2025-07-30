"""Abstract base class for channel implementations in the quantum emulator.

This module provides the Channel abstract base class that defines the interface
for all channel implementations in the quantum emulator system.
"""
from abc import ABC, abstractmethod
from typing import Optional
from emulator.config.channel_config import ChannelConfig
from emulator.config.hardware_config import HWConfig

class Channel(ABC):
    """Abstract base class for channel implementations in the emulator.
    
    This class defines the interface that all channel implementations must follow,
    including methods for loading buffers, adding pulses, and managing simulation state.
    """
    @abstractmethod
    def __init__(
        self,
        name: str,
        chanconfig: ChannelConfig,
        hwconfig: HWConfig
    ) -> None:
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

    @abstractmethod
    def load_env_buffer(self, env_bin: bytes) -> None:
        """Load envelope buffer data.

        Parameters
        ----------
        env_bin : bytes
            Binary envelope data
        """

    @abstractmethod
    def load_freq_buffer(self, freq_bin: bytes) -> None:
        """Load frequency buffer data.

        Parameters
        ----------
        freq_bin : bytes
            Binary frequency data
        """

    @abstractmethod
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

    @abstractmethod
    def resolve(self, time: Optional[int] = None) -> None:
        """Resolve channel data up to the given time.

        Parameters
        ----------
        time : Optional[int], optional
            Time to resolve to, defaults to None (use current time)
        """

    @abstractmethod
    def end_sim(self) -> None:
        """End the current simulation and finalize data."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the channel state."""

"""Channel configuration module for quantum circuit emulation.

This module provides configuration classes for managing quantum channel parameters,
including memory assignments and element parameters for the emulator.
"""
import json

class ChannelConfig:
    """Configuration handler for quantum channel parameters and memory assignments.

    Attributes
    ----------
    channels : dict
        Dictionary of channel configurations indexed by channel name
    """

    def __init__(self, filepath):
        """Initialize channel configuration from a JSON file.

        Parameters
        ----------
        filepath : str
            Path to the channel configuration JSON file

        Raises
        ------
        ValueError
            If filepath is empty or if there's an error loading the configuration
        """
        if filepath == "":
                raise ValueError("Channel configuration path is empty.")
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                chanconfig = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Unable to load channel configuration: {e}") from e
        
        self.channels = {}
        for name, channel in chanconfig.items():
             if name != 'fpga_clk_freq':
                self.channels[name] = IndividualChannelConfig()
                if 'elem_type' in channel:
                    self.channels[name].elem_type = channel["elem_type"]
                else:
                    raise ValueError("elem_type is not specified in the channel configuration")
                if self.channels[name].elem_type == 'rf':
                    if 'env_mem_name' in channel:
                        self.channels[name].env_mem_name = channel["env_mem_name"]
                    else:
                        raise ValueError("env_mem_name is not specified in the channel configuration")
                    if 'freq_mem_name' in channel:
                        self.channels[name].freq_mem_name = channel["freq_mem_name"]
                    else:
                        raise ValueError("freq_mem_name is not specified in the channel configuration")
                if 'core_ind' in channel:
                    self.channels[name].core_ind = channel["core_ind"]
                else:
                    raise ValueError("core_ind is not specified in the channel configuration")
                if 'elem_ind' in channel:
                    self.channels[name].elem_ind = channel["elem_ind"]
                else:
                    raise ValueError("elem_ind is not specified in the channel configuration")
                if 'core_name' in channel:
                    self.channels[name].core_name = channel["core_name"]
                else:
                    raise ValueError("core_name is not specified in the channel configuration")
                if 'elem_params' in channel:
                    self.channels[name].elem_params = channel["elem_params"]
                else:
                    raise ValueError("elem_params is not specified in the channel configuration")


class IndividualChannelConfig:
    """Configuration for a single quantum channel with memory and element parameters.

    Attributes
    ----------
    core_ind : int
        Index of the core this channel belongs to
    elem_ind : int
        Element index within the core
    core_name : str
        Name of the core this channel is assigned to
    env_mem_name : str
        Name of the envelope memory for RF channels
    freq_mem_name : str
        Name of the frequency memory for RF channels
    elem_type : str
        Type of the element (e.g., 'rf')
    elem_params : dict
        Additional element-specific parameters
    """

    def __init__(self):
        """Initialize an empty channel configuration."""
        self.core_ind = None
        self.elem_ind = None
        self.core_name = None
        self.env_mem_name = None
        self.freq_mem_name = None
        self.elem_type = None
        self.elem_params = None

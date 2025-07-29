"""Buffer parser module for quantum circuit emulation.

This module provides functionality to decode machine code buffers used in the emulator.
It handles the parsing of envelope, frequency, and command buffers from executables,
converting them into instructions for the quantum cores.
"""
from distproc.executable import Executable
import emulator.parsers.command_parser as cp
from emulator.config.channel_config import ChannelConfig


def decode(executable: Executable | bytes, cores: list, chanconfig: ChannelConfig) -> None:
    """Decode executable binaries into core instructions and channel data.

    This function processes the executable's binary data, converting it into:
    - Envelope buffers for signal channels
    - Frequency buffers for signal channels
    - Command buffers for quantum cores

    Parameters
    ----------
    executable : Executable | bytes
        The executable object or raw bytes containing program binaries
    cores : list
        List of quantum cores from the ProcessorEmulator
    chanconfig : ChannelConfig
        Channel configuration object containing channel parameters
    """
    envelope_buffers = []
    env_length = {}
    binaries = executable if isinstance(executable, bytes) else executable.program_binaries

    # Process each binary buffer
    for buffer_key, buffer_data in binaries.items():
        # Skip empty buffers
        if len(buffer_data) == 0:
            continue

        # Handle envelope buffers
        if 'env' in buffer_key:
            envelope_buffers.append(buffer_key)
            continue

        # Handle frequency buffers
        if 'freq' in buffer_key:
            _process_frequency_buffer(buffer_key, buffer_data, cores, chanconfig)
            continue

        # Handle command buffers
        if 'command' in buffer_key:
            _process_command_buffer(buffer_key, buffer_data, cores, env_length)
            continue

    # Process envelope buffers after command parsing
    _process_envelope_buffers(envelope_buffers, env_length, binaries, cores, chanconfig)


def _process_frequency_buffer(
    buffer_key: str,
    buffer_data: bytes,
    cores: list,
    chanconfig: ChannelConfig
) -> None:
    """Process a frequency buffer and load it onto the appropriate channel.

    Parameters
    ----------
    buffer_key : str
        Key identifying the frequency buffer
    buffer_data : bytes
        Binary frequency data
    cores : list
        List of quantum cores
    chanconfig : ChannelConfig
        Channel configuration object
    """
    # Extract core and channel information from buffer key
    core_type, chan_type, core_num = _extract_core_channel_info(buffer_key)
    core_name = _format_core_name(core_type, core_num)
    chan_name = _format_channel_name(core_type, chan_type, core_num)

    # Validate buffer length
    samples_per_clk = chanconfig.channels[chan_name].elem_params['samples_per_clk']
    if len(buffer_data) % (4 * samples_per_clk) != 0:
        raise ValueError(
            f"Binary data must be a multiple of {4 * samples_per_clk} bytes, "
            f"length of byte string in {buffer_key} is {len(buffer_data)}"
        )

    # Split and process frequency data
    frequencies = [
        buffer_data[i*(4*samples_per_clk):(i+1)*(4*samples_per_clk)]
        for i in range(len(buffer_data) // 4 // samples_per_clk)
    ]
    for freq in frequencies:
        cores[core_name].add_channel_freq_buffer(chan_name, freq)


def _process_command_buffer(
    buffer_key: str,
    buffer_data: bytes,
    cores: list,
    env_length: dict
) -> None:
    """Process a command buffer and load commands onto the appropriate core.

    Parameters
    ----------
    buffer_key : str
        Key identifying the command buffer
    buffer_data : bytes
        Binary command data
    cores : list
        List of quantum cores
    env_length : dict
        Dictionary tracking envelope lengths
    """
    if len(buffer_data) % 16 != 0:
        raise ValueError(
            f"Binary data must be a multiple of 16 bytes, "
            f"length of byte string in {buffer_key} is {len(buffer_data)}"
        )

    # Extract core information and process commands
    core_type = buffer_key[buffer_key.find(':') + 1:buffer_key.find('_')]
    core_num = int(buffer_key[-1])
    core_name = _format_core_name(core_type, core_num)

    # Process each command
    commands = [buffer_data[i:i+16] for i in range(0, len(buffer_data), 16)]
    mem_to_env_map = {}
    for cmd in commands:
        parsed_cmd = cp.parse_cmd(cmd)
        # Track envelope lengths for pulse commands
        if parsed_cmd['op'] == 'pulse_write_trig':
            length_key = f"{core_num}{core_type}{parsed_cmd['cfg']}"
            if length_key not in env_length:
                env_length[length_key] = []
            if length_key not in mem_to_env_map:
                mem_to_env_map[length_key] = {}
            if parsed_cmd['env'] not in mem_to_env_map[length_key]:
                mem_to_env_map[length_key][parsed_cmd['env']] = len(mem_to_env_map[length_key])
                parsed_cmd['env'] = mem_to_env_map[length_key][parsed_cmd['env']]
                env_length[length_key].append(parsed_cmd['env_len'])
            else:
                parsed_cmd['env'] = mem_to_env_map[length_key][parsed_cmd['env']]

        cores[core_name].commands.append(parsed_cmd)


def _process_envelope_buffers(
    envelope_buffers: list,
    env_length: dict,
    binaries: dict,
    cores: list,
    chanconfig: ChannelConfig
) -> None:
    """Process envelope buffers and load them onto the appropriate channels.

    Parameters
    ----------
    envelope_buffers : list
        List of envelope buffer keys
    env_length : dict
        Dictionary of envelope lengths
    binaries : dict
        Dictionary of binary data
    cores : list
        List of quantum cores
    chanconfig : ChannelConfig
        Channel configuration object
    """
    # Channel type to configuration mapping
    chan_to_cfg = {
        'qdrv': 0,
        'rdrv': 1,
        'rdlo': 2,
        'cdrv': 0,
        'dc': 1,
        'qdrv2': 0
    }

    for buffer_key in envelope_buffers:
        # Extract core and channel information
        core_type, chan_type, core_num = _extract_core_channel_info(buffer_key)
        core_name = _format_core_name(core_type, core_num)
        chan_name = _format_channel_name(core_type, chan_type, core_num)

        # Get channel configuration
        channel_type = buffer_key[buffer_key.find('_', buffer_key.find(':')) + 1:
                                buffer_key.find('_', buffer_key.find('_') + 1)]
        channel_cfg = chan_to_cfg[channel_type]
        length_key = f"{core_num}{core_type}{channel_cfg}"

        # Process envelope data
        start_index = 0
        for length in env_length[length_key]:
            # If length is 0, CW pulse
            if length == 0:
                length = 4 * chanconfig.channels[chan_name].elem_params['samples_per_clk']
                length //= chanconfig.channels[chan_name].elem_params['interp_ratio']
            else:
                # Calculate actual buffer length
                length *= 4 * chanconfig.channels[chan_name].elem_params['samples_per_clk']
                length //= chanconfig.channels[chan_name].elem_params['interp_ratio']
            
            # Extract and load envelope buffer
            env_buffer = binaries[buffer_key][start_index:start_index + length]
            cores[core_name].add_channel_env_buffer(chan_name, env_buffer)
            start_index += length


def _extract_core_channel_info(buffer_key: str) -> tuple[str, str, int]:
    """Extract core type, channel type, and core number from a buffer key.

    Parameters
    ----------
    buffer_key : str
        Buffer key to parse

    Returns
    -------
    tuple[str, str, int]
        Core type, channel type, and core number
    """
    start_idx = buffer_key.find(':') + 1
    end_idx = buffer_key.find('_')
    core_type = buffer_key[start_idx:end_idx]
    chan_type = buffer_key[end_idx+1:buffer_key.find('_', end_idx+1)]
    core_num = int(buffer_key[-1])
    return core_type, chan_type, core_num


def _format_core_name(core_type: str, core_num: int) -> str:
    """Format a core name based on its type and number.

    Parameters
    ----------
    core_type : str
        Type of the core (e.g., 'qubit', 'drive')
    core_num : int
        Core number

    Returns
    -------
    str
        Formatted core name
    """
    prefix = 'Q' if core_type in ['qubit', 'drive'] else 'C'
    return f"{prefix}{core_num}.{core_type}"


def _format_channel_name(core_type: str, chan_type: str, core_num: int) -> str:
    """Format a channel name based on core and channel information.

    Parameters
    ----------
    core_type : str
        Type of the core
    chan_type : str
        Type of the channel
    core_num : int
        Core number

    Returns
    -------
    str
        Formatted channel name
    """
    prefix = 'Q' if core_type in ['qubit', 'drive'] else 'C'
    chan_name = f"{prefix}{core_num}.{chan_type}"
    if 'drive' in core_type:
        chan_name += '2'
    return chan_name

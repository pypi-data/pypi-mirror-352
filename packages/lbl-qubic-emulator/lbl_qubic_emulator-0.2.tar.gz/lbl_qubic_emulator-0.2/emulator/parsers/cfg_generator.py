"""Configuration generator module for quantum circuit emulation.

This module provides functionality to generate emulator-specific configuration files
from various hardware and qubit configuration sources. It handles the conversion of
DSP configurations, channel assignments, and qubit parameters into formats suitable
for the emulator.
"""
import json
from typing import Dict, List, Union, Any
import yaml
import distproc.hwconfig as hw
from distproc.hwconfig import load_channel_configs


def create_hwconfig(
    write_path: str,
    chanconfig: Union[str, Dict[str, Any]],
    dspcfg_path: str,
    fpgaconfig: hw.FPGAConfig
) -> None:
    """Generate emulator-specific hardware configuration JSON file.

    Takes information from pre-existing hardware config files and extracts only the
    necessary information for the emulator. The resulting configuration is written
    to a JSON file at the specified path.

    Parameters
    ----------
    write_path : str
        Path where the configuration JSON file will be written
    chanconfig : Union[str, Dict[str, Any]]
        Either a path to a channel configuration JSON file or a dictionary
        containing the configuration
    dspcfg_path : str
        Path to the DSP configuration YAML file
    fpgaconfig : hw.FPGAConfig
        FPGA configuration object containing timing parameters

    Raises
    ------
    ValueError
        If any of the input parameters are invalid or if there's an error loading
        the configuration files
    """
    _validate_inputs(write_path, chanconfig, dspcfg_path, fpgaconfig)

    # Load channel configuration if path is provided
    if isinstance(chanconfig, str):
        if not chanconfig:
            raise ValueError("Channel configuration path is empty")
        try:
            chanconfig = load_channel_configs(chanconfig)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Unable to load channel configuration: {e}") from e

    active_channels = list(chanconfig.keys())
    dac_assignments = parse_dac_assignments(dspcfg_path, active_channels)
    adc_assignments = parse_adc_assignments(dspcfg_path, active_channels)

    # Prepare configuration dictionaries
    dac_dict = _create_indexed_dict(dac_assignments)
    adc_dict = _create_indexed_dict(adc_assignments)
    fpga_dict = _create_fpga_dict(fpgaconfig, chanconfig)

    # Combine all configurations
    config_dict = {
        'num_dacs': len(dac_dict),
        'dacs': dac_dict,
        'num_adcs': len(adc_dict),
        'adcs': adc_dict,
        'fpga': fpga_dict,
        'fproc_measurement_latency': 3,
        'adc_response_latency': 1,
    }

    # Write configuration to file
    with open(write_path, 'w', encoding="utf-8") as json_file:
        json.dump(config_dict, json_file, indent=4)


def _validate_inputs(
    write_path: str,
    chanconfig: Union[str, Dict[str, Any]],
    dspcfg_path: str,
    fpgaconfig: hw.FPGAConfig
) -> None:
    """Validate input parameters for create_hwconfig.

    Parameters
    ----------
    write_path : str
        Output file path
    chanconfig : Union[str, Dict[str, Any]]
        Channel configuration
    dspcfg_path : str
        DSP configuration path
    fpgaconfig : hw.FPGAConfig
        FPGA configuration object

    Raises
    ------
    ValueError
        If any input parameter is invalid
    """
    if not isinstance(write_path, str):
        raise ValueError(f"Output file path must be a string, got {type(write_path)}")
    if not isinstance(chanconfig, (str, dict)):
        raise ValueError(f"Chanconfig must be a string or dict, got {type(chanconfig)}")
    if not isinstance(dspcfg_path, str):
        raise ValueError(f"DSP config path must be a string, got {type(dspcfg_path)}")
    if not isinstance(fpgaconfig, hw.FPGAConfig):
        raise ValueError(f"FPGA Config must be a hwconfig.FPGAConfig object, got {type(fpgaconfig)}")


def _create_indexed_dict(assignments: List[List[str]]) -> Dict[str, List[str]]:
    """Create a dictionary from a list of assignments, filtering out empty lists.

    Parameters
    ----------
    assignments : List[List[str]]
        List of channel assignments

    Returns
    -------
    Dict[str, List[str]]
        Dictionary mapping indices to non-empty channel lists
    """
    return {
        str(index): channels
        for index, channels in enumerate(assignments)
        if channels
    }


def _create_fpga_dict(
    fpgaconfig: hw.FPGAConfig,
    chanconfig: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FPGA configuration dictionary.

    Parameters
    ----------
    fpgaconfig : hw.FPGAConfig
        FPGA configuration object
    chanconfig : Dict[str, Any]
        Channel configuration dictionary

    Returns
    -------
    Dict[str, Any]
        FPGA configuration dictionary
    """
    return {
        'alu_instr_clks': fpgaconfig.alu_instr_clks,
        'jump_cond_clks': fpgaconfig.jump_cond_clks,
        'jump_fproc_clks': fpgaconfig.jump_fproc_clks,
        'pulse_regwrite_clks': fpgaconfig.pulse_regwrite_clks,
        'pulse_load_clks': fpgaconfig.pulse_load_clks,
        "cordic_delay": 47,
        "phasein_delay": 1,
        "qclk_delay": 4,
        "cstrobe_delay": 2,
        "phase_rst_delay": 9,
        "freq": chanconfig['fpga_clk_freq'],
        "num_cores": 15
    }


def create_qubitconfig(write_path: str, qubitcfg_path: str) -> None:
    """Create emulator-specific qubit configuration file.

    Generates a configuration file from the qubit configuration used for compilation
    in the QChip object.

    Parameters
    ----------
    write_path : str
        Path where the configuration JSON file will be written
    qubitcfg_path : str
        Path to the qubit configuration JSON file

    Raises
    ------
    FileNotFoundError
        If the qubit configuration path is empty
    ValueError
        If there's an error loading or parsing the configuration file
    """
    if not qubitcfg_path:
        raise FileNotFoundError("Qubit configuration path is empty")

    try:
        with open(qubitcfg_path, 'r', encoding="utf-8") as file:
            qubitconfig = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Unable to load qubit configuration: {e}") from e

    qubits_to_write = {}
    resonators_to_write = {}
    qubits = qubitconfig["Qubits"]

    for qubit, data in qubits.items():
        if qubit[0] != 'Q':
            continue

        # Process qubit data
        qubits_to_write[qubit] = {
            "freq": data["freq"],
            "readfreq": data["readfreq"],
            "Omega": qubitconfig["Gates"][f"{qubit}X90"][0]["amp"]
        }

        # Process resonator data
        resonator = f"R{qubit[1]}"
        resonators_to_write[resonator] = {
            "Q": 3500,
            "resonant_frequency_0": data.get("readfreq0", data["readfreq"]),
            "resonant_frequency_1": data.get("readfreq1", data["readfreq"])
        }

    config_dict = {
        "num_qubits": len(qubits_to_write),
        "qubits": qubits_to_write,
        "resonators": resonators_to_write
    }

    with open(write_path, 'w', encoding="utf-8") as json_file:
        json.dump(config_dict, json_file, indent=4)


def parse_dac_assignments(filename: str, active_channels: List[str]) -> List[List[str]]:
    """Parse DAC assignments from DSP configuration YAML.

    Parameters
    ----------
    filename : str
        Path to the DSP configuration YAML file
    active_channels : List[str]
        List of active channel names to validate assignments

    Returns
    -------
    List[List[str]]
        List of channel assignments for each DAC

    Raises
    ------
    ValueError
        If an invalid DAC output command is encountered
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    dac_cmds = data['dac_outputs']
    dacs = [[] for _ in range(16)]

    for cmd in dac_cmds:
        if 'gen' in cmd:
            _process_gen_cmd(cmd, dacs, active_channels)
        elif 'sum' in cmd:
            _process_sum_cmd(cmd, dacs, active_channels, data['cores'])
        else:
            raise ValueError(f"Invalid DAC output command: {cmd}")

    return dacs


def _process_gen_cmd(
    cmd: Dict[str, Any],
    dacs: List[List[str]],
    active_channels: List[str]
) -> None:
    """Process a generator command for DAC assignments.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Generator command dictionary
    dacs : List[List[str]]
        List of DAC assignments to update
    active_channels : List[str]
        List of active channel names
    """
    range_str = cmd['gen']['range']
    expr = cmd['gen']['expr'].replace(' ', '')

    # Parse range
    lower, upper = map(int, range_str.split(','))

    # Parse expression
    lhs = expr[:expr.find('<=')]
    rhs = expr[expr.find('<=')+2:]

    # Process each index in range
    for i in range(lower, upper):
        dac_index = _process_string_addition(lhs.replace('i', str(i)))
        channels = parse_gen_rhs(rhs, i)
        dacs[dac_index] = [ch for ch in channels if ch in active_channels]

def _process_string_addition(line: str) -> int:
    """Process a string addition command for DAC assignments.

    Parameters
    ----------
    line : str
        String addition command
    """
    parts = line.split('+')
    numbers = [int(part.strip()) for part in parts]
    return sum(numbers)

def _process_sum_cmd(
    cmd: Dict[str, Any],
    dacs: List[List[str]],
    active_channels: List[str],
    cores: Dict[str, int]
) -> None:
    """Process a sum command for DAC assignments.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Sum command dictionary
    dacs : List[List[str]]
        List of DAC assignments to update
    active_channels : List[str]
        List of active channel names
    cores : Dict[str, int]
        Core configuration dictionary
    """
    # Calculate range
    num_cores = sum(cores.values())
    if 'range' in cmd['sum']:
        lower, upper = map(int, cmd['sum']['range'].split(','))
    else:
        lower, upper = 0, num_cores

    # Extract channel type
    chan_type = cmd['sum']['sig_gens'].split('.')[-1]

    # Collect channels
    summed_channels = []
    for i in range(lower, upper):
        prefix = 'Q' if 'qubit' in cmd['sum']['sig_gens'] else 'C'
        suffix = '2' if 'drive' in cmd['sum']['sig_gens'] else ''
        chan = f"{prefix}{i}.{chan_type}{suffix}"
        if chan in active_channels:
            summed_channels.append(chan)

    dacs[cmd['sum']['dac_ind']] = summed_channels


def parse_gen_rhs(line: str, index: int) -> List[str]:
    """Parse generator function right hand side and compute channels.

    Parameters
    ----------
    line : str
        Generator function right hand side expression
    index : int
        Current index in the range

    Returns
    -------
    List[str]
        List of channel names

    Raises
    ------
    ValueError
        If an unknown core type is encountered
    """
    channels = []
    terms = line.split('+')

    for term in terms:
        core_type = term[:term.find('.')]
        chan_type = term[term.find('.')+1:term.find('[')]
        core_num = int(term[term.find('[')+1:term.find(']')].replace('i', str(index)))

        if core_type == 'qubit':
            channels.append(f"Q{core_num}.{chan_type}")
        elif core_type == 'drive':
            channels.append(f"Q{core_num}.{chan_type}2")
        elif core_type == 'coupler':
            channels.append(f"C{core_num}.{chan_type}")
        else:
            raise ValueError(f"Unknown core type: {core_type}")

    return channels


def parse_adc_assignments(filename: str, active_channels: List[str]) -> List[List[str]]:
    """Parse ADC assignments from DSP configuration YAML.

    Parameters
    ----------
    filename : str
        Path to the DSP configuration YAML file
    active_channels : List[str]
        List of active channel names to validate assignments

    Returns
    -------
    List[List[str]]
        List of channel assignments for each ADC
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    adc_cmds = data['adc_mix_inputs']
    adcs = [[] for _ in range(16)]

    for cmd in adc_cmds:
        if 'gen' in cmd:
            _process_adc_gen_cmd(cmd, adcs, active_channels)

    return adcs


def _process_adc_gen_cmd(
    cmd: Dict[str, Any],
    adcs: List[List[str]],
    active_channels: List[str]
) -> None:
    """Process a generator command for ADC assignments.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Generator command dictionary
    adcs : List[List[str]]
        List of ADC assignments to update
    active_channels : List[str]
        List of active channel names
    """
    var = cmd['gen']['var']
    range_str = cmd['gen']['range'].replace(' ', '')
    expr = cmd['gen']['expr'].replace(' ', '')

    # Parse range and expression
    lower, upper = map(int, range_str.split(','))
    lhs = expr[:expr.find('<=')]
    rhs = expr[expr.find('<=')+2:]

    # Process each index
    for i in range(lower, upper):
        channels = parse_gen_lhs(lhs, i)
        adc_index = _process_string_addition(rhs.replace(var, str(i)))
        adcs[adc_index].extend(ch for ch in channels if ch in active_channels)


def parse_gen_lhs(line: str, index: int) -> List[str]:
    """Parse generator function left hand side and compute channels.

    Parameters
    ----------
    line : str
        Generator function left hand side expression
    index : int
        Current index in the range

    Returns
    -------
    List[str]
        List of channel names

    Raises
    ------
    ValueError
        If an unknown core type is encountered
    """
    channels = []
    terms = line.split('+')

    for term in terms:
        core_type = term[:term.find('.')]
        chan_type = term[term.find('.')+1:term.find('[')]
        core_num = int(term[term.find('[')+1:term.find(']')].replace('i', str(index)))

        if core_type == 'qubit':
            channels.append(f"Q{core_num}.{chan_type}")
        elif core_type == 'drive':
            channels.append(f"Q{core_num}.{chan_type}2")
        elif core_type == 'coupler':
            channels.append(f"C{core_num}.{chan_type}")
        else:
            raise ValueError(f"Unknown core type: {core_type}")

    return channels

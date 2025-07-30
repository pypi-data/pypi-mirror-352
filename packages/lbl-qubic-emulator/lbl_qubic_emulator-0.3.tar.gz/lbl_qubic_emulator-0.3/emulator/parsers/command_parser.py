"""Command parser module for quantum circuit emulation.

This module provides functionality to parse binary commands and frequency buffers
used in the quantum circuit emulator. It handles the conversion of binary data
into structured command dictionaries and frequency parameters.
"""
from typing import Dict, Any, Union
import numpy as np
import distproc.asmparse as ps
from distproc.command_gen import opcodes, alu_opcodes


def parse_cmd(binary_data: bytes) -> Dict[str, Any]:
    """Parse a 128-bit binary command into a structured dictionary.

    This function decodes the binary command data into a dictionary containing
    operation parameters. The decoding process depends on the opcode found in
    the first 5 bits of the command.

    Parameters
    ----------
    binary_data : bytes
        16-byte sequence containing the command information

    Returns
    -------
    Dict[str, Any]
        Dictionary containing command parameters with keys:
        - 'op': Operation code
        - Other keys depend on the operation type

    Raises
    ------
    ValueError
        If an invalid operation is encountered
    """
    cmd = {}
    flipped = bytearray(binary_data)[::-1]
    bitstring = ''.join(f"{byte:08b}" for byte in flipped)

    cmd['op'] = get_opcode(int(bitstring[:5], 2))

    if cmd['op'] in ('pulse_write', 'pulse_write_trig'):
        _parse_pulse_command(cmd, bitstring)
    elif cmd['op'] in ('reg_alu_i', 'reg_alu'):
        _parse_alu_command(cmd, bitstring)
    elif cmd['op'] in ('jump_i', 'jump_cond_i', 'jump_cond'):
        _parse_jump_command(cmd, bitstring)
    elif cmd['op'] in ('alu_fproc', 'alu_fproc_i'):
        _parse_fproc_command(cmd, bitstring)
    elif cmd['op'] in ('jump_fproc_i', 'jump_fproc'):
        _parse_jump_fproc_command(cmd, bitstring)
    elif cmd['op'] in ('inc_qclk_i', 'inc_qclk'):
        _parse_qclk_command(cmd, bitstring)
    elif cmd['op'] == 'sync':
        cmd['sync_barrier_id'] = int(bitstring[8:16], 2)
    elif cmd['op'] == 'idle':
        cmd['idle_time'] = int(bitstring[8:123], 2)
    elif cmd['op'] in ('done', 'pulse_reset'):
        pass
    else:
        raise ValueError(f"Invalid operation: {cmd['op']}")

    return cmd


def _parse_pulse_command(cmd: Dict[str, Any], bitstring: str) -> None:
    """Parse pulse command parameters.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Command dictionary to update
    bitstring : str
        Binary string representation of the command
    """
    pulse_reg = int(bitstring[8:12], 2)
    cmd['env_select'] = int(bitstring[12:13], 2)
    cmd['env_ri'] = int(bitstring[13:14], 2)
    cmd['env_len'] = int(bitstring[14:26], 2)
    cmd['env'] = int(bitstring[26:38], 2)

    # Parse phase parameters
    cmd['phase_select'] = int(bitstring[38:39], 2)
    cmd['phase_ri'] = int(bitstring[39:40], 2)
    cmd['phase'] = pulse_reg if cmd['phase_ri'] else int(bitstring[40:57], 2)

    # Parse frequency parameters
    cmd['freq_select'] = int(bitstring[57:58], 2)
    cmd['freq_ri'] = int(bitstring[58:59], 2)
    cmd['freq'] = pulse_reg if cmd['freq_ri'] else int(bitstring[59:68], 2)

    # Parse amplitude parameters
    cmd['amp_select'] = int(bitstring[68:69], 2)
    cmd['amp_ri'] = int(bitstring[69:70], 2)
    cmd['amp'] = pulse_reg if cmd['amp_ri'] else int(bitstring[70:86], 2)

    cmd['cfg'] = int(bitstring[87:91], 2)
    if cmd['op'] == 'pulse_write_trig':
        cmd['start_time'] = int(bitstring[91:123], 2)


def _parse_alu_command(cmd: Dict[str, Any], bitstring: str) -> None:
    """Parse ALU command parameters.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Command dictionary to update
    bitstring : str
        Binary string representation of the command
    """
    cmd['alu_op'] = get_alu_opcode(int(bitstring[5:8], 2))
    if cmd['op'] == 'reg_alu_i':
        cmd['in0_i'] = int(bitstring[8:40], 2)
    else:
        cmd['in0_reg'] = int(bitstring[8:12], 2)
    cmd['in1_reg'] = int(bitstring[40:44], 2)
    cmd['out_reg'] = int(bitstring[44:48], 2)


def _parse_jump_command(cmd: Dict[str, Any], bitstring: str) -> None:
    """Parse jump command parameters.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Command dictionary to update
    bitstring : str
        Binary string representation of the command
    """
    if cmd['op'] != 'jump_i':
        cmd['alu_op'] = get_alu_opcode(int(bitstring[5:8], 2))
        if cmd['op'] == 'jump_cond_i':
            cmd['in0_i'] = int(bitstring[8:40], 2)
        else:
            cmd['in0_reg'] = int(bitstring[8:12], 2)
        cmd['in1_reg'] = int(bitstring[40:44], 2)
    cmd['jump_label'] = int(bitstring[44:60], 2)


def _parse_fproc_command(cmd: Dict[str, Any], bitstring: str) -> None:
    """Parse function processor command parameters.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Command dictionary to update
    bitstring : str
        Binary string representation of the command
    """
    cmd['alu_op'] = get_alu_opcode(int(bitstring[5:8], 2))
    if cmd['op'] == 'alu_fproc_i':
        cmd['in0_i'] = int(bitstring[8:40], 2)
    else:
        cmd['in0_reg'] = int(bitstring[8:12], 2)
    cmd['out_reg'] = int(bitstring[44:48], 2)
    cmd['func_id'] = int(bitstring[60:76], 2)


def _parse_jump_fproc_command(cmd: Dict[str, Any], bitstring: str) -> None:
    """Parse jump function processor command parameters.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Command dictionary to update
    bitstring : str
        Binary string representation of the command
    """
    cmd['alu_op'] = get_alu_opcode(int(bitstring[5:8], 2))
    if cmd['op'] == 'jump_fproc_i':
        cmd['in0_i'] = int(bitstring[8:40], 2)
    else:
        cmd['in0_reg'] = int(bitstring[8:12], 2)
    cmd['jump_label'] = int(bitstring[44:60], 2)
    cmd['func_id'] = int(bitstring[60:76], 2)


def _parse_qclk_command(cmd: Dict[str, Any], bitstring: str) -> None:
    """Parse quantum clock command parameters.

    Parameters
    ----------
    cmd : Dict[str, Any]
        Command dictionary to update
    bitstring : str
        Binary string representation of the command
    """
    if cmd['op'] == 'inc_qclk_i':
        cmd['time_duration_i'] = twos_complement_to_int(bitstring[8:40])
    else:
        cmd['time_duration_reg'] = int(bitstring[8:12], 2)


def get_opcode(opcode: int) -> str:
    """Get the string representation of an opcode.

    Parameters
    ----------
    opcode : int
        Decimal representation of the first 5 bits of a command

    Returns
    -------
    str
        String representing the opcode

    Raises
    ------
    ValueError
        If the opcode is not found
    """
    for name, code in opcodes.items():
        if code == opcode:
            return name
    raise ValueError(f"Unknown opcode: {opcode}")


def get_alu_opcode(opcode: int) -> str:
    """Get the string representation of an ALU opcode.

    Parameters
    ----------
    opcode : int
        Decimal representation of bits 6-8 of an ALU command

    Returns
    -------
    str
        String representing the ALU opcode

    Raises
    ------
    ValueError
        If the ALU opcode is not found
    """
    for name, code in alu_opcodes.items():
        if code == opcode:
            return name
    raise ValueError(f"Unknown ALU opcode: {opcode}")


def parse_freq(
    binary_data: bytes,
    fsamp: float = 500e6
) -> Dict[str, Union[float, np.ndarray]]:
    """Parse frequency buffer data into frequency and IQ offset values.

    Parameters
    ----------
    binary_data : bytes
        Assembled frequency buffer from assembler
    fsamp : float, optional
        Sampling frequency (FPGA clock frequency), default 500MHz

    Returns
    -------
    Dict[str, Union[float, np.ndarray]]
        Dictionary containing:
        - 'freq': float representing frequency modulo fsamp
        - 'iq15': numpy array of IQ offset values
    """
    dt = np.dtype(np.uint32).newbyteorder('little')
    freq_data = np.frombuffer(binary_data, dtype=dt)

    total_values = len(freq_data)
    iq_offsets = total_values - 1
    freq16 = freq_data.reshape([-1, iq_offsets + 1])
    freq = freq16[:, 0] / 2**32 * fsamp

    iq15r = ps.vsign16((freq16[:, 1:].astype(np.int32) >> 16) & 0xffff)
    iq15i = ps.vsign16(freq16[:, 1:].astype(np.int32) & 0xffff)
    return {'freq': freq, 'iq15': iq15r + 1j * iq15i}


def twos_complement_to_int(bitstring: str) -> int:
    """Convert a two's complement bitstring to an integer.

    Parameters
    ----------
    bitstring : str
        String of 1s and 0s representing an integer in two's complement

    Returns
    -------
    int
        The integer value represented by the bitstring
    """
    n = len(bitstring)
    value = int(bitstring, 2)
    if bitstring[0] == '1':
        value -= (1 << n)
    return value

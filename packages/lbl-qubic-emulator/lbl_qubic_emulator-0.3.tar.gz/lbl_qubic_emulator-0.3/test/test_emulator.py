import sys
import os

import pytest
import numpy as np
import ipdb
import yaml
import distproc.asmparse as parse
import distproc.assembler as asm 
import distproc.compiler as cm
import distproc.hwconfig as hw
from distproc.hwconfig import FPGAConfig
import qubic.toolchain as tc
import qubitconfig.qchip as qc
from distproc.compiler import CompilerFlags

parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_folder)

import qubic.rfsoc.hwconfig as rf
from emulator.emulator import Emulator

# Input any circuit
def test_circuit(circuit: list, graph: list = []):
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    
    #edit
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    """compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=None, compiler_flags={'resolve_gates': False},
                                        proc_grouping=[('{qubit}.qdrv', '{qubit}.rdrv', '{qubit}.rdlo'),
                                                    ('{qubit}.qdrv2',),
                                                    ('{qubit}.cdrv', '{qubit}.dc')]) # Resolve gates = false, dont give it the qchip"""
    compiled_prog = tc.run_compile_stage(circuit, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)

    # print(binary.program_binaries)
    em = Emulator("./test/config/channel_config.json",
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)

    result = em.execute(tags=[],toggle_resonator=True)
    for name in graph:
        result.graph_channel(name)
    result.graph_dac('DAC0') # rdrv channels belong to 0th dac
    result.graph_adc('ADC0')
    result.graph_iq()


circuit = [{'name': 'pulse', 'phase': 0, 'freq': 6553826000.000857, 'amp': 1, 'twidth': 1e-6,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.15}},
                'dest': 'Q0.rdrv'},
        {'name': 'pulse', 'phase': 0, 'freq': 6553826000.000857, 'amp': 1, 'twidth': 1e-6,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.15}},
                'dest': 'Q0.rdlo'}]



test_circuit(circuit, graph=['Q0.rdlo'])
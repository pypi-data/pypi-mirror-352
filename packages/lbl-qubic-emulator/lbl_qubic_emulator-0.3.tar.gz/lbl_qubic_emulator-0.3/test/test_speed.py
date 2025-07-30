import sys
import os
import distproc.hwconfig as hw
from distproc.hwconfig import FPGAConfig
import qubic.toolchain as tc
import qubitconfig.qchip as qc
from distproc.compiler import CompilerFlags
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_folder)
from emulator.emulator import Emulator
import timeit
import matplotlib.pyplot as plt
import numpy as np

# Input any circuit
def test_x90_speed():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [{'name': 'X90', 'qubit': 'Q0'}, {'name': 'X90', 'qubit': 'Q0'}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")

def test_sweep_speed():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [
        {'name': 'declare', 'var': 'loop_ind', 'scope': ['Q0']},
        {'name': 'set_var', 'value': 0, 'var': 'loop_ind'},
        {'name': 'declare', 'var': 'amp', 'scope': ['Q0'], 'dtype': 'amp'},
        {'name': 'set_var', 'value': 0.1, 'var': 'amp'}, # pulse amplitude is parameterized by processor register
        {'name': 'loop', 'cond_lhs': 10, 'alu_cond': 'ge', 'cond_rhs': 'loop_ind', 'scope': ['Q0'], 
        'body': [
                {'name': 'pulse', 'phase': 0, 'freq': 310e6, 'amp': 'amp', 'twidth': 2.4e-08,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.25}},
                'dest': 'Q0.qdrv'},
            {'name': 'alu', 'op': 'add', 'lhs': 1, 'rhs': 'loop_ind', 'out': 'loop_ind'},
            {'name': 'alu', 'op': 'add', 'lhs': 0.1, 'rhs': 'amp', 'out': 'amp'}
        ]}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    # print(binary.program_binaries)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute(toggle_qubits=True)
    sim_data = result.get_channel_data("Q0.qdrv")


def test_simul_pulse_speed():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [{'name': 'X90', 'qubit': 'Q0'},
            {'name': 'pulse', 'freq': 100.e6, 'phase': 0, 'twidth': 50.e-9,
             'amp': 0.5, 'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.1}}
             , 'dest': 'Q0.qdrv2'}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip,
                                         proc_grouping=[('{qubit}.qdrv', '{qubit}.rdrv', '{qubit}.rdlo'),
                                                        ('{qubit}.qdrv2',),
                                                        ('{qubit}.cdrv', '{qubit}.dc')])
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_dac_data("DAC0")


def test_two_rdrv_speed():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [{'name': 'X90', 'qubit': 'Q0'},
            {'name': 'barrier', 'qubit': 'Q0'},
            {'name': 'pulse', 'dest': 'Q0.rdrv', 'twidth': 100.e-9, 'amp': 0.5,
             'freq': 5.127e9, 'phase': 0, 'env': np.ones(50)},
            {'name': 'pulse', 'dest': 'Q2.rdrv', 'twidth': 100.e-9, 'amp': 0.5,
             'freq': 6.227e9, 'phase': 0, 'env': {'env_func': 'cos_edge_square', 
                                                  'paradict': {'ramp_fraction': 0.25}}}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    result.graph_dac('DAC7')

def test_long_delay_speed():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [{'name': 'delay', 't': 500e-6},
            {'name': 'X90', 'qubit': 'Q0'}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")
    #result.graph_channel('Q0.qdrv')

def test_hundred_pulses():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [
        {'name': 'declare', 'var': 'loop_ind', 'scope': ['Q0']},
        {'name': 'set_var', 'value': 0, 'var': 'loop_ind'},
        {'name': 'loop', 'cond_lhs': 100, 'alu_cond': 'ge', 'cond_rhs': 'loop_ind', 'scope': ['Q0'], 
        'body': [
                {'name': 'pulse', 'phase': 0, 'freq': 310e6, 'amp': 0.5, 'twidth': 2.4e-08,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.25}},
                'dest': 'Q0.qdrv'},
            {'name': 'alu', 'op': 'add', 'lhs': 1, 'rhs': 'loop_ind', 'out': 'loop_ind'}
        ]}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")

def test_thousand_pulses():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [
        {'name': 'declare', 'var': 'loop_ind', 'scope': ['Q0']},
        {'name': 'set_var', 'value': 0, 'var': 'loop_ind'},
        {'name': 'loop', 'cond_lhs': 1000, 'alu_cond': 'ge', 'cond_rhs': 'loop_ind', 'scope': ['Q0'], 
        'body': [
                {'name': 'pulse', 'phase': 0, 'freq': 310e6, 'amp': 0.5, 'twidth': 2.4e-08,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.25}},
                'dest': 'Q0.qdrv'},
            {'name': 'alu', 'op': 'add', 'lhs': 1, 'rhs': 'loop_ind', 'out': 'loop_ind'}
        ]}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")

def test_two_thousand_pulses():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [
        {'name': 'declare', 'var': 'loop_ind', 'scope': ['Q0']},
        {'name': 'set_var', 'value': 0, 'var': 'loop_ind'},
        {'name': 'loop', 'cond_lhs': 2000, 'alu_cond': 'ge', 'cond_rhs': 'loop_ind', 'scope': ['Q0'], 
        'body': [
                {'name': 'pulse', 'phase': 0, 'freq': 310e6, 'amp': 0.5, 'twidth': 2.4e-08,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.25}},
                'dest': 'Q0.qdrv'},
            {'name': 'alu', 'op': 'add', 'lhs': 1, 'rhs': 'loop_ind', 'out': 'loop_ind'}
        ]}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")

def test_five_thousand_pulses():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [
        {'name': 'declare', 'var': 'loop_ind', 'scope': ['Q0']},
        {'name': 'set_var', 'value': 0, 'var': 'loop_ind'},
        {'name': 'loop', 'cond_lhs': 5000, 'alu_cond': 'ge', 'cond_rhs': 'loop_ind', 'scope': ['Q0'], 
        'body': [
                {'name': 'pulse', 'phase': 0, 'freq': 310e6, 'amp': 0.5, 'twidth': 2.4e-08,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.25}},
                'dest': 'Q0.qdrv'},
            {'name': 'alu', 'op': 'add', 'lhs': 1, 'rhs': 'loop_ind', 'out': 'loop_ind'}
        ]}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")

def test_ten_thousand_pulses():
    channel_config = hw.load_channel_configs('./test/config/channel_config.json')
    qchip = qc.QChip('./test/existing_config/qubitcfg.json')
    prog = [
        {'name': 'declare', 'var': 'loop_ind', 'scope': ['Q0']},
        {'name': 'set_var', 'value': 0, 'var': 'loop_ind'},
        {'name': 'loop', 'cond_lhs': 10, 'alu_cond': 'ge', 'cond_rhs': 'loop_ind', 'scope': ['Q0'], 
        'body': [
                {'name': 'pulse', 'phase': 0, 'freq': 432894573, 'amp': 0.5, 'twidth': 2.4e-08,
                'env': {'env_func': 'cos_edge_square', 'paradict': {'ramp_fraction': 0.25}},
                'dest': 'Q0.qdrv'},
            {'name': 'alu', 'op': 'add', 'lhs': 1, 'rhs': 'loop_ind', 'out': 'loop_ind'}
        ]}]
    compiled_prog = tc.run_compile_stage(prog, fpga_config=hw.FPGAConfig(), qchip=qchip)
    binary = tc.run_assemble_stage(compiled_prog, channel_config)
    em = Emulator("./test/config/channel_config.json", 
              "./test/config/hw_config.json",
              "./test/config/qubit_config.json")
    em.load_program(binary)
    result = em.execute()
    sim_data = result.get_channel_data("Q0.qdrv")


execution_time = timeit.timeit(test_x90_speed, number=1)
print("X90 Runtime:", execution_time)
execution_time = timeit.timeit(test_sweep_speed, number=1)
print("Sweep Runtime:", execution_time)
execution_time = timeit.timeit(test_simul_pulse_speed, number=1)
print("Simul Pulse Runtime:", execution_time)
execution_time = timeit.timeit(test_two_rdrv_speed, number=1)
print("Two Rdrv Runtime:", execution_time)
execution_time = timeit.timeit(test_long_delay_speed, number=1)
print("Long Delay Runtime:", execution_time)
execution_time = timeit.timeit(test_hundred_pulses, number=1)
print("100 Pulses Runtime:", execution_time)
execution_time = timeit.timeit(test_thousand_pulses, number=1)
print("1000 Pulses Runtime:", execution_time)
execution_time = timeit.timeit(test_two_thousand_pulses, number=1)
print("2000 Pulses Runtime:", execution_time)
execution_time = timeit.timeit(test_five_thousand_pulses, number=1)
print("5000 Pulses Runtime:", execution_time)
execution_time = timeit.timeit(test_ten_thousand_pulses, number=1)
print("10000 Pulses Runtime:", execution_time)


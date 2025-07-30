# QubiC Distributed Processor Emulator

A tool for emulating the signal generation and instruction execution of QubiC 2.0's FPGA based distributed processor. Takes binaries of assembled instructions that would be fed to the distributed processor, parses the commands, and executes clock accurate RF pulse generation, ALU instructions, jump instructions, etc. Pulses can then be graphed, and execution order of instructions can be viewed. Options for simulating the effect on the QPU for educational purposes, such as the readout resonator response and the evolution of the qubit state.

# Dependencies
- [distproc](https://gitlab.com/LBL-QubiC/distributed_processor)
- [qubitconfig](https://gitlab.com/LBL-QubiC/experiments/qubitconfig)
- numpy
- matplotlib
- pyvcd
- pyyaml
- scipy
- qutip

The [software](https://gitlab.com/LBL-QubiC/software) repository is not a dependency for the Emulator package, but is required if users want to compile and assemble their high level circuit code into machine code that is usable in the emulator.

# Tutorial
A tutorial jupyter notebook can be found in the [tutorial folder](https://gitlab.com/LBL-QubiC/qubic_emulator/-/tree/main/tutorial?ref_type=heads) within the repository. The notebook will walk through the process of creating an Emulator object and the steps to be taken to generate simulations.

# Testing
To test new additions to the emulator, use the Cocotb folder (instructions included), or unzip the `npz_files.zip` file in the `test/test_suite folder`, and run `pytest test_suite` while in the test directory.

# Paper
A paper about the emulator can be found in the [repository](https://gitlab.com/LBL-QubiC/qubic_emulator/-/blob/main/SULI_Spring%202025_Paper_Mills_Jeremy.pdf?ref_type=heads). Paper was created during the Spring 2025 term, and outlines program architecture, background information, performance, etc.

# Poster
A poster presentation for the emulator package can be found in the [repository](https://gitlab.com/LBL-QubiC/qubic_emulator/-/blob/main/SULI_Spring%202025_Poster_Mills_Jeremy.pdf?ref_type=heads). Poster was created during the Spring 2025 SULI term.

# Documentation
HTML Documentation can be found in [/docs/_build/html](https://gitlab.com/LBL-QubiC/qubic_emulator/-/tree/main/docs/_build/html?ref_type=heads).
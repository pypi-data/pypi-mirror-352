"""QubiC emulator module for quantum circuit simulation.

This module provides the Emulator class, which handles the simulation of quantum
circuits using the QubiC architecture. It manages configuration loading, program
execution, and qubit state simulation.
"""

import json
from typing import List, Union, Any
from distproc.executable import Executable
import distproc.hwconfig as hw
from emulator.hardware.distributed_processor import DistributedProcessor
from emulator.hardware.function_processor import FunctionProcessor
from emulator.data.result import Result
import emulator.parsers.cfg_generator as cfg
from emulator.config.hardware_config import HWConfig
from emulator.config.channel_config import ChannelConfig
from emulator.config.qubit_config import QubitConfig
import qutip as qt


class Emulator:
    """Main QubiC emulator class for quantum circuit simulation.

    This class manages the entire QubiC emulation process, including configuration
    loading, program execution, and qubit state simulation.

    Attributes
    ----------
    dist_proc : DistributedProcessor
        Processor for executing FPGA-level instructions, handling pulse simulation,
        qubit simulation, and resonator simulation
    func_proc : FunctionProcessor
        Processor for storing measurements and values for circuit branching
    manual_fproc : bool
        Whether to use manual function processor instructions instead of automatic
        qubit measurements
    """

    def __init__(self, chanconfig_path: str = "", hwconfig_path: str = "", qubitconfig_path: str = "") -> None:
        """Initialize the QubiC emulator.

        Parameters
        ----------
        chanconfig_path : str, optional
            Path to channel configuration JSON file
        hwconfig_path : str, optional
            Path to hardware configuration JSON file
        qubitconfig_path : str, optional
            Path to qubit configuration JSON file

        Raises
        ------
        FileNotFoundError
            If any configuration file is not found
        json.JSONDecodeError
            If any configuration file has invalid JSON
        """
        chanconfig = ChannelConfig(chanconfig_path)
        hwconfig = HWConfig(hwconfig_path)
        qubitconfig = QubitConfig(qubitconfig_path)

        self.dist_proc = DistributedProcessor(chanconfig, hwconfig, qubitconfig)
        self.func_proc = FunctionProcessor(hwconfig.fproc_measurement_latency)
        self.manual_fproc = True

    @staticmethod
    def generate_hwcfg(write_path: str,
                       chancfg_path: str,
                       dspcfg_path: str,
                       fpgaconfig: hw.FPGAConfig) -> None:
        """Generate hardware configuration file.

        Parameters
        ----------
        write_path : str
            Path to write the configuration file
        chancfg_path : str
            Path to channel configuration file
        dspcfg_path : str
            Path to DSP configuration file
        fpgaconfig : hw.FPGAConfig
            FPGA configuration object
        """
        cfg.create_hwconfig(write_path, chancfg_path, dspcfg_path, fpgaconfig)

    @staticmethod
    def generate_qubitcfg(write_path: str, qubitcfg_path: str) -> None:
        """Generate qubit configuration file.

        Parameters
        ----------
        write_path : str
            Path to write the configuration file
        qubitcfg_path : str
            Path to qubit configuration file
        """
        cfg.create_qubitconfig(write_path, qubitcfg_path)

    def define_dac(self, dac_id: int, channel_names: List[str],
                   hwconfig: str, qubitconfig: str) -> None:
        """Manually define a DAC and its channel assignments.

        Parameters
        ----------
        dac_id : int
            DAC index (0-15)
        channel_names : List[str]
            List of channel names to assign to the DAC

        Raises
        ------
        AssertionError
            If DAC ID is invalid or channel names are invalid
        """
        assert (isinstance(dac_id, int)), f"DAC ID must be an integer, got {type(dac_id)}"
        assert (0 <= dac_id <= 15), f"DAC ID must be [0, 15], got {dac_id}"
        assert (isinstance(channel_names, list)), (
            f"Channel names must be a list, got {type(channel_names)}"
        )
        for channel_name in channel_names:
            assert (isinstance(channel_name, str)), (
                f"Channel name must be a string, got {type(channel_name)}"
            )
        if hwconfig == "":
            raise ValueError("Hardware configuration path is empty.")
        else:
            try:
                with open(hwconfig, 'r', encoding="utf-8") as file:
                    hwconfig = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise ValueError(f"Unable to load hardware configuration: {e}") from e

        if qubitconfig == "":
            raise ValueError("Qubit configuration path is empty.")
        try:
            with open(qubitconfig, 'r', encoding="utf-8") as file:
                qubitconfig = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Unable to load qubit configuration: {e}") from e
        self.dist_proc.define_dac(dac_id, channel_names, hwconfig, qubitconfig)

    def define_adc(self, adc_id: int, channel_names: List[str]) -> None:
        """Manually define an ADC and its channel assignments.

        Parameters
        ----------
        adc_id : int
            ADC index (0-15)
        channel_names : List[str]
            List of channel names to assign to the ADC

        Raises
        ------
        AssertionError
            If ADC ID is invalid or channel names are invalid
        """
        assert (isinstance(adc_id, int)), f"ADC ID must be an integer, got {type(adc_id)}"
        assert (0 <= adc_id <= 15), f"ADC ID must be [0, 15], got {adc_id}"
        assert (isinstance(channel_names, list)), (
                f"Channel names must be a list, got {type(channel_names)}"
        )
        for channel_name in channel_names:
            assert (isinstance(channel_name, str)), (
                    f"Channel name must be a string, got {type(channel_name)}"
            )
        self.dist_proc.define_adc(adc_id, channel_names)

    def which_dac(self, chan: str) -> str:
        """Find DAC assigned to a channel.

        Parameters
        ----------
        chan : str
            Channel name to look up

        Returns
        -------
        str
            Name of the DAC assigned to the channel

        Raises
        ------
        AssertionError
            If channel is not assigned to any DAC
        """
        for dac in self.dist_proc.dacs:
            if chan in list(dac.channels.keys()):
                return dac.name
        raise AssertionError(f"Channel {chan} not assigned to any DAC")

    def set_qubit_state(self, qubit: str, state: Union[int, qt.Qobj]) -> None:
        """Set initial state of a qubit before simulation.

        Parameters
        ----------
        qubit : str
            Qubit name (e.g., "Q0")
        state : Union[int, qt.Qobj]
            Initial state to set (0, 1, or custom Qobj)

        Raises
        ------
        AssertionError
            If state is invalid or qubit not found
        """
        assert (isinstance(state, (int, qt.Qobj))), f"State must be int or Qobj, got {type(state)}"
        if isinstance(state, int):
            assert (state in (0, 1)), f"Integer state must be 0 or 1, got {state}"
        if isinstance(state, qt.Qobj):
            assert (state.dim == [[2], [1]]), f"Qobj must have dimensions [[2], [1]], got {state}"

        for name, qb in self.dist_proc.qubits.items():
            if qubit == name:
                if isinstance(state, int):
                    qb.curr_state = qt.basis(2, state)
                else:
                    qb.curr_state = state
                return
        raise AssertionError(f"Qubit {qubit} not found")

    def load_program(self, assembled_prog: Union[Executable, bytes]) -> None:
        """Load program into the distributed processor.

        Parameters
        ----------
        assembled_prog : Union[Executable, bytes]
            Program machine code to load

        Raises
        ------
        AssertionError
            If program type is invalid
        """
        assert (isinstance(assembled_prog, (Executable, bytes))), (
                f"Program must be Executable or bytes, got {type(assembled_prog)}"
        )
        self.dist_proc.load_program(assembled_prog)

    def load_fproc(self, fproc_instr: List[Any]) -> None:
        """Load manual function processor instructions.

        This overrides automatic qubit measurements with manual instructions for
        inserting values into the function processor.

        Parameters
        ----------
        fproc_instr : List[Any]
            List of instructions, each containing:
            - core: Core taking the measurement
            - meas: Measurement sequence number (1-indexed)
            - value: Value to place in function processor
            - time: Optional auto-resolved time

        Raises
        ------
        AssertionError
            If instructions are invalid
        """
        assert(isinstance(fproc_instr, list)), (
            f"Instructions must be a list, got {type(fproc_instr)}"
        )
        self.manual_fproc = True
        for instr in fproc_instr:
            assert('core' in instr), (
                f"Instructions must specify core: {instr}"
            )
            assert('meas' in instr or 'time' in instr), (
                f"Instructions must have 'meas' or 'time': {instr}"
            )
            assert('value' in instr), (
                f"Instructions must have 'value': {instr}"
            )
        self.func_proc.read_instructions(fproc_instr)

    def execute(self, tags: str | list=None, toggle_resonator: bool=False, toggle_qubits: bool=False, prog: Executable | bytes=None) -> Result:
        """
        Executes the simulation with the instructions currently loaded. Returns
        a Result object with the simulation data.

        Parameters
        ----------
            tags : str | list
                The tags that will determine if anything will be printed during the
                simulation. The valid tags are 'DEBUG', which will print out every
                command ran, 'REG', which will print out the registers after every
                command call, and 'FPROC', which will print out the function processor
                values after a value has been updated. Invalid tags will not do anything
            toggle_resonator : bool
                Toggles whether to simulate resonators
            toggle_qubits : bool
                Toggles whether to simulate qubits
            prog : Executable | bytes
                Program to execute

        Return
        ----------
            result : Result
                The Result object with all of the simulation data
        """
        if tags is None:
            tags = []
        assert(isinstance(tags, list) or isinstance(tags, str)), f"Execution tags must be a list or string, tags: {type(tags)}"
        assert(isinstance(toggle_resonator, bool)), f"toggle_resonator must be a boolean, type(toggle_resonator): {type(toggle_resonator)}"
        assert(isinstance(toggle_qubits, bool)), f"toggle_qubits must be a boolean, type(toggle_qubits): {type(toggle_qubits)}"

        if isinstance(tags, str):
            tags = [tags]
        if prog is not None:
            self.load_program(prog)
        
        if toggle_resonator:
            toggle_qubits = True
        self.manual_fproc = not toggle_resonator
        result = self.dist_proc.execute(self.func_proc, self.manual_fproc, toggle_qubits, tags)
        self.func_proc.clear()
        self.manual_fproc = True
        return result

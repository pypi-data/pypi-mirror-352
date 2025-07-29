"""Core module for distributed processor pulse instruction execution.

This module contains the Core class, which represents a single core on the distributed
processor used for executing pulse instructions. Each core manages multiple channels
and handles pulse generation, ALU operations, and jump instructions.
"""

from typing import Dict, List, Optional, Any, NamedTuple
from emulator.channels.rf_channel import Channel
from emulator.hardware.function_processor import FunctionProcessor
from emulator.channels.dc_channel import DCChannel
from emulator.channels.rf_channel import RFChannel
from emulator.hardware.qubit import Qubit
from emulator.config.hardware_config import HWConfig
from emulator.config.channel_config import ChannelConfig


class CommandResult(NamedTuple):
    """Result of a command execution.

    Attributes
    ----------
    is_done : bool
        Whether the simulation is done
    measurement_taken : bool
        Whether a measurement was taken
    command : Optional[Dict[str, Any]]
        The command that was executed
    """
    is_done: bool
    measurement_taken: bool
    command: Optional[Dict[str, Any]]


class Core:
    """Single core on the distributed processor.

    A core controls multiple channels and runs simulations with pulse generation,
    ALU operations, and jump instructions.

    Attributes
    ----------
    alu_instr_clks : int
        Number of clock cycles for an ALU instruction
    jump_cond_clks : int
        Number of clock cycles for a jump condition instruction
    jump_fproc_clks : int
        Number of clock cycles for a jump condition using the function processor
    pulse_regwrite_clks : int
        Number of clock cycles for a pulse register write instruction
    pulse_load_clks : int
        Number of clock cycles to load a pulse
    name : str
        Unique name of the core, containing core type and index information
    channels : Dict[str, Channel]
        Dictionary mapping channel types to Channel objects controlled by this core
    reg : List[int]
        List of register values (maximum 16 values)
    commands : List[Dict[str, Any]]
        List of commands to be executed during simulation
    curr_sim_data : CoreSimData
        Object storing current simulation state information:
        - current_time: Current simulation time
        - pulse_time: Time for pulse generation logic
        - current_cmd: Current command index
        - pulse_cooldown: Cooldown timers for each channel
        - pulse_readtime: Read time for each channel
        - alu_cooldown: ALU operation cooldown
        - active_pulse: Whether a pulse is currently active
        - done: Whether simulation is complete
    pulse_register : PulseRegister
        Object storing pulse register values:
        - freq: Frequency value
        - amp: Amplitude value
        - phase: Phase value
        - env: Envelope value
        - cfg: Channel configuration value

    Parameters
    ----------
    name : str
        Unique name of the core
    chanconfig : Dict[str, Any]
        Channel configuration dictionary
    hwconfig : HWConfig
        Hardware configuration object
    """

    def __init__(self, name: str, chanconfig: Dict[str, ChannelConfig],
                hwconfig: HWConfig) -> None:
        """Initialize a new core with the given configuration.

        Parameters
        ----------
        name : str
            Unique name of the core
        chanconfig : dict
            Dictionary mapping channel names to individual channel configurations
        hwconfig : HWConfig
            Hardware configuration object

        Raises
        ------
        ValueError
            If invalid channel element type is encountered
        """
        # Hardware configurations
        self.alu_instr_clks = hwconfig.alu_instr_clks
        self.jump_cond_clks = hwconfig.jump_cond_clks
        self.jump_fproc_clks = hwconfig.jump_fproc_clks
        self.pulse_regwrite_clks = hwconfig.pulse_regwrite_clks
        self.pulse_load_clks = hwconfig.pulse_load_clks

        self.name = name
        self.channels = {}
        for key in chanconfig:
            if chanconfig[key].elem_type == 'rf':
                self.channels[key] = RFChannel(key, chanconfig[key], hwconfig)
            elif chanconfig[key].elem_type == 'dc':
                self.channels[key] = DCChannel(key, chanconfig[key], hwconfig)
            else: # Add more element types here in the future
                raise ValueError(
                    f"Invalid channel element type, elem_type: {chanconfig[key].elem_type}"
                )

        self.reg = [0 for _ in range(16)]
        self.commands = []
        self.curr_sim_data = CoreSimData(len(self.channels))
        self.pulse_register = PulseRegister()

    def reset_channels(self) -> None:
        """Reset all channels controlled by this core."""
        for _, channel in self.channels.items():
            channel.reset()

    def execute_current(self, fproc: FunctionProcessor, qubits: Dict[str, Qubit],
                       sim_qubits: bool, tags: Optional[List[str]] = None) -> CommandResult:
        """Execute the current command in the simulation.

        Parameters
        ----------
        fproc : FunctionProcessor
            Function processor for executing commands
        qubits : Dict[str, Qubit]
            Dictionary of qubits in the system
        sim_qubits : bool
            Whether to simulate qubit behavior
        tags : Optional[List[str]], optional
            List of tags for the current command, defaults to None

        Returns
        -------
        CommandResult
            Result of the command execution containing:
            - is_done: Whether the simulation is done
            - measurement_taken: Whether a measurement was taken
            - command: The command that was executed
        """
        if tags is None:
            tags = []
        if not self.commands:
            self.curr_sim_data.done = True
            return CommandResult(True, False, None)

        debug_tag = True if 'DEBUG' in tags else False
        register_tag = True if 'REGISTER' in tags else False

        cmd = self.commands[self.curr_sim_data.current_cmd]
        start_cmd = self.curr_sim_data.current_cmd
        cmd_ran = False
        meas_taken = False
        if cmd['op'] == 'pulse_write_trig':
            self.curr_sim_data.pulse_readtime[cmd['cfg']] += 1
            if cmd['start_time'] < self.curr_sim_data.pulse_time:
                raise ValueError(
                    f"Current time is greater than pulse start time, "
                    f"pulse_time: {self.curr_sim_data.pulse_time}, "
                    f"start_time: {cmd['start_time']}"
                )
            elif cmd['start_time'] > self.curr_sim_data.pulse_time:
                cmd_ran = False # Do Nothing
            elif (self.curr_sim_data.pulse_cooldown[cmd['cfg']] != 0 and
                  cmd['start_time'] == self.curr_sim_data.pulse_time):
                raise RuntimeError(f"Pulse being generated in cfg: {cmd['cfg']}")
            elif self.curr_sim_data.pulse_readtime[cmd['cfg']] < 3:
                raise RuntimeError(
                    f"Pulses need 3 clock cycles from being loaded to execute properly, "
                    f"clocks: {self.curr_sim_data.pulse_readtime[cmd['cfg']]}"
                )
            elif (cmd['freq'] is not None and cmd['phase'] is not None and
                  cmd['freq'] is not None and cmd['env'] is not None):
                

                if cmd['freq_select'] == 1:
                    if cmd['freq_ri'] == 1:
                        self.pulse_register.freq = self.reg[cmd['freq']]
                    else:
                        self.pulse_register.freq = cmd['freq']
                if cmd['amp_select'] == 1:
                    if cmd['amp_ri'] == 1:
                        self.pulse_register.amp = self.reg[cmd['amp']]
                    else:
                        self.pulse_register.amp = cmd['amp']
                if cmd['phase_select'] == 1:
                    if cmd['phase_ri'] == 1:
                        self.pulse_register.phase = self.reg[cmd['phase']]
                    else:
                        self.pulse_register.phase = cmd['phase']
                if cmd['env_select'] == 1:
                    if cmd['env_ri'] == 1:
                        self.pulse_register.env = self.reg[cmd['env']]
                    else:
                        self.pulse_register.env = cmd['env']


                if self.commands[self.curr_sim_data.current_cmd-1]['op'] == 'pulse_write':
                    prev_cmd = self.commands[self.curr_sim_data.current_cmd-1]
                    if prev_cmd['freq_ri'] == 1:
                        self.pulse_register.freq = self.reg[prev_cmd['freq']]
                    else:
                        self.pulse_register.freq = self.pulse_register.freq
                    if prev_cmd['amp_ri'] == 1:
                        self.pulse_register.amp = self.reg[prev_cmd['amp']]
                    else:
                        self.pulse_register.amp = self.pulse_register.amp
                    if prev_cmd['phase_ri'] == 1:
                        self.pulse_register.phase = self.reg[prev_cmd['phase']]
                    else:
                        self.pulse_register.phase = self.pulse_register.phase
                    if prev_cmd['env_ri'] == 1:
                        self.pulse_register.env = self.reg[prev_cmd['env']]
                    else:
                        self.pulse_register.env = self.pulse_register.env


                self.generate_pulse(
                    cmd['cfg'], self.pulse_register.freq, self.pulse_register.amp,
                    self.pulse_register.phase, self.curr_sim_data.current_time,
                    cmd['env_len'], self.pulse_register.env, qubits, sim_qubits
                )

                self.curr_sim_data.pulse_cooldown[cmd['cfg']] = max(3, cmd['env_len'])
                self.curr_sim_data.pulse_readtime[cmd['cfg']] = 0
                self.curr_sim_data.current_cmd += 1
                cmd_ran = True
                meas_taken = True if cmd['cfg'] == 1 else False
            else:
                pass
        elif cmd['op'] == 'pulse_write':
            self.curr_sim_data.current_cmd += 1
            self.curr_sim_data.pulse_cooldown[cmd['cfg']] = 3
            self.curr_sim_data.pulse_readtime[cmd['cfg']] = 0
            cmd_ran = True
        elif cmd['op'] == 'reg_alu_i' and self.curr_sim_data.alu_cooldown == 0:
            self.reg_alu(cmd['in0_i'], cmd['alu_op'], cmd['in1_reg'], cmd['out_reg'], False)
            self.curr_sim_data.alu_cooldown = self.alu_instr_clks
            self.curr_sim_data.current_cmd += 1
            cmd_ran = True
        elif cmd['op'] == 'reg_alu' and self.curr_sim_data.alu_cooldown == 0:
            self.reg_alu(cmd['in0_reg'], cmd['alu_op'], cmd['in1_reg'], cmd['out_reg'], True)
            self.curr_sim_data.alu_cooldown = self.alu_instr_clks
            self.curr_sim_data.current_cmd += 1
            cmd_ran = True
        elif cmd['op'] == 'jump_i':
            self.curr_sim_data.current_cmd = cmd['jump_label']
            cmd_ran = True
        elif cmd['op'] == 'jump_cond_i' and self.curr_sim_data.alu_cooldown == 0:
            self.curr_sim_data.current_cmd = self.jump_cond(cmd['in0_i'],
                                                               cmd['alu_op'],
                                                               cmd['in1_reg'],
                                                               cmd['jump_label'],
                                                               False,
                                                               self.curr_sim_data.current_cmd)
            self.curr_sim_data.alu_cooldown = self.jump_cond_clks
            cmd_ran = True
        elif cmd['op'] == 'jump_cond' and self.curr_sim_data.alu_cooldown == 0:
            self.curr_sim_data.current_cmd = self.jump_cond(cmd['in0_reg'],
                                                               cmd['alu_op'],
                                                               cmd['in1_reg'],
                                                               cmd['jump_label'],
                                                               True,
                                                               self.curr_sim_data.current_cmd)
            self.curr_sim_data.alu_cooldown = self.jump_cond_clks
            cmd_ran = True
        elif cmd['op'] == 'alu_fproc' and self.curr_sim_data.alu_cooldown == 0:
            self.alu_fproc(cmd['in0_reg'],
                           cmd['alu_op'],
                           cmd['out_reg'],
                           fproc.values[cmd['func_id']],
                           True,
                           fproc)
            self.curr_sim_data.alu_cooldown = self.alu_instr_clks
            self.curr_sim_data.current_cmd += 1
            cmd_ran = True
        elif cmd['op'] == 'alu_fproc_i' and self.curr_sim_data.alu_cooldown == 0:
            self.alu_fproc(cmd['in0_i'],
                           cmd['alu_op'],
                           cmd['out_reg'],
                           fproc.values[cmd['func_id']],
                           False,
                           fproc)
            self.curr_sim_data.alu_cooldown = self.alu_instr_clks
            self.curr_sim_data.current_cmd += 1
            cmd_ran = True
        elif (cmd['op'] == 'jump_fproc_i' and
              self.curr_sim_data.alu_cooldown == 0):
            self.curr_sim_data.current_cmd = self.jump_fproc(
                cmd['in0_i'],
                cmd['alu_op'],
                cmd['jump_label'],
                fproc.values[cmd['func_id']],
                False,
                self.curr_sim_data.current_cmd,
                fproc
            )
            self.curr_sim_data.alu_cooldown = self.jump_fproc_clks
            cmd_ran = True
        elif (cmd['op'] == 'jump_fproc' and 
              self.curr_sim_data.alu_cooldown == 0):
            self.curr_sim_data.current_cmd = self.jump_fproc(
                cmd['in0_reg'],
                cmd['alu_op'],
                cmd['jump_label'],
                fproc.values[cmd['func_id']],
                True,
                self.curr_sim_data.current_cmd,
                fproc
            )
            self.curr_sim_data.alu_cooldown = self.jump_fproc_clks
            cmd_ran = True
        elif cmd['op'] == 'inc_qclk_i' and self.curr_sim_data.alu_cooldown == 0:
            self.curr_sim_data.pulse_time += cmd['time_duration_i']
            self.curr_sim_data.alu_cooldown = self.alu_instr_clks
            cmd_ran = True
            self.curr_sim_data.current_cmd += 1
        elif cmd['op'] == 'inc_qclk':
            self.curr_sim_data.pulse_time += self.reg[cmd['time_duration_reg']]
            self.curr_sim_data.alu_cooldown = self.alu_instr_clks
            cmd_ran = True
            self.curr_sim_data.current_cmd += 1
        elif cmd['op'] == 'sync':
            pass
        elif (cmd['op'] == 'done' and
              not any(list(self.curr_sim_data.pulse_cooldown.values())) and
              self.curr_sim_data.alu_cooldown == 0):
            self.curr_sim_data.done = True
        elif cmd['op'] == 'pulse_reset':  # Phase reset
            self.curr_sim_data.current_cmd += 1
            cmd_ran = True
        elif cmd['op'] == 'idle' and self.curr_sim_data.pulse_time == cmd['idle_time']:
            self.curr_sim_data.current_cmd += 1
            cmd_ran = True
        self.curr_sim_data.current_time += 1
        self.curr_sim_data.pulse_time += 1
        self.curr_sim_data.alu_cooldown = max(0, self.curr_sim_data.alu_cooldown - 1)
        for cfg in self.curr_sim_data.pulse_cooldown:
            self.curr_sim_data.pulse_cooldown[cfg] = max(
                0, self.curr_sim_data.pulse_cooldown[cfg] - 1
            )

        if cmd_ran:
            if debug_tag:
                print(
                    f"COMMAND {start_cmd}: {cmd} WAS EXECUTED AT TIMESTAMP "
                    f"{self.curr_sim_data.current_time - 1}"
                )
            if register_tag:
                print(
                    f"REGISTERS AT TIMESTAMP {self.curr_sim_data.current_time}: "
                    f"{self.reg}"
                )

        return CommandResult(self.curr_sim_data.done, meas_taken, cmd)


    def resolve(self, channels: Dict[str, Channel], time: int) -> None:
        """Resolve channel states at the given time.

        Parameters
        ----------
        channels : Dict[str, Channel]
            Dictionary of channels to resolve
        time : int
            Current simulation time
        """
        for chan in channels:
            if chan in self.channels:
                self.channels[chan].resolve(time)


    def end_sim(self) -> None:
        """End the current simulation and reset core state."""
        chan_data = {}
        env_buffer = {}
        freq_buffer = {}
        for name, chan in self.channels.items():
            sim_data, chan_env_buffer, chan_freq_buffer = chan.end_sim()
            chan_data[name] = sim_data
            env_buffer[name] = chan_env_buffer
            freq_buffer[name] = chan_freq_buffer
            chan.reset()

        reg_data = list(self.reg)
        cmd_data = list(self.commands)
        self.reg = [0 for _ in range(16)]
        self.commands = []

        self.curr_sim_data.reset()
        self.pulse_register.reset()

        return chan_data, env_buffer, freq_buffer, reg_data, cmd_data


    def add_channel_env_buffer(self, chan: str, env_bin: bytes) -> None:
        """Add envelope buffer for a channel.

        Parameters
        ----------
        chan : str
            Channel identifier
        env_bin : bytes
            Binary envelope data
        """
        assert (chan in self.channels), f"Channel name does not exist, chan: {chan}"
        self.channels[chan].load_env_buffer(env_bin)


    def add_channel_freq_buffer(self, chan: str, freq_bin: bytes) -> None:
        """Add frequency buffer for a channel.

        Parameters
        ----------
        chan : str
            Channel identifier
        freq_bin : bytes
            Binary frequency data
        """
        assert (chan in self.channels), f"Channel name does not exist, chan: {chan}"
        self.channels[chan].load_freq_buffer(freq_bin)


    def generate_pulse(self, cfg: int, freq: int, amp: int, phase: int,
                      tstart: int, twidth: int, env: int, qubits: Dict[str, Qubit],
                      sim_qubits: bool) -> None:
        """Generate a pulse on the specified channel.

        Parameters
        ----------
        cfg : int
            Channel configuration
        freq : int
            Pulse frequency
        amp : int
            Pulse amplitude
        phase : int
            Pulse phase
        tstart : int
            Start time
        twidth : int
            Pulse width
        env : int
            Envelope identifier
        qubits : Dict[str, Qubit]
            Dictionary of qubits
        sim_qubits : bool
            Whether to simulate qubit behavior
        """
        for name, chan in self.channels.items():
            if cfg == chan.chanconfig.elem_ind:
                self.channels[name].add_pulse(
                    freq, amp, phase, tstart, twidth, env
                )
                if cfg == 0 and sim_qubits and 'qubit' in self.name:
                    if twidth == 0:
                        envelope = None
                        for i in range(self.curr_sim_data.current_cmd+1, len(self.commands)):
                            if 'pulse_write_trig' in self.commands[i]['op']:
                                twidth = self.commands[i]['start_time'] - self.curr_sim_data.current_time
                                break
                    else:
                        envelope = chan.env_buffers[env]
                    if env >= len(chan.env_buffers):
                        qubits[f"Q{int(self.name[1])}"].apply_pulse_gate(
                            chan.get_real_freq(freq), amp, phase,
                            envelope, tstart, twidth,
                            chan.chanconfig.elem_params['samples_per_clk'],
                            chan.chanconfig.elem_params['interp_ratio']
                        )
                    else:
                        qubits[f"Q{int(self.name[1])}"].apply_pulse_gate(
                            chan.get_real_freq(freq), amp, phase,
                            envelope, tstart, twidth,
                            chan.chanconfig.elem_params['samples_per_clk'],
                            chan.chanconfig.elem_params['interp_ratio']
                        )
                return
        raise ValueError(
            f"Invalid cfg value in {self.name}, "
            f"cfg: {cfg}"
        )


    def reg_alu(self, in0: int, alu_op: str, in1_reg: int, out_reg: int, r: bool) -> None:
        """Perform ALU operation on registers.

        Parameters
        ----------
        in0 : int
            First input value
        alu_op : str
            ALU operation to perform
        in1_reg : int
            Second input register
        out_reg : int
            Output register
        r : bool
            Whether to use register value
        """
        assert (isinstance(in0, int)), (
            f"First input must be an integer (immediate value or register address), "
            f"in0: {in0}"
        )
        assert ((not r) or (r and (in0 >= 0 and in0 < 16))), (
            f"First input register address does not exist, in0: {in0}"
        )
        assert (isinstance(alu_op, str)), (
            f"ALU Operation must be a string, alu_op: {alu_op}"
        )
        assert (isinstance(in1_reg, int)), (
            f"Second input must be an integer (register address), in1_reg: {in1_reg}"
        )
        assert (in1_reg >= 0 and in1_reg < 16), (
            f"Second input register address does not exist, in1_reg: {in1_reg}"
        )
        assert (isinstance(out_reg, int)), (
            f"Output must be an integer (register address), out_reg: {out_reg}"
        )
        assert (out_reg >= 0 and out_reg < 16), (
            f"Output register address does not exist, out_reg: {out_reg}"
        )

        if r:
            in0 = self.reg[in0]
        in1 = self.reg[in1_reg]

        if alu_op == 'add':
            self.reg[out_reg] = in0 + in1
        elif alu_op == 'sub':
            self.reg[out_reg] = in0 - in1
        elif alu_op == 'id0':
            self.reg[out_reg] = in0
        elif alu_op == 'id1':
            self.reg[out_reg] = in1
        elif alu_op == 'eq':
            self.reg[out_reg] = int(in0 == in1)
        elif alu_op == 'le':
            self.reg[out_reg] = int(in0 < in1)
        elif alu_op == 'ge':
            self.reg[out_reg] = int(in0 > in1)
        elif alu_op == 'zero':
            self.reg[out_reg] = 0
        else:
            raise ValueError(f"Invalid ALU operation, alu_op: {alu_op}")


    def jump_cond(self, in0: int, alu_op: str, in1_reg: int, jump_label: int, 
                 r: bool, curr_cmd: int) -> int:
        """Perform conditional jump based on ALU operation.

        Parameters
        ----------
        in0 : int
            First input value
        alu_op : str
            ALU operation to perform
        in1_reg : int
            Second input register
        jump_label : int
            Jump target label
        r : bool
            Whether to use register value
        curr_cmd : int
            Current command index

        Returns
        -------
        int
            New command index after jump
        """
        assert (isinstance(in0, int)), (
            "First input must be an integer (immediate value or register address)"
        )
        assert ((not r) or (r and (in0 >= 0 and in0 < 16))), (
            f"First input register address does not exist, in0: {in0}"
        )
        assert (isinstance(alu_op, str)), (
            f"ALU Operation must be a string, alu_op: {alu_op}"
        )
        assert (isinstance(in1_reg, int)), (
            f"Second input must be an integer (register address), in1_reg: {in1_reg}"
        )
        assert (in1_reg >= 0 and in1_reg < 16), (
            f"Second input register address does not exist, in1_reg: {in1_reg}"
        )
        assert (isinstance(jump_label, int)), (
            f"Jump label must be an integer, jump_label: {jump_label}"
        )
        assert (jump_label >= 0 and jump_label < len(self.commands)), (
            f"Jump label address does not exist, jump_label: {jump_label}"
        )
        if r:
            in0 = self.reg[in0]
        in1 = self.reg[in1_reg]
        if alu_op == 'eq' and in0 == in1:
            return jump_label
        elif alu_op == 'le' and in0 < in1:
            return jump_label
        elif alu_op == 'ge' and in0 > in1:
            return jump_label
        elif alu_op == 'add' and in0 + in1 != 0:
            return jump_label
        elif alu_op == 'sub' and in0 - in1 != 0:
            return jump_label
        elif alu_op == 'id0' and in0 != 0:
            return jump_label
        elif alu_op == 'id1' and in1 != 0:
            return jump_label
        elif alu_op in ['add', 'sub', 'id0', 'id1', 'eq', 'le', 'ge', 'zero']:
            return curr_cmd + 1
        else:
            raise ValueError(f"Invalid ALU operation, alu_op: {alu_op}")


    def alu_fproc(self, in0: int, alu_op: str, out_reg: int, func_id: int,
                 r: bool, fproc: FunctionProcessor) -> None:
        """Perform ALU operation using function processor.

        Parameters
        ----------
        in0 : int
            First input value
        alu_op : str
            ALU operation to perform
        out_reg : int
            Output register
        func_id : int
            Function identifier
        r : bool
            Whether to use register value
        fproc : FunctionProcessor
            Function processor instance
        """
        assert (isinstance(in0, int)), (
            f"First input must be an integer (immediate value or register address), "
            f"in0: {in0}"
        )
        assert ((not r) or (r and (in0 < 0 or in0 > 15))), (
            f"First input register address does not exist, in0: {in0}"
        )
        assert (isinstance(alu_op, str)), (
            f"ALU Operation must be a string, alu_op: {alu_op}"
        )
        assert (isinstance(out_reg, int)), (
            f"Output must be an integer (register address), out_reg: {out_reg}"
        )
        assert (out_reg >= 0 and out_reg < 16), (
            f"Output register address does not exist, out_reg: {out_reg}"
        )
        assert (isinstance(func_id, int)), (
            f"Function ID must be an int, func_id: {func_id}"
        )

        if r:
            in0 = self.reg[in0]
        in1 = fproc.values[func_id - 1]

        if alu_op == 'add':
            self.reg[out_reg] = in0 + in1
        elif alu_op == 'sub':
            self.reg[out_reg] = in0 - in1
        elif alu_op == 'id0':
            self.reg[out_reg] = in0
        elif alu_op == 'id1':
            self.reg[out_reg] = in1
        elif alu_op == 'eq':   # Double check to see if the boolean operations are valid for this
            self.reg[out_reg] = int(in0 == in1)
        elif alu_op == 'le':
            self.reg[out_reg] = int(in0 < in1)
        elif alu_op == 'ge':
            self.reg[out_reg] = int(in0 > in1)
        elif alu_op == 'zero':
            self.reg[out_reg] = 0
        else:
            raise ValueError(f"Invalid ALU operation, alu_op: {alu_op}")


    def jump_fproc(self, in0: int, alu_op: str, jump_label: int, func_id: int, 
                  r: bool, curr_cmd: int, fproc: FunctionProcessor) -> int:
        """Perform conditional jump using function processor.

        Parameters
        ----------
        in0 : int
            First input value
        alu_op : str
            ALU operation to perform
        jump_label : int
            Jump target label
        func_id : int
            Function identifier
        r : bool
            Whether to use register value
        curr_cmd : int
            Current command index
        fproc : FunctionProcessor
            Function processor instance

        Returns
        -------
        int
            New command index after jump
        """
        assert (isinstance(in0, int)), (
            f"First input must be an integer (immediate value or register address), in0: {in0}"
        )
        assert ((not r) or (r and (in0 >= 0 and in0 < 16))), (
            f"First input register address does not exist, in0: {in0}"
        )
        assert (isinstance(alu_op, str)), (
            f"ALU Operation must be a string, alu_op: {alu_op}"
        )
        assert (isinstance(jump_label, int)), (
            f"Jump label must be an integer, jump_label: {jump_label}"
        )
        assert (jump_label >= 0 and jump_label < len(self.commands)), (
            f"Jump label address does not exist, jump_label: {jump_label}"
        )
        assert (isinstance(func_id, int)), (
            f"Function ID must be an int, func_id: {func_id}"
        )

        if r:
            in0 = self.reg[in0]
        in1 = fproc.values[func_id - 1]

        if alu_op == 'eq' and in0 == in1:
            return jump_label
        elif alu_op == 'le' and in0 < in1:
            return jump_label
        elif alu_op == 'ge' and in0 > in1:
            return jump_label
        elif alu_op == 'add' and in0 + in1 != 0:
            return jump_label
        elif alu_op == 'sub' and in0 - in1 != 0:
            return jump_label
        elif alu_op == 'id0' and in0 != 0:
            return jump_label
        elif alu_op == 'id1' and in1 != 0:
            return jump_label
        elif alu_op in [
            'add', 'sub', 'id0', 'id1', 
            'eq', 'le', 'ge', 'zero'
        ]:
            return curr_cmd + 1
        else:
            raise ValueError(f"Invalid ALU operation, alu_op: {alu_op}")


class CoreSimData:
    """Simulation data container for core execution state.
    
    Attributes
    ----------
    current_time : int
        Current simulation time
    pulse_time : int
        Time for pulse generation logic
    current_cmd : int
        Current command index
    pulse_cooldown : dict
        Cooldown timers for each channel
    pulse_readtime : dict
        Read time for each channel
    alu_cooldown : int
        ALU operation cooldown
    active_pulse : bool
        Whether a pulse is currently active
    done : bool
        Whether simulation is complete
    """

    def __init__(self, num_channels: int):
        """Initialize simulation data state.
        
        Parameters
        ----------
        num_channels : int
            Number of channels to initialize cooldown and read time trackers
        """
        self.current_time = 0
        self.pulse_time = 0
        self.current_cmd = 0
        self.pulse_cooldown = {i: 0 for i in range(num_channels)}
        self.pulse_readtime = {i: 0 for i in range(num_channels)}
        self.alu_cooldown = 0
        self.active_pulse = False
        self.done = False

    def reset(self):
        """Reset all simulation state variables to their initial values."""
        self.current_time = 0
        self.pulse_time = 0
        self.current_cmd = 0
        self.pulse_cooldown = {i: 0 for i in range(len(self.pulse_cooldown))}
        self.pulse_readtime = {i: 0 for i in range(len(self.pulse_readtime))}
        self.alu_cooldown = 0
        self.active_pulse = False
        self.done = False

class PulseRegister:
    """Container for pulse register values.
    
    Attributes
    ----------
    amp : int
        Amplitude value
    freq : int
        Frequency value
    phase : int
        Phase value
    env : int
        Envelope identifier
    cfg : int
        Channel configuration value
    """

    def __init__(self):
        """Initialize pulse register with default values."""
        self.amp = 0
        self.freq = 0
        self.phase = 0
        self.env = 0
        self.cfg = 0

    def reset(self):
        """Reset all pulse register values to zero."""
        self.amp = 0
        self.freq = 0
        self.phase = 0
        self.env = 0
        self.cfg = 0


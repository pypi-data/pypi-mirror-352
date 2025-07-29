"""Module for distributed processor emulation in quantum circuits.

This module provides the DistributedProcessor class for orchestrating quantum circuit
simulations across multiple cores, DACs, and ADCs.
"""
import random
import warnings
from distproc.executable import Executable
from emulator.hardware.core import Core
from emulator.hardware.dac import DAC
import emulator.parsers.buffer_parser as bp
from emulator.hardware.function_processor import FunctionProcessor
from emulator.hardware.qubit import Qubit
from emulator.hardware.adc import ADC
from emulator.data.result import Result
from emulator.config.channel_config import ChannelConfig
from emulator.config.hardware_config import HWConfig
from emulator.config.qubit_config import QubitConfig, IndividualQubitConfig
import numpy as np


class MeasurementData:
    """
    Data for a measurement pulse.

    Attributes
    ----------
        pulse_width : int
            The width of the pulse
        start_time : int
            The time the pulse started
        is_active : bool
            Whether the pulse is currently active
        pulse_width : int
            The width of the pulse
    """
    def __init__(self, t_left: int, start_time: int, is_active: bool, pulse_width: int):
        self.t_left = t_left
        self.start_time = start_time
        self.is_active = is_active
        self.pulse_width = pulse_width


class DistributedProcessor:
    """
    Class that holds all of the cores and orchestrates the simulations from the highest level.
    Is able to orchestrate communication between cores if needed.

    Attributes
    ----------
        cores : dict
            Dictionary of cores with keys being the name of the core and the value being the Core 
            object
        chanconfig : dict
            List of channel configs for future reference
        num_cores : int
            The number of cores in the setup (qubit + drive + coupler) 
        dacs : list
            List of DAC objects indexed by their id
        adcs : list
            List of ADC objects indexed by their id
        self.dac_adc_link : dict
            Mapping of DAC indices to ADC indices if the rdrv and rdlo channels for the same core
            are common between them
        self.qubits : dict
            Dictionary of Qubit objects indexed by their name
        self.sim_iq : list
            List of IQ points calculated to hold in the Result object for scatter plot graphing
        self.measurement_iq_map : list
            List of dictionaries containing information about which IQ values map to which states 
            in which cores. Each dictionary carries three keys:
                'core' - The core that is assigned to the qubit that is being measured
                'meas' - The state of the qubit, 1 or 0
                'iq' - The calculated IQ value after the IQ mixing
    """


    def __init__(self, chanconfig: ChannelConfig, hwconfig: HWConfig, qubitconfig: QubitConfig):
        """
        Parameters
        ----------
            chanconfig : ChannelConfig
                ChannelConfig object from config files
            hwconfig : HWConfig
                HWConfig object from config files
            qubitconfig : QubitConfig
                QubitConfig object from config files
        """
        self.cores = {}
        self.chanconfig = chanconfig
        for key, config in chanconfig.channels.items():
            core_name = f"{key[0:2]}.{config.core_name}"
            if core_name not in self.cores:
                self.cores[core_name] = {key: config}
            else:
                self.cores[core_name].update({key: config})

        for key, config_lst in self.cores.items():
            core_chan_config = config_lst
            self.cores[key] = Core(key, core_chan_config, hwconfig)

        # Load channels into DACS for output according to the configuration file
        self.num_cores = hwconfig.num_cores
        self.dacs = [None for _ in range(hwconfig.num_dacs)]
        self.adcs = [None for _ in range(hwconfig.num_adcs)]

        for i, _ in enumerate(self.dacs):
            if str(i) in hwconfig.dacs:
                chans = hwconfig.dacs[str(i)]
                chan_to_core = {}
                for chan in chans:
                    if chan[0] == 'Q':
                        core = (f"{chan[:2]}.qubit"
                                if not chan[-1].isdigit()
                                else f"{chan[:2]}.drive")
                    else:
                        core = f"{chan[:2]}.coupler"
                    if core in self.cores:
                        chan_to_core[chan] = core
                channels = {chan: self.cores[core].channels[chan]
                          for chan, core in chan_to_core.items()}
                self.dacs[i] = DAC(f"DAC{i}", channels, hwconfig, qubitconfig)
            else:
                self.dacs[i] = DAC(f"DAC{i}", {}, hwconfig, qubitconfig)

        for i, _ in enumerate(self.adcs):
            if str(i) in hwconfig.adcs:
                chans = hwconfig.adcs[str(i)]
                chan_to_core = {}
                for chan in chans:
                    if chan[0] == 'Q':
                        core = (f"{chan[:2]}.qubit"
                                if not chan[-1].isdigit()
                                else f"{chan[:2]}.drive")
                    else:
                        core = f"{chan[:2]}.coupler"
                    if core in self.cores:
                        chan_to_core[chan] = core

                adc_channels = {chan: self.cores[core].channels[chan] 
                                for chan, core in chan_to_core.items()}
                self.adcs[i] = ADC(f"ADC{i}", adc_channels)
            else:
                self.adcs[i] = ADC(f"ADC{i}", {})

        self.dac_adc_link = {} # Keys = dac index, values = adc index
        for i, _ in enumerate(self.dacs):
            dac_channels = [chan.name for chan in self.dacs[i].channels.values()]
            for j, _ in enumerate(self.adcs):
                adc_channels = [chan.name.replace('rdlo', 'rdrv')
                                for chan in self.adcs[j].channels.values()]
                if dac_channels != [] and set(dac_channels) == set(adc_channels):
                    self.dac_adc_link[i] = j
                    self.adcs[j].set_config(self.dacs[i].samples_per_clk, self.dacs[i].interp_ratio)

    
        self.qubits = {}
        for name, config in qubitconfig.qubits.items():
            if name in qubitconfig.qubits and f"{name}.qubit" in self.cores:
                self.qubits[name] = Qubit(name, config)
            else:
                if name in qubitconfig.qubits:
                    warnings.warn(f"{name} configuration is not included in qubit config."
                                  "Default values are being used")
                else:
                    warnings.warn(f"{name} has no core assigned to it.")
                default_qubit = IndividualQubitConfig()
                default_qubit.freq = 500e6
                default_qubit.Omega = 0.11
                self.qubits[name] = Qubit(name, default_qubit)

        self.sim_iq = []
        self.measurement_iq_map = []
        self.time = 0


    def define_dac(self, name, channel_names, hwconfig, qubitconfig):
        """
        Way to manually define DAC's if no .yaml profile is provided.

        Parameters
        ----------
            dac_id : int
                The number of the dac being accessed, limited from 0-15
            channel_names : list
                List of strings containing the names of the channels that belong to that DAC
        """
        dac_channels = []
        for core in self.cores.values():
            for chan in channel_names:
                if chan in core.channels:
                    dac_channels.append(core.channels[chan])
        self.dacs[name] = DAC(name, channel_names, hwconfig, qubitconfig)


    def define_adc(self, adc_id: int, channel_names: list):
        """
        Way to manually define ADC's if no .yaml profile is provided.

        Parameters
        ----------
            adc_id : int
                The number of the adc being accessed, limited from 0-15
            channel_names : list
                List of strings containing the names of the channels that belong to that ADC
        """
        dac_channels = []
        for core in self.cores.values():
            for chan in channel_names:
                if chan in core.channels:
                    dac_channels.append(core.channels[chan])
        self.adcs[adc_id] = ADC(adc_id, dac_channels)


    def load_program(self, assembled_prog: Executable | bytes):
        """
        Load envelope, frequency, and command buffers onto the cores

        Parameters
        ----------
            assembled_prog : Executable | bytes
                Assembled Executable or binaries that will be loaded and parsed for simulation.
        """
        bp.decode(assembled_prog, self.cores, self.chanconfig)


    def execute(self, fproc: FunctionProcessor, manual_fproc: bool, toggle_qubits: bool, tags: list = None):
        """
        Simulates pulses and commands for all cores

        Parameters
        ----------
            fproc : FunctionProcessor
                The function processor object in this simulation to place values in when measurements are taken
            manual_fproc : bool
                Whether or not the function processor was manually updated
            toggle_qubits : bool
                Whether or not the qubits were toggled
            tags : list
                A list of tags that can be specified for print statements during simulation. Useful
                for debugging. List of tags are as follows:
                    'DEBUG' - Prints out every command executed and when it was executed
                    'REGISTER' - Prints out the registers every time a command is executed
                    'FPROC' - Prints out the function processor every time a command is executed
                An example tags list could be tags=['DEBUG', 'REGISTER'], which will print out all
                operations when executed, and the registers at each step
        """
        
        if tags is None:
            tags = []
        # Distributed Processor Simulation
        core_statuses = [False] # First while loop will always happen
        meas_active = {core: MeasurementData(0, 0, False, 0) for core in self.cores}

        while not all(core_statuses): # While at least one core has something happening
            # Cores
            core_statuses = []
            for core_name, core in self.cores.items():
                result = core.execute_current(fproc, self.qubits, toggle_qubits, tags)
                core_statuses.append(result.is_done)
                if result.measurement_taken: # If there is a measurement pulse
                    pulse_width = result.command['env_len']
                    meas_active[core_name] = MeasurementData(pulse_width, self.time, True, pulse_width)
                    if manual_fproc:
                        fproc.update(core_name, self.time + pulse_width)
            if manual_fproc:
                fproc.check_queue(self.time, 'FPROC' in tags)


            # Measurement and IQ mixing
            if not manual_fproc:
                for core_name, meas_data in meas_active.items():
                    meas_data.t_left = max(meas_data.t_left - 1, 0) # Decrement pulse width time if its there
                    
                    if meas_data.t_left == 0 and meas_data.is_active:
                        # Measure every qubit
                        measurements = {qubit.name: 0 for qubit in self.qubits.values()}
                        for qubit in self.qubits.values():
                            measurements[qubit.name] = qubit.measure()

                        # Find the DAC and ADC indices for the current core taking measurements
                        dac_index = 0
                        adc_index = 0
                        for i, dac in enumerate(self.dacs):
                            chan_names = list(dac.channels.keys())
                            if f"{core_name[:2]}.rdrv" in chan_names:
                                dac_index = i
                        for j, adc in enumerate(self.adcs):
                            chan_names = list(adc.channels.keys())
                            if f"{core_name[:2]}.rdlo" in chan_names:
                                adc_index = j

                        # Update the DAC and ADC data with resonator response
                        self.dacs[dac_index].update_data(self.time + 1)
                        resonator_response = self.dacs[dac_index].get_resonator_response(f"{core_name[:2]}.rdrv", meas_data.start_time, meas_data.pulse_width, measurements)
                        self.adcs[adc_index].update_data(resonator_response, meas_data.start_time)

                        # IQ mixing and FPROC updating
                        iq = self.iq_mix(adc_index, f"{core_name[:2]}.rdlo", meas_data.start_time, meas_data.pulse_width)
                        state = None
                        tolerance = 1e-4

                        for val in self.measurement_iq_map:
                            within_tolerance = np.abs(iq.real - val['iq'].real) < tolerance and np.abs(iq.imag - val['iq'].imag) < tolerance
                            if core_name == val['core'] and within_tolerance:
                                state = val['meas']

                        if state is None:
                            self.measurement_iq_map.append({'core': core_name, 'meas': measurements[f"Q{int(core_name[1])}"], 'iq': iq})
                            state = measurements[f"Q{int(core_name[1])}"]

                        state = measurements[f"Q{int(core_name[1])}"]
                        fproc.insert_value(int(core_name[1]), state)
                        if 'FPROC' in tags:
                            print(f"FPROC Updated at Time {self.time} with a measurement of {state} in qubit {core_name[1]}. The values are: {fproc.values}")
                        meas_data.is_active = False
            
            self.time += 1
            if self.time >= 500000:
                print("Clock cycle limit reached, 1 ms of simulation completed")
                break
        
        result = self.end_sim(fproc, manual_fproc, toggle_qubits)
        return result


    def end_sim(self, fproc: FunctionProcessor, manual_fproc: bool, toggle_qubits: bool):
        """
        Ends the current simulation by gathering all of the crucial information from the 
        simulation, and returning a Result object with that data in it. Also ends the 
        simulation for cores, adcs, dacs, qubits, etc.

        Parameters
        ----------
            fproc : FunctionProcessor
                The function processor used in simulation to get its values to place in the Result 
                object
            manual_fproc : bool
                Whether or not the function processor was manually updated
            toggle_qubits : bool
                Whether or not the qubits were toggled
        """
        channel_data = {}
        env_buffers = {}
        freq_buffers = {}
        dac_data = {}
        adc_data = {}
        qubit_data = {}
        registers = {}
        commands = {}
        functionprocessor = fproc.values
        iq_values = np.array(self.sim_iq)

        for core_name, core in self.cores.items():
            chan, env, freq, reg, cmd = core.end_sim()
            channel_data.update(chan)
            env_buffers.update(env)
            freq_buffers.update(freq)
            registers[core_name] = reg
            commands[core_name] = cmd
        for dac in self.dacs:
            dac_data[dac.name] = dac.end_sim()
            dac.reset()
        for adc in self.adcs:
            ran_chan = random.choice(list(channel_data))
            adc_data[adc.name] = adc.end_sim(channel_data[ran_chan].get('time'))
            adc.reset()
        for qubit in self.qubits.values():
            qubit_data[qubit.name] = qubit.end_sim()

        result = Result(channel_data,
                        dac_data,
                        adc_data,
                        qubit_data,
                        commands,
                        registers,
                        functionprocessor,
                        env_buffers,
                        freq_buffers,
                        iq_values,
                        self.time,
                        manual_fproc,
                        toggle_qubits
                        )
        self.time = 0
        self.sim_iq = []
        self.measurement_iq_map = []
        return result


    def iq_mix(self, adc_index: int, chan: str, tstart: int, twidth: int):
        """
        Acts as the IQ mixer with the complex dac signal and the adc resonator response signal. 
        Multiplies the two signals into a mixed_signal, and then integrates over the measurement 
        window to get a complex number that represents the I/Q values of the measurement.

        Parameters
        ----------
            adc_index : int
                The index of the adc that will have its resonatr response multiplied
            chan : str
                The channel that will be used for the IQ mixing
            tstart : int
                The start time of the measurement for proper integration bounds
            twidth : int
                The width of the measurement for proper integration bounds
        
        Returns
        -------
            complex_num : np.complex128
                A complex number representing the I and Q after the IQ mixing. 
                complex_num = I + jQ, and complex_num.real = I, complex_num.imag = Q
        
        """
        tstart_adc = tstart * self.adcs[adc_index].samples_per_clk
        twidth_adc = twidth * self.adcs[adc_index].samples_per_clk
        tstart_rdlo = tstart * self.cores[f"{chan[:2]}.qubit"].channels[chan].sim_data.samples_per_clk
        twidth_rdlo = twidth * self.cores[f"{chan[:2]}.qubit"].channels[chan].sim_data.samples_per_clk

        self.cores[f"{chan[:2]}.qubit"].channels[chan].sim_data.resolve()
        full_signal = self.cores[f"{chan[:2]}.qubit"].channels[chan].sim_data.get('voltage_imag')
        rdlo_signal = full_signal[tstart_rdlo:tstart_rdlo+twidth_rdlo]
        adc_signal = self.adcs[adc_index].sim_data.get('voltage')[tstart_adc:tstart_adc+twidth_adc]

        try:
            n_points = len(rdlo_signal)
            new_length = (int)(n_points * self.adcs[adc_index].samples_per_clk / self.cores[f"{chan[:2]}.qubit"].channels[chan].sim_data.samples_per_clk)
            x_old = np.arange(n_points)
            x_new = np.linspace(0, n_points - 1, new_length)
            rdlo_signal = np.interp(x_new, x_old, rdlo_signal)

            if isinstance(rdlo_signal, list):
                rdlo_signal = np.array(rdlo_signal)
            if isinstance(adc_signal, list):
                adc_signal = np.array(adc_signal)

            diff = len(adc_signal) - len(rdlo_signal)
            rdlo_signal = np.append(rdlo_signal, np.zeros(diff))
            mixed_signal = rdlo_signal * adc_signal

            complex_num = np.trapz(mixed_signal, np.arange(len(mixed_signal)) / self.adcs[adc_index].samples_per_clk)
            self.sim_iq.append(complex_num)
            return complex_num
        except Exception as e:
            warnings.warn(f"RDLO signal needed for proper IQ Mixing, {e}")
            self.sim_iq.append(np.complex128(0 + 1j * 0))
            return np.complex128(0 + 1j * 0)

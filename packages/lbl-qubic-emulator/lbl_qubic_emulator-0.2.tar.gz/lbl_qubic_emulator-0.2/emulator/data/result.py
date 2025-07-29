"""Module for handling simulation results from the QubiC emulator.

This module provides the Result class for storing and analyzing simulation data,
including channel signals, DAC/ADC signals, qubit states, and more.
"""

from typing import Dict, List, Union, Any
import warnings
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import qutip as qt
from vcd import VCDWriter



class Result:
    """Store and analyze QubiC emulator simulation results.

    This class provides methods for accessing and visualizing simulation data,
    including channel signals, DAC/ADC signals, qubit states, commands executed,
    register values, and function processor data.

    Attributes
    ----------
    channel_data : Dict[str, Dict[str, np.ndarray]]
        Channel signal data, keyed by channel name (e.g., 'Q0.qdrv').
        Values are dicts with 'time' and 'voltage' series data.
    dac_data : Dict[str, Dict[str, np.ndarray]]
        DAC signal data, keyed by DAC name.
        Values are dicts with 'time' and 'voltage' series data.
    adc_data : Dict[str, Dict[str, np.ndarray]]
        ADC signal data, keyed by ADC name.
        Values are dicts with 'time' and 'voltage' series data.
    qubit_data : Dict[str, Dict[str, Union[np.ndarray, List[qt.Qobj]]]]
        Qubit state data, keyed by qubit name (e.g., 'Q0').
        Values are dicts with 'time' and 'states' series data.
    commands : Dict[str, List[Dict[str, Any]]]
        Commands executed by each core, keyed by core name (e.g., 'Q0.qubit').
    registers : Dict[str, List[int]]
        Register values for each core, keyed by core name.
    fproc : List[float]
        Function processor results at simulation end.
    env_buffers : Dict[str, List[np.ndarray]]
        Envelope data buffers, keyed by channel name.
        Values are lists of numpy arrays.
    freq_buffers : Dict[str, List[np.ndarray]]
        Frequency data buffers, keyed by channel name.
        Values are lists of numpy arrays.
    iq_values : np.ndarray
        IQ measurement values
    end_time : int
        End time of the simulation in clock cycles
    manual_fproc : bool
        Whether function processor values were manually set
    toggle_qubit : bool
        Whether qubit simulation was enabled
    """

    def __init__(
        self,
        channel_data: Dict[str, Dict[str, np.ndarray]] = None,
        dac_data: Dict[str, Dict[str, np.ndarray]] = None,
        adc_data: Dict[str, Dict[str, np.ndarray]] = None,
        qubit_data: Dict[str, Dict[str, Union[np.ndarray, List[qt.Qobj]]]] = None,
        commands: Dict[str, List[Dict[str, Any]]] = None,
        registers: Dict[str, List[int]] = None,
        fproc: List[float] = None,
        env_buffers: Dict[str, List[np.ndarray]] = None,
        freq_buffers: Dict[str, List[np.ndarray]] = None,
        iq_values: np.ndarray = None,
        end_time: int = 0,
        manual_fproc: bool = True,
        toggle_qubit: bool = False
    ) -> None:
        """Initialize a new Result instance.

        Parameters
        ----------
        channel_data : Dict[str, Dict[str, np.ndarray]], optional
            Channel signal data, defaults to empty dict
        dac_data : Dict[str, Dict[str, np.ndarray]], optional
            DAC signal data, defaults to empty dict
        adc_data : Dict[str, Dict[str, np.ndarray]], optional
            ADC signal data, defaults to empty dict
        qubit_data : Dict[str, Dict[str, Union[np.ndarray, List[qt.Qobj]]]], optional
            Qubit state data, defaults to empty dict
        commands : Dict[str, List[Dict[str, Any]]], optional
            Commands executed by each core, defaults to empty dict
        registers : Dict[str, List[int]], optional
            Register values for each core, defaults to empty dict
        fproc : List[float], optional
            Function processor results, defaults to empty list
        env_buffers : Dict[str, List[np.ndarray]], optional
            Envelope data buffers, defaults to empty dict
        freq_buffers : Dict[str, List[np.ndarray]], optional
            Frequency data buffers, defaults to empty dict
        iq_values : np.ndarray, optional
            IQ measurement values, defaults to empty array
        end_time : int, optional
            End time of simulation, defaults to 0
        manual_fproc : bool, optional
            Whether function processor values were manually set, defaults to True
        toggle_qubit : bool, optional
            Whether qubit simulation was enabled, defaults to False
        """
        self.channel_data = channel_data if channel_data is not None else {}
        self.dac_data = dac_data if dac_data is not None else {}
        self.adc_data = adc_data if adc_data is not None else {}
        self.qubit_data = qubit_data if qubit_data is not None else {}
        self.commands = commands if commands is not None else {}
        self.fproc = fproc if fproc is not None else []
        self.registers = registers if registers is not None else {}
        self.env_buffers = env_buffers if env_buffers is not None else {}
        self.freq_buffers = freq_buffers if freq_buffers is not None else {}
        self.iq_values = iq_values if iq_values is not None else np.array([])
        self.end_time = end_time
        self.manual_fproc = manual_fproc
        self.toggle_qubit = toggle_qubit


    def graph_multiple_channels(self, channels: List[str]) -> None:
        """Plot multiple channel signal data.

        Parameters
        ----------
        channels : List[str]
        """
        for chan in channels:
            if chan in self.channel_data:
                if not self.channel_data[chan].fully_resolved:
                    self.channel_data[chan].resolve(self.end_time)
                    self.channel_data[chan].fully_resolved = True
                plt.plot(
                    self.channel_data[chan].get('time'),
                    self.channel_data[chan].get('voltage'),
                    label=chan
                )
            elif chan in self.dac_data:
                if not self.dac_data[chan][0].fully_resolved:
                    self.resolve_dac(chan)
                plt.plot(
                    self.dac_data[chan][0].get('time'),
                    self.dac_data[chan][0].get('voltage'),
                    label=chan
                )
            elif chan in self.adc_data:
                if self.manual_fproc:
                    warnings.warn("Resonators not toggled, ADC behavior is undefined")
                plt.plot(self.adc_data[chan][0].get('time'), self.adc_data[chan][0].get('voltage'), label=chan)

            else:
                raise ValueError(f"Invalid channel name. chan={chan}, "
                                 f"channel_data.keys={self.channel_data.keys()}")
            
        
        plt.title(f"{chan}: RF Pulse Simulation Plot", fontsize=22)
        plt.xlabel('Time (FPGA Clock Cycles)', fontsize=18)
        plt.ylabel('Voltage (Normalized)', fontsize=18)
        plt.legend()
        plt.show()



    # Channel Methods
    def graph_channel(self, chan: str) -> None:
        """Plot channel signal data.

        Parameters
        ----------
        chan : str
            Channel name to plot
        """
        assert (chan in self.channel_data), (
            f"Invalid channel name. chan={chan}, "
            f"channel_data.keys={self.channel_data.keys()}"
        )
        if not self.channel_data[chan].fully_resolved:
            self.channel_data[chan].resolve(self.end_time)
            self.channel_data[chan].fully_resolved = True
        plt.plot(
            self.channel_data[chan].get('time'),
            self.channel_data[chan].get('voltage'),
            label=chan
        )
        plt.title(f"{chan}: RF Pulse Simulation Plot", fontsize=22)
        plt.xlabel('Time (FPGA Clock Cycles)', fontsize=18)
        plt.ylabel('Voltage (Normalized)', fontsize=18)
        plt.legend()
        plt.show()

    def graph_channel_complex(self, chan: str) -> None:
        """Plot complex channel signal data.

        Parameters
        ----------
        chan : str
            Channel name to plot
        """
        assert (chan in self.channel_data), (
            f"Invalid channel name. chan={chan}, "
            f"channel_data.keys={self.channel_data.keys()}"
        )
        if not self.channel_data[chan].fully_resolved:
            self.channel_data[chan].resolve(self.end_time)
            self.channel_data[chan].fully_resolved = True
        plt.plot(
            self.channel_data[chan].get('time'),
            self.channel_data[chan].get('voltage'),
            label='Real (I)'
        )
        plt.plot(
            self.channel_data[chan].get('time'),
            self.channel_data[chan].get('voltage_imag').imag,
            label='Complex (Q)'
        )
        plt.title(f"{chan}: RF Pulse Simulation Plot", fontsize=22)
        plt.xlabel('Time (FPGA Clock Cycles)', fontsize=18)
        plt.ylabel('Voltage (Normalized)', fontsize=18)
        plt.legend()
        plt.show()

    def get_channel_data(self, chan: str) -> Dict[str, np.ndarray]:
        """Get channel signal data.

        Parameters
        ----------
        chan : str
            Channel name

        Returns
        -------
        Dict[str, np.ndarray]
            Channel signal data dictionary
        """
        assert (chan in self.channel_data), (
            f"Invalid channel name. chan={chan}, "
            f"channel_data.keys={self.channel_data.keys()}"
        )
        if not self.channel_data[chan].fully_resolved:
            self.channel_data[chan].resolve(self.end_time)
            self.channel_data[chan].fully_resolved = True
        return self.channel_data[chan].sim_data

    def write_vcd(self, filename: str, channels: List[str] = None) -> None:
        """Write simulation data to VCD file using pyvcd.

        Parameters
        ----------
        filename : str
            Output VCD file path
        channels : List[str], optional
            List of channels to include in the VCD file. Ex ['Q0.qdrv', 'Q0.rdrv', 'DAC7', 'ADC0'].
            If no list is provided, all channels will be included.
        """
        if channels is None:
            channels = list(self.channel_data.keys())
            channels.extend(self.dac_data.keys())
            channels.extend(self.adc_data.keys())

        with open(filename, 'w', encoding="utf-8") as f:
            # Use 1 ps time scale to capture fractional clock cycles
            writer = VCDWriter(f, timescale='1 ps', date='today')
            
            # Check if we have any data at all
            if not (self.channel_data or self.dac_data or self.adc_data):
                print("Warning: No signal data available for VCD generation")
                writer.close()
                return
                
            # Resolve all data first and print summary
            print(f"Processing {len(self.channel_data)} channels for VCD file")
            for chan in self.channel_data:
                if chan in channels:
                    if not self.channel_data[chan].fully_resolved:
                        self.channel_data[chan].resolve(self.end_time)
                        self.channel_data[chan].fully_resolved = True
                    
                    # Debug info
                    times = self.channel_data[chan].get('time')
                    voltages = self.channel_data[chan].get('voltage')
                    print(f"Channel {chan}: {len(times)} time points, {len(voltages)} voltage points")
                    if len(times) > 0:
                        print(f"  Time range: {times[0]} to {times[-1]}")
                        # Check if we have fractional clock cycles
                        fractional = np.any(times % 1 != 0)
                        if fractional:
                            print("Contains fractional clock cycles")
                    if len(voltages) > 0:
                        print(f"  Voltage range: {min(voltages)} to {max(voltages)}")
            
            # Resolve DAC data if present
            if self.dac_data:
                print(f"Processing {len(self.dac_data)} DACs for VCD file")
                for dac in self.dac_data:
                    if dac in channels:
                        if not self.dac_data[dac][0].fully_resolved:
                            self.resolve_dac(dac)
                        
                        # Debug info
                        times = self.dac_data[dac][0].get('time')
                        voltages = self.dac_data[dac][0].get('voltage')
                        print(f"DAC {dac}: {len(times)} time points, {len(voltages)} voltage points")
                        if len(times) > 0:
                            print(f"  Time range: {times[0]} to {times[-1]}")
                        if len(voltages) > 0:
                            print(f"  Voltage range: {min(voltages)} to {max(voltages)}")
            
            # Check ADC data if present
            if self.adc_data:
                print(f"Processing {len(self.adc_data)} ADCs for VCD file")
                for adc in self.adc_data:
                    if adc in channels:
                        # Debug info
                        times = self.adc_data[adc][0].get('time')
                        voltages = self.adc_data[adc][0].get('voltage')
                        print(f"ADC {adc}: {len(times)} time points, {len(voltages)} voltage points")
                        if len(times) > 0:
                            print(f"  Time range: {times[0]} to {times[-1]}")
                        if len(voltages) > 0:
                            print(f"  Voltage range: {min(voltages)} to {max(voltages)}")
            
            # Register all signal variables
            signals = {}
            
            # Add clock signal
            signals['clk'] = writer.register_var('top', 'clk', 'reg', size=1, init=0)
            
            # Channel signals
            channel_vars = {}
            for chan in self.channel_data:
                if chan in channels:
                    # Skip channels with no data
                    times = self.channel_data[chan].get('time')
                    voltages = self.channel_data[chan].get('voltage')
                    if len(times) == 0 or len(voltages) == 0:
                        print(f"Skipping channel {chan} - no data")
                        continue
                        
                    # Register real and imag components for complex signals
                    signals[f"{chan}_real"] = writer.register_var('top', f"{chan}_real", 'wire', size=16)
                    signals[f"{chan}_imag"] = writer.register_var('top', f"{chan}_imag", 'wire', size=16)
                    channel_vars[chan] = {
                        'real': signals[f"{chan}_real"],
                        'imag': signals[f"{chan}_imag"],
                    }
            
            # DAC signals (real voltage only)
            dac_vars = {}
            if self.dac_data:
                for dac in self.dac_data:
                    if dac in channels:
                        times = self.dac_data[dac][0].get('time')
                        voltages = self.dac_data[dac][0].get('voltage')
                        if len(times) == 0 or len(voltages) == 0:
                            print(f"Skipping DAC {dac} - no data")
                            continue
                        
                        # Register real component only for DAC
                        signals[f"DAC_{dac}"] = writer.register_var('top', f"DAC_{dac}", 'wire', size=16)
                        dac_vars[dac] = signals[f"DAC_{dac}"]
            
            # ADC signals (real voltage only)
            adc_vars = {}
            if self.adc_data:
                for adc in self.adc_data:
                    if adc in channels:
                        times = self.adc_data[adc][0].get('time')
                        voltages = self.adc_data[adc][0].get('voltage')
                        if len(times) == 0 or len(voltages) == 0:
                            print(f"Skipping ADC {adc} - no data")
                        continue
                    
                        # Register real component only for ADC
                        signals[f"ADC_{adc}"] = writer.register_var('top', f"ADC_{adc}", 'wire', size=16)
                        adc_vars[adc] = signals[f"ADC_{adc}"]
            
            # Find max time across all signals
            max_time = 0
            
            # Check channels
            for chan in self.channel_data:
                if chan in channels:
                    times = self.channel_data[chan].get('time')
                    if len(times) > 0:
                        max_time = max(max_time, times[-1])
            
            # Check DACs
            if self.dac_data:
                for dac in self.dac_data:
                    if dac in channels:
                        times = self.dac_data[dac][0].get('time')
                        if len(times) > 0:
                            max_time = max(max_time, times[-1])
            
            # Check ADCs
            if self.adc_data:
                for adc in self.adc_data:
                    if adc in channels:
                        times = self.adc_data[adc][0].get('time')
                        if len(times) > 0:
                            max_time = max(max_time, times[-1])
            
            # Time scaling: each clock cycle is 2000 ps (2 ns)
            # Use picoseconds for better fractional representation
            CLOCK_CYCLE_PS = 2000
            total_clock_cycles = int(max_time) + 10  # Add buffer
            total_ps = int(total_clock_cycles * CLOCK_CYCLE_PS)
            
            print(f"Max simulation time: {max_time} clock cycles")
            print(f"VCD time range: 0-{total_ps} ps ({total_clock_cycles} clock cycles)")
            
            # Collect all changes for all signals with timestamps
            all_changes = []
            
            # First add clock changes (regular pattern)
            # Clock toggles every 1ns (1000ps)
            for i in range(int(total_ps/1000) + 1):
                # Every even ns, clock is low
                # Every odd ns, clock is high
                all_changes.append((i*1000, signals['clk'], i % 2))
            
            # Add channel data
            for chan, var_dict in channel_vars.items():
                times = self.channel_data[chan].get('time')
                voltages_real = self.channel_data[chan].get('voltage')
                
                # Skip channels with no data
                if len(times) == 0 or len(voltages_real) == 0:
                    continue
                
                # Handle complex data if available
                try:
                    voltages_imag = self.channel_data[chan].get('voltage_imag').imag
                    if voltages_imag is None or len(voltages_imag) == 0:
                        voltages_imag = np.zeros_like(voltages_real)
                except (AttributeError, KeyError, TypeError):
                    voltages_imag = np.zeros_like(voltages_real)
                
                # Ensure arrays have same length
                min_len = min(len(times), len(voltages_real), len(voltages_imag))
                if min_len == 0:
                    continue
                
                times = times[:min_len]
                voltages_real = voltages_real[:min_len]
                voltages_imag = voltages_imag[:min_len]
                
                # Scale values to fit in 16-bit range (-32768 to 32767)
                voltages_real_scaled = np.round(voltages_real * 32767).astype(int)
                voltages_imag_scaled = np.round(voltages_imag * 32767).astype(int)
                
                # Initial values at time 0
                all_changes.append((0, var_dict['real'], int(voltages_real_scaled[0])))
                all_changes.append((0, var_dict['imag'], int(voltages_imag_scaled[0])))
                
                # Add all data points, preserving fractional clock cycles
                for i in range(1, len(times)):
                    # Convert clock cycles to picoseconds with high precision
                    # Multiply by 2000 to convert to ps (2ns per clock cycle)
                    vcd_time = int(times[i] * CLOCK_CYCLE_PS)
                    
                    # Only add if value changed (to reduce file size)
                    if voltages_real_scaled[i] != voltages_real_scaled[i-1]:
                        all_changes.append((vcd_time, var_dict['real'], int(voltages_real_scaled[i])))
                    
                    if voltages_imag_scaled[i] != voltages_imag_scaled[i-1]:
                        all_changes.append((vcd_time, var_dict['imag'], int(voltages_imag_scaled[i])))
            
            # Add DAC data (real component only)
            if dac_vars:
                for dac, var in dac_vars.items():
                    times = self.dac_data[dac][0].get('time')
                    voltages = self.dac_data[dac][0].get('voltage')
                    
                    # Skip DACs with no data
                    if len(times) == 0 or len(voltages) == 0:
                        continue
                    
                    # Ensure arrays have same length
                    min_len = min(len(times), len(voltages))
                    if min_len == 0:
                        continue
                    
                    times = times[:min_len]
                    voltages = voltages[:min_len]
                    
                    # Scale values to fit in 16-bit range (-32768 to 32767)
                    voltages_scaled = np.round(voltages * 32767).astype(int)
                    
                    # Initial value at time 0
                    all_changes.append((0, var, int(voltages_scaled[0])))
                    
                    # Add all data points, preserving fractional clock cycles
                    for i in range(1, len(times)):
                        # Convert clock cycles to picoseconds
                        vcd_time = int(times[i] * CLOCK_CYCLE_PS)
                        
                        # Only add if value changed (to reduce file size)
                        if voltages_scaled[i] != voltages_scaled[i-1]:
                            all_changes.append((vcd_time, var, int(voltages_scaled[i])))
            
            # Add ADC data (real component only)
            if adc_vars:
                for adc, var in adc_vars.items():
                    times = self.adc_data[adc][0].get('time')
                    voltages = self.adc_data[adc][0].get('voltage')
                    
                    # Skip ADCs with no data
                    if len(times) == 0 or len(voltages) == 0:
                        continue
                    
                    # Ensure arrays have same length
                    min_len = min(len(times), len(voltages))
                    if min_len == 0:
                        continue
                    
                    times = times[:min_len]
                    voltages = voltages[:min_len]
                    
                    # Scale values to fit in 16-bit range (-32768 to 32767)
                    voltages_scaled = np.round(voltages * 32767).astype(int)
                    
                    # Initial value at time 0
                    all_changes.append((0, var, int(voltages_scaled[0])))
                    
                    # Add all data points, preserving fractional clock cycles
                    for i in range(1, len(times)):
                        # Convert clock cycles to picoseconds
                        vcd_time = int(times[i] * CLOCK_CYCLE_PS)
                        
                        # Only add if value changed (to reduce file size)
                        if voltages_scaled[i] != voltages_scaled[i-1]:
                            all_changes.append((vcd_time, var, int(voltages_scaled[i])))
            
            # Sort all changes by timestamp
            all_changes.sort(key=lambda x: x[0])
            
            # Apply changes in timestamp order
            current_time = -1
            change_count = 0
            
            for timestamp, var, value in all_changes:
                # Ensure timestamp is strictly increasing (add 1ps if needed)
                if timestamp <= current_time:
                    timestamp = current_time + 1
                
                writer.change(var, timestamp, value)
                current_time = timestamp
                change_count += 1
            
            print(f"Successfully wrote {change_count} changes to VCD file")
            if channel_vars:
                print(f"  Channel signals: {len(channel_vars)}")
            if dac_vars:
                print(f"  DAC signals: {len(dac_vars)}")
            if adc_vars:
                print(f"  ADC signals: {len(adc_vars)}")
            writer.close()


    # DAC Methods
    def resolve_dac(self, dac: str) -> None:
        """Resolve DAC signal data.

        Parameters
        ----------
        dac : str
            DAC name
        """
        self.dac_data[dac][0].resolve(self.end_time)
        self.dac_data[dac][0].sim_data['voltage'] = np.zeros(
            len(self.dac_data[dac][0].sim_data['voltage'])
        )
        self.dac_data[dac][0].sim_data['voltage_imag'] = np.zeros(
            len(self.dac_data[dac][0].sim_data['voltage_imag']),
            dtype=np.complex128
        )
        for chan in self.dac_data[dac][1]:
            self.channel_data[chan].resolve(self.end_time)
            try:
                self.dac_data[dac][0].sim_data['voltage'] += (
                    self.channel_data[chan].sim_data['voltage']
                )
                self.dac_data[dac][0].sim_data['voltage_imag'] += (
                    self.channel_data[chan].sim_data['voltage_imag']
                )
            except ValueError:
                print(f"Error resolving channel {chan} for DAC {dac}")
        self.dac_data[dac][0].fully_resolved = True

    def graph_dac(self, dac: str) -> None:
        """Plot DAC signal data.

        Parameters
        ----------
        dac : str
            DAC name to plot
        """
        assert (dac in self.dac_data), (
            f"Invalid dac name. dac={dac}, "
            f"dac_data.keys={self.dac_data.keys()}"
        )
        if not self.dac_data[dac][0].fully_resolved:
            self.resolve_dac(dac)
        plt.plot(
            self.dac_data[dac][0].get('time'),
            self.dac_data[dac][0].get('voltage'),
            label=dac
        )
        plt.title(f"{dac}: RF Pulse Simulation Plot", fontsize=22)
        plt.xlabel('Time (FPGA Clock Cycles)', fontsize=18)
        plt.ylabel('Voltage (Normalized)', fontsize=18)
        plt.legend()
        plt.show()

    def graph_dac_complex(self, dac: str) -> None:
        """Plot complex DAC signal data.

        Parameters
        ----------
        dac : str
            DAC name to plot
        """
        assert (dac in self.dac_data), (
            f"Invalid dac name. dac={dac}, "
            f"dac_data.keys={self.dac_data.keys()}"
        )
        if not self.dac_data[dac][0].fully_resolved:
            self.resolve_dac(dac)
        plt.plot(
            self.dac_data[dac][0].get('time'),
            self.dac_data[dac][0].get('voltage'),
            label='Real (I)'
        )
        plt.plot(
            self.dac_data[dac][0].get('time'),
            self.dac_data[dac][0].get('voltage_imag').imag,
            label='Complex (Q)'
        )
        plt.title(f"{dac}: RF Pulse Simulation Plot", fontsize=22)
        plt.xlabel('Time (FPGA Clock Cycles)', fontsize=18)
        plt.ylabel('Voltage (Normalized)', fontsize=18)
        plt.legend()
        plt.show()

    def get_dac_data(self, dac: str) -> Dict[str, np.ndarray]:
        """Get DAC signal data.

        Parameters
        ----------
        dac : str
            DAC name

        Returns
        -------
        Dict[str, np.ndarray]
            DAC signal data dictionary
        """
        assert (dac in self.dac_data), (
            f"Invalid dac name. dac={dac}, "
            f"dac_data.keys={self.dac_data.keys()}"
        )
        if not self.dac_data[dac][0].fully_resolved:
            self.resolve_dac(dac)
        return self.dac_data[dac][0].sim_data


    # ADC Methods
    def graph_adc(self, adc: str) -> None:
        """Plot ADC signal data.

        Parameters
        ----------
        adc : str
            ADC name to plot
        """
        assert(adc in self.adc_data), f"Invalid adc name. adc={adc}, adc_data.keys={self.adc_data.keys()}"
        if self.manual_fproc:
            warnings.warn("Resonators not toggled, ADC behavior is undefined")
        plt.plot(self.adc_data[adc][0].get('time'), self.adc_data[adc][0].get('voltage'), label=adc)
        plt.title(f"{adc}: RF Pulse Simulation Plot", fontsize=22)
        plt.xlabel('Time (FPGA Clock Cycles)', fontsize=18)
        plt.ylabel('Voltage (Normalized)', fontsize=18)
        plt.legend()
        plt.show()

    def get_adc_data(self, adc: str) -> Dict[str, np.ndarray]:
        """Get ADC signal data.

        Parameters
        ----------
        adc : str
            ADC name

        Returns
        -------
        Dict[str, np.ndarray]
            ADC signal data dictionary
        """
        assert(adc in self.adc_data), f"Invalid adc name. adc={adc}, adc_data.keys={self.adc_data.keys()}"
        if self.manual_fproc:
            warnings.warn("Resonators not toggled, ADC behavior is undefined")
        return self.adc_data[adc][0].sim_data


    # Qubit Methods
    def graph_bloch(self, qubit: str) -> None:
        """Plot qubit state on Bloch sphere.

        Parameters
        ----------
        qubit : str
            Qubit name to plot
        """
        assert(qubit in self.qubit_data), (
            f"Invalid qubit name. qubit={qubit}, "
            f"qubit_data.keys={self.qubit_data.keys()}"
        )
        if not self.toggle_qubit:
            warnings.warn("Qubits not toggled, qubit behavior is undefined")
        b = qt.Bloch()

        sx_expect = np.zeros(len(self.qubit_data[qubit]))
        sy_expect = np.zeros(len(self.qubit_data[qubit]))
        sz_expect = np.zeros(len(self.qubit_data[qubit]))
        for i in range(len(self.qubit_data[qubit])):
            sx_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmax() *
                self.qubit_data[qubit][i]
            ).real
            sy_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmay() *
                self.qubit_data[qubit][i]
            ).real
            sz_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmaz() *
                self.qubit_data[qubit][i]
            ).real

        # for i in range(0, len(self.qubit_data[qubit])):
        #     if i == 0:
        #         b.add_points([sx_expect[i], sy_expect[i], sz_expect[i]], colors=['g'], meth='s', alpha=1)
        #     elif i == len(self.qubit_data[qubit]) - 1:
        #         b.add_vectors([sx_expect[i], sy_expect[i], sz_expect[i]])
        #     elif i % 16 == 0:
        #         b.add_points([sx_expect[i], sy_expect[i], sz_expect[i]], colors=['b'], meth='s', alpha=0.8)

        b.add_points([sx_expect[0], sy_expect[0], sz_expect[0]], colors=['g'], meth='s', alpha=1)
        b.add_points(np.array([[sx_expect[i], sy_expect[i], sz_expect[i]] for i in range(1, len(self.qubit_data[qubit]) - 1) 
                      if i % 16 == 0]).T, colors=['b'], meth='s', alpha=0.8)
        b.add_vectors([sx_expect[-1], sy_expect[-1], sz_expect[-1]])

        b.interactive = True
        b.show()
        plt.show()


    def animate_bloch(self, qubit: str, speed: int = 1, save: str = False) -> None:
        """Animate qubit state on Bloch sphere.

        Parameters
        ----------
        qubit : str
            Qubit name to animate
        speed : int, optional
            Animation speed multiplier, defaults to 1
        """
        assert(qubit in self.qubit_data), (
            f"Invalid qubit name. qubit={qubit}, "
            f"qubit_data.keys={self.qubit_data.keys()}"
        )
        if not self.toggle_qubit:
            warnings.warn("Qubits not toggled, qubit behavior is undefined")
        fig = plt.figure()
        ax = fig.add_subplot(azim=-40, elev=30, projection="3d")
        sphere = qt.Bloch(axes=ax)
        sx_expect = np.zeros(len(self.qubit_data[qubit]))
        sy_expect = np.zeros(len(self.qubit_data[qubit]))
        sz_expect = np.zeros(len(self.qubit_data[qubit]))

        # Use a different colormap that is guaranteed to exist
        nrm = matplotlib.colors.Normalize(0, len(self.qubit_data[qubit]) // 10)
        colors = plt.cm.cool(nrm(range(len(self.qubit_data[qubit]) // 10)))
        colors = [matplotlib.colors.rgb2hex(color) for color in colors]
        fig.suptitle(f"Qubit {qubit} Bloch Sphere Animation")
        time_text = fig.text(
            0.5, 0.05, '', 
            ha='right', 
            fontsize=12, 
            transform=fig.transFigure
        )

        def animate(i):
            nonlocal time_text
            sphere.clear()

            sphere.vector_color = ['r']
            sphere.add_vectors([sx_expect[i], sy_expect[i], sz_expect[i]])
            sphere.point_color = [colors[i // 10]]
            sphere.add_points([
                sx_expect[0:i+1:10],
                sy_expect[0:i+1:10],
                sz_expect[0:i+1:10]
            ])

            time_text.set_text(f"Time: {i // (speed*2)}")
            sphere.render()
            return ax

        for i in range(len(self.qubit_data[qubit])):
            sx_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmax() *
                self.qubit_data[qubit][i]
            ).real
            sy_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmay() *
                self.qubit_data[qubit][i]
            ).real
            sz_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmaz() *
                self.qubit_data[qubit][i]
            ).real

        sx_expect = sx_expect[::2*speed]
        sy_expect = sy_expect[::2*speed]
        sz_expect = sz_expect[::2*speed]

        time_text = ax.text2D(
            0.95, 0.05, '',
            transform=ax.transAxes,
            ha='right',
            fontsize=12
        )

        ani = animation.FuncAnimation(
            fig,
            animate,
            np.arange(len(self.qubit_data[qubit]) // (2*speed)),
            blit=False,
            repeat=False
        )

        if save:
            ani.save('bloch_sphere.gif', fps=20)


    def graph_expectation_values(self, qubit: str) -> None:
        """Plot qubit expectation values.

        Parameters
        ----------
        qubit : str
            Qubit name to plot
        """
        assert(qubit in self.qubit_data), (
            f"Invalid qubit name. qubit={qubit}, "
            f"qubit_data.keys={self.qubit_data.keys()}"
        )
        if not self.toggle_qubit:
            warnings.warn("Qubits not toggled, qubit behavior is undefined")
        tlist = np.linspace(
            0, 
            len(self.qubit_data[qubit]),
            len(self.qubit_data[qubit])
        )
        sx_expect = np.zeros(len(self.qubit_data[qubit]))
        sy_expect = np.zeros(len(self.qubit_data[qubit]))
        sz_expect = np.zeros(len(self.qubit_data[qubit]))

        for i in range(len(self.qubit_data[qubit])):
            sx_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmax() *
                self.qubit_data[qubit][i]
            ).real
            sy_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmay() *
                self.qubit_data[qubit][i]
            ).real
            sz_expect[i] = (
                self.qubit_data[qubit][i].dag() *
                qt.sigmaz() *
                self.qubit_data[qubit][i]
            ).real

        plt.figure(figsize=(12, 6))
        plt.figure(figsize=(12, 6))

        plt.subplot(3, 1, 1)
        plt.plot(tlist, sx_expect)
        plt.xlabel('Time')
        plt.ylabel('Expectation value of σ_x')
        plt.grid(True)

        plt.subplot(3, 1, 2)
        plt.plot(tlist, sy_expect)
        plt.xlabel('Time')
        plt.ylabel('Expectation value of σ_y')
        plt.grid(True)

        plt.subplot(3, 1, 3)
        plt.plot(tlist, sz_expect)
        plt.xlabel('Time')
        plt.ylabel('Expectation value of σ_z')
        plt.grid(True)

        plt.tight_layout()
        plt.show()


    def get_qubit_data(self, qubit: str) -> Dict[str, Union[np.ndarray, List[qt.Qobj]]]:
        """Get qubit state data.

        Parameters
        ----------
        qubit : str
            Qubit name

        Returns
        -------
        Dict[str, Union[np.ndarray, List[qt.Qobj]]]
            Qubit state data dictionary
        """
        assert (qubit in self.qubit_data), (
            f"Invalid qubit name. qubit={qubit}, "
            f"qubit_data.keys={self.qubit_data.keys()}"
        )
        if not self.toggle_qubit:
            warnings.warn("Qubits not toggled, qubit behavior is undefined")
        return self.qubit_data[qubit]

    # Core Methods
    def get_commands(self, core: str) -> List[Dict[str, Any]]:
        """Get commands executed by a core.

        Parameters
        ----------
        core : str
            Core name

        Returns
        -------
        List[Dict[str, Any]]
            List of commands executed by the core
        """
        assert (core in self.commands), (
            f"Invalid core name. core={core}, "
            f"commands.keys={self.commands.keys()}"
        )
        return self.commands[core]

    def get_registers(self, core: str) -> List[int]:
        """Get register values for a core.

        Parameters
        ----------
        core : str
            Core name

        Returns
        -------
        List[int]
            Register values for the core
        """
        assert (core in self.registers), (
            f"Invalid core name. core={core}, "
            f"registers.keys={self.registers.keys()}"
        )
        return self.registers[core]

    # Function Processor Methods
    def get_fproc(self) -> List[float]:
        """Get function processor results.

        Returns
        -------
        List[float]
            Function processor results
        """
        return self.fproc

    # IQ
    def graph_iq(self) -> None:
        """Plot IQ measurement values."""
        if not self.toggle_qubit:
            warnings.warn("Qubits not toggled, qubit behavior is undefined")
        real = self.iq_values.real
        imag = self.iq_values.imag

        plt.scatter(real, imag)
        plt.xlabel('Real (I)')
        plt.ylabel('Imaginary (Q)')
        plt.title('IQ Measurement Plots')
        plt.show()

    def get_env_buffers(self, chan: str) -> List[np.ndarray]:
        """Get envelope buffers for a channel.

        Parameters
        ----------
        chan : str
            Channel name

        Returns
        -------
        List[np.ndarray]
            List of envelope buffers
        """
        assert (chan in self.env_buffers), (
            f"Invalid channel name. chan={chan}, "
            f"env_buffers.keys={self.env_buffers.keys()}"
        )
        return self.env_buffers[chan]

    def get_freq_buffers(self, chan: str) -> List[np.ndarray]:
        """Get frequency buffers for a channel.

        Parameters
        ----------
        chan : str
            Channel name

        Returns
        -------
        List[np.ndarray]
            List of frequency buffers
        """
        assert (chan in self.freq_buffers), (
            f"Invalid channel name. chan={chan}, "
            f"freq_buffers.keys={self.freq_buffers.keys()}"
        )
        return self.freq_buffers[chan]

    def get_iq_values(self) -> np.ndarray:
        """Get IQ measurement values.

        Returns
        -------
        np.ndarray
            IQ measurement values
        """
        return self.iq_values

    def plot_iq_values(self) -> None:
        """Plot IQ measurement values."""
        iq_values = self.get_iq_values()
        plt.figure(figsize=(10, 10))
        plt.scatter(iq_values[:, 0], iq_values[:, 1])
        plt.xlabel('I', fontsize=18)
        plt.ylabel('Q', fontsize=18)
        plt.title('IQ Measurement Plots')
        plt.show()

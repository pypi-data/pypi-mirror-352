"""Hardware configuration module for quantum circuit emulation.

This module provides configuration classes for managing hardware parameters, including
FPGA settings, DACs, and ADCs for the quantum emulator.
"""
import json
import warnings

class HWConfig:
    """Hardware configuration manager for FPGA settings, DACs, and ADCs.
    
    Attributes
    ----------
    freq : float
        FPGA clock frequency
    alu_instr_clks : int
        Clock cycles for ALU instructions
    jump_cond_clks : int
        Clock cycles for conditional jumps
    jump_fproc_clks : int
        Clock cycles for function processor jumps
    pulse_regwrite_clks : int
        Clock cycles for pulse register writes
    pulse_load_clks : int
        Clock cycles for pulse loads
    cordic_delay : int
        CORDIC algorithm delay
    phasein_delay : int
        Phase input delay
    qclk_delay : int
        Quantum clock delay
    cstrobe_delay : int
        Control strobe delay
    phase_rst_delay : int
        Phase reset delay
    num_cores : int
        Number of quantum cores
    dacs : dict
        DAC channel assignments
    adcs : dict
        ADC channel assignments
    fproc_measurement_latency : int
        Function processor measurement latency
    adc_response_latency : int
        ADC response latency
    num_dacs : int
        Number of DACs
    num_adcs : int
        Number of ADCs
    """

    def __init__(self, filepath):
        """Initialize hardware configuration from a JSON file.

        Parameters
        ----------
        filepath : str
            Path to the hardware configuration JSON file

        Raises
        ------
        ValueError
            If filepath is empty or if there's an error loading the configuration
        """
        if filepath == "":
            raise ValueError("Hardware configuration path is empty.")
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                hwconfig = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Unable to load hardware configuration: {e}") from e

        if 'fpga' in hwconfig:
            if 'freq' in hwconfig['fpga']:
                self.freq = hwconfig['fpga']['freq']
            else:
                warnings.warn("Hardware configuration does not contain fpga freq key, default value is being used")
                self.freq = 500e6
            if 'alu_instr_clks' in hwconfig['fpga']:
                self.alu_instr_clks = hwconfig['fpga']['alu_instr_clks']
            else:
                warnings.warn("Hardware configuration does not contain fpga alu_instr_clks key, default value is being used")
                self.alu_instr_clks = 4
            if 'jump_cond_clks' in hwconfig['fpga']:
                self.jump_cond_clks = hwconfig['fpga']['jump_cond_clks']
            else:
                warnings.warn("Hardware configuration does not contain fpga jump_cond_clks key, default value is being used")
                self.jump_cond_clks = 6
            if 'jump_fproc_clks' in hwconfig['fpga']:
                self.jump_fproc_clks = hwconfig['fpga']['jump_fproc_clks']
            else:
                warnings.warn("Hardware configuration does not contain fpga jump_fproc_clks key, default value is being used")
                self.jump_fproc_clks = 8
            if 'pulse_regwrite_clks' in hwconfig['fpga']:
                self.pulse_regwrite_clks = hwconfig['fpga']['pulse_regwrite_clks']
            else:
                warnings.warn("Hardware configuration does not contain fpga pulse_regwrite_clks key, default value is being used")
                self.pulse_regwrite_clks = 3
            if 'pulse_load_clks' in hwconfig['fpga']:
                self.pulse_load_clks = hwconfig['fpga']['pulse_load_clks']
            else:
                warnings.warn("Hardware configuration does not contain fpga pulse_load_clks key, default value is being used")
                self.pulse_load_clks = 3
            if 'cordic_delay' in hwconfig['fpga']:
                self.cordic_delay = hwconfig['fpga']['cordic_delay']
            else:
                warnings.warn("Hardware configuration does not contain fpga cordic_delay key, default value is being used")
                self.cordic_delay = 47
            if 'phasein_delay' in hwconfig['fpga']:
                self.phasein_delay = hwconfig['fpga']['phasein_delay']
            else:
                warnings.warn("Hardware configuration does not contain fpga phasein_delay key, default value is being used")
                self.phasein_delay = 1
            if 'qclk_delay' in hwconfig['fpga']:
                self.qclk_delay = hwconfig['fpga']['qclk_delay']
            else:
                warnings.warn("Hardware configuration does not contain fpga qclk_delay key, default value is being used")
                self.qclk_delay = 4
            if 'cstrobe_delay' in hwconfig['fpga']:
                self.cstrobe_delay = hwconfig['fpga']['cstrobe_delay']
            else:
                warnings.warn("Hardware configuration does not contain fpga cstrobe_delay key, default value is being used")
                self.cstrobe_delay = 2
            if 'phase_rst_delay' in hwconfig['fpga']:
                self.phase_rst_delay = hwconfig['fpga']['phase_rst_delay']
            else:
                warnings.warn("Hardware configuration does not contain fpga phase_rst_delay key, default value is being used")
                self.phase_rst_delay = 9
            if 'num_cores' in hwconfig['fpga']:
                self.num_cores = hwconfig['fpga']['num_cores']
            else:
                warnings.warn("Hardware configuration does not contain fpga num_cores key, default value is being used")
                self.num_cores = 1
        else:
            warnings.warn("Hardware configuration does not contain fpga key, default values are being used")
            self.freq = 500e6
            self.alu_instr_clks = 4
            self.jump_cond_clks = 5
            self.jump_fproc_clks = 8
            self.pulse_regwrite_clks = 1
            self.pulse_load_clks = 1
            self.num_cores = 1
        if 'dacs' in hwconfig:
            self.dacs = hwconfig['dacs']
        else:
            warnings.warn("Hardware configuration does not contain dacs key, no dacs being assigned")
            self.dacs = {}
        if 'adcs' in hwconfig:
            self.adcs = hwconfig['adcs']
        else:
            warnings.warn("Hardware configuration does not contain adcs key, no adcs being assigned")
            self.adcs = {}

        if 'fproc_measurement_latency' in hwconfig:
            self.fproc_measurement_latency = hwconfig['fproc_measurement_latency']
        else:
            warnings.warn("Hardware configuration does not contain fproc_measurement_latency key, default value is being used")
            self.fproc_measurement_latency = 1
        if 'adc_response_latency' in hwconfig:
            self.adc_response_latency = hwconfig['adc_response_latency']
        else:
            warnings.warn("Hardware configuration does not contain num_dacs key, default value is being used")
            self.num_dacs = 1
        if 'num_dacs' in hwconfig:
            self.num_dacs = hwconfig['num_dacs']
        else:
            warnings.warn("Hardware configuration does not contain num_dacs key, default value is being used")
            self.num_dacs = 1
        if 'num_adcs' in hwconfig:
            self.num_adcs = hwconfig['num_adcs']
        else:
            warnings.warn("Hardware configuration does not contain num_adcs key, default value is being used")
            self.num_adcs = 1
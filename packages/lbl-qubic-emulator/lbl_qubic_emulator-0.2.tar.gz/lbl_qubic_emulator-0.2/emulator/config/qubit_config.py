"""Qubit configuration module for quantum circuit emulation.

This module provides configuration classes for managing qubit parameters and their
associated resonators, including frequencies and drive parameters.
"""
import json
import warnings

class QubitConfig:
    """Configuration manager for quantum bits and their associated resonators.
    
    Attributes
    ----------
    num_qubits : int
        Number of qubits in the configuration
    qubits : dict
        Dictionary of qubit configurations indexed by qubit name
    resonators : dict
        Dictionary of resonator configurations indexed by resonator name
    """

    def __init__(self, filepath):
        """Initialize qubit configuration from a JSON file.

        Parameters
        ----------
        filepath : str
            Path to the qubit configuration JSON file

        Raises
        ------
        ValueError
            If filepath is empty or if there's an error loading the configuration
        """
        if filepath == "":
            raise ValueError("Qubit configuration path is empty.")     
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                qubitconfig = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Unable to load qubit configuration: {e}") from e
        if 'num_qubits' in qubitconfig:
            self.num_qubits = qubitconfig['num_qubits']
        else:
            self.num_qubits = 1
        self.qubits = {}
        for name, qubit in qubitconfig['qubits'].items():
            self.qubits[name] = IndividualQubitConfig()
            if 'freq' in qubit:
                self.qubits[name].freq = qubit['freq']
            else:
                warnings.warn("Qubit configuration does not contain freq key, default value is being used")
                self.qubits[name].freq = 5e9
            if 'readfreq' in qubit:
                self.qubits[name].readfreq = qubit['readfreq']
            else:
                warnings.warn("Qubit configuration does not contain readfreq key, default value is being used")
                self.qubits[name].readfreq = 5e9
            if 'Omega' in qubit:
                self.qubits[name].Omega = qubit['Omega']
            else:
                warnings.warn("Qubit configuration does not contain Omega key, default value is being used")
                self.qubits[name].Omega = 0.1
        self.resonators = {}
        for name, resonator in qubitconfig['resonators'].items():
            self.resonators[name] = IndividualResonatorConfig()
            if 'Q' in resonator:
                self.resonators[name].Q = resonator['Q']
            else:
                warnings.warn("Resonator configuration does not contain Q key, default value is being used")
                self.resonators[name].Q = 10000
            if 'resonant_frequency_0' in resonator:
                self.resonators[name].resonant_frequency_0 = resonator['resonant_frequency_0']
            else:
                warnings.warn("Resonator configuration does not contain resonant_frequency_0 key, default value is being used")
                self.resonators[name].resonant_frequency_0 = 5e9
            if 'resonant_frequency_1' in resonator:
                self.resonators[name].resonant_frequency_1 = resonator['resonant_frequency_1']
            else:
                warnings.warn("Resonator configuration does not contain resonant_frequency_1 key, default value is being used")
                self.resonators[name].resonant_frequency_1 = 5e9

class IndividualQubitConfig:
    """Configuration for a single qubit with frequency and drive parameters.
    
    Attributes
    ----------
    freq : float
        Qubit frequency
    readfreq : float
        Readout frequency for the qubit
    Omega : float
        Rabi frequency/drive amplitude
    """

    def __init__(self):
        """Initialize an empty qubit configuration."""
        self.freq = None
        self.readfreq = None
        self.omega = None

class IndividualResonatorConfig:
    """Configuration for a single resonator with Q-factor and resonant frequencies.
    
    Attributes
    ----------
    Q : float
        Quality factor of the resonator
    resonant_frequency_0 : float
        Resonant frequency corresponding to qubit state |0⟩
    resonant_frequency_1 : float
        Resonant frequency corresponding to qubit state |1⟩
    """

    def __init__(self):
        """Initialize an empty resonator configuration."""
        self.Q = None
        self.resonant_frequency_0 = None
        self.resonant_frequency_1 = None
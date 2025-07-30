"""Module for quantum bit simulation and manipulation.

This module provides the Qubit class for simulating quantum bits and their interactions
with control pulses and measurements.
"""

from typing import Dict, Any
import numpy as np
import qutip as qt
from scipy.interpolate import interp1d

class Qubit:
    """Class representing a qubit that can be manipulated and visualized with gates and 
    measurements.

    This class simulates a quantum bit's behavior under various control pulses and measurements,
    tracking its state evolution over time.

    Attributes
    ----------
    name : str
        The name of this qubit, convention tbd, most likely just Q#
    freq : float
        The frequency that this qubit oscillates at in Hz
    curr_state : QObj
        The current state of the qubit, a 2-dimensional ket
    sim_data : List[QObj]
        A list of previous quantum states of the qubit in the current simulation
    x90_amp : float
        A float value provided by configuration files that gives the amplitude needed for an X90
        gate. This tunes the qubits' gate response so that the pulses that are supposed to be
        X90s rotate exactly 90 degrees.

    Parameters
    ----------
    name : str
        Identifier for this qubit. Convention tbd, most likely just Q#
    qubitconfig : Dict[str, Any]
        Configuration dictionary containing qubit parameters
    """
    def __init__(self, name: str, qubitconfig: Dict[str, Any]) -> None:
        """Initialize a new qubit with the given configuration.

        Parameters
        ----------
        name : str
            Identifier for this qubit
        qubitconfig : Dict[str, Any]
            Configuration dictionary containing qubit parameters
        """
        self.name = name
        self.freq = qubitconfig.freq
        self.x90_amp = qubitconfig.Omega
        self.curr_state = qt.basis(2, 0) # |0>
        self.sim_data = []

    def apply_pulse_gate(self, drive_freq: float, amp: float, phase: float,
                        envelope: np.ndarray, tstart: int, twidth: int,
                        samples_per_clk: int, interp_ratio: int) -> None:
        """Apply a control pulse to the qubit.

        Parameters
        ----------
        drive_freq : float
            Drive frequency of the pulse in Hz
        amp : float
            Amplitude of the pulse
        phase : float
            Phase of the pulse in radians
        envelope : np.ndarray
            Envelope shape of the pulse
        tstart : int
            Start time of the pulse in clock cycles
        twidth : int
            Width of the pulse in clock cycles
        samples_per_clk : int
            Samples per clock of the channel generating the pulse
        interp_ratio : int
            Internpolation ratio of the channel generating the pulse
        """
        for _ in range(len(self.sim_data) - (tstart*samples_per_clk//interp_ratio)):
            self.sim_data.append(self.curr_state)

        # Difference between drive and qubit frequency
        delta_omega = (self.freq - drive_freq) * 1e-9 * 2
        phi = phase # Phase shift of pulse
        phi *= np.pi / 65536
        amp /= 32767
        tlist = np.linspace(0, twidth, twidth * samples_per_clk//interp_ratio)
        if envelope is None:
            envelope = np.ones(len(tlist))
        integral = np.trapz(envelope, tlist)
        omega = (np.pi / 2 / integral) * (1 / self.x90_amp)
        envelope_interp = interp1d(tlist, envelope, kind='linear', fill_value='extrapolate')
        sigma_plus = qt.sigmap()
        sigma_minus = qt.sigmam()

        
        def H(t):
            return omega/2 * amp * envelope_interp(t) * np.exp(1j*(delta_omega*t + phi)) * sigma_plus + omega/2 * amp * envelope_interp(t)* np.exp(-1j*(delta_omega*t + phi)) * sigma_minus
        H_t = qt.QobjEvo(H)
        result = qt.mesolve(H_t, self.curr_state, tlist, [], [], options={'nsteps': 100})
        states = result.states

        for _, state in enumerate(states):
            self.sim_data.append(state)
        self.curr_state = self.sim_data[-1]

    def measure(self) -> int:
        """Perform a measurement on the qubit.

        Returns
        -------
        Tuple[float, float]
            A tuple containing (probability of |0>, probability of |1>)
        """
        expectation = qt.expect(qt.sigmaz(), self.curr_state)
        p = (1 + expectation) / 2
        return int(np.random.random() > p)

    def end_sim(self) -> np.ndarray:
        """End the current simulation and return the final state.

        Returns
        -------
        np.ndarray
            The final quantum state of the qubit
        """
        return_data = np.array(self.sim_data)
        self.sim_data = []
        self.curr_state = qt.basis(2, 0) # Reset state to |0>
        return return_data

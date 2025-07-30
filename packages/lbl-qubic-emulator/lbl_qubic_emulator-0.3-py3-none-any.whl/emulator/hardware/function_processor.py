"""Function processor module for quantum emulation.

This module provides the FunctionProcessor class for handling function instructions
during quantum circuit simulation, including measurement processing and value storage.
"""

from typing import Dict, List, Optional, Any


class FunctionProcessor:
    """Process and manage function instructions for quantum emulation.

    This class handles the processing of instructions during simulation, resolving them
    into low-level instructions that depend on time, index, and value. It is updated
    every clock cycle.

    Attributes
    ----------
    measurements : List[int]
        List of measurements held by the function processor
    measurement_latency : int
        Number of clock cycles between readout completion and measurement entry
    instructions : List[Dict[str, Any]]
        List of dictionaries detailing when measurements will be added
    values : List[int]
        List of current values in the function processor
    value_queue : List[Dict[str, Any]]
        Queue of values waiting to be processed
    measurement_ind : Dict[str, int]
        Dictionary tracking measurement indices for each core
    manual_measurements : bool
        Flag indicating if measurements are manually controlled
    """

    def __init__(self, latency: int) -> None:
        """Initialize the FunctionProcessor.

        Parameters
        ----------
        latency : int
            Number of clock cycles between readout completion and measurement entry.
            Provided by Emulator via config file.
        """
        self.measurements = [0 for _ in range(32)]
        self.values = [0 for _ in range(32)]
        self.measurement_latency = latency
        self.instructions = []
        self.value_queue = []
        self.measurement_ind = {}
        self.manual_measurements = False

    def read_instructions(self, instructions: List[Dict[str, Any]]) -> None:
        """Load function processor instructions before execution.

        During simulation, these instructions will be executed at the correct times
        and store measurements in the function processor array.

        Parameters
        ----------
        instructions : List[Dict[str, Any]]
            List of instruction dictionaries containing:
            - core: Core taking the measurement
            - time: Time to take the measurement
            - index: Measurement index
            - value: Value to store
        """
        self.instructions = instructions
        self.manual_measurements = True
        self.value_queue.extend([instr for instr in self.instructions if 'time' in instr])
        self.instructions = [instr for instr in self.instructions if 'time' not in instr]

    def update(self, core: str, time: int) -> None:
        """Update function processor state for the current clock cycle.

        Parameters
        ----------
        core : str
            Core identifier
        time : int
            Current simulation time
        """
        for instr in self.instructions:
            if instr['core'] == core:
                if core not in self.measurement_ind and instr['meas'] == 1:
                    self.value_queue.append({
                        'core': core,
                        'time': time + self.measurement_latency,
                        'value': instr['value']
                    })
                    self.measurement_ind[core] = 2
                elif self.measurement_ind[core] == instr['meas']:
                    self.value_queue.append({
                        'core': core,
                        'time': time + self.measurement_latency,
                        'value': instr['value']
                    })
                    self.measurement_ind[core] += 1

    def check_queue(self, time: int, tag: Optional[str] = None) -> None:
        """Check and process queued values.

        Parameters
        ----------
        time : int
            Current simulation time
        tag : Optional[str], optional
            Debug tag, defaults to None
        """
        to_pop = []
        for i, instr in enumerate(self.value_queue):
            if time == instr['time']:
                self.measurements[int(instr['core'][1])] = instr['value']
                self.values[int(instr['core'][1])] = instr['value']
                to_pop.append(i)
                if tag:
                    print(f"FPROC Updated at time {time}, values: {self.values}")

        for i in to_pop:
            self.value_queue.pop(i)

    def clear(self) -> None:
        """Clear all function processor values and measurements."""
        self.measurements = [0 for _ in range(32)]
        self.values = [0 for _ in range(32)]
        self.instructions = []
        self.measurement_ind = {}
        self.manual_measurements = False

    def insert_value(self, index: int, value: int) -> None:
        """Insert a value into the function processor.

        Parameters
        ----------
        index : int
            Value index
        value : int
            Value to insert
        """
        if not self.manual_measurements:
            self.measurements[index] = value
            self.values[index] = value

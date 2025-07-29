# src/pyneurorg/simulation/simulator.py

"""
Defines the Simulator class for orchestrating pyneurorg simulations.

The Simulator class takes an Organoid instance, allows adding monitors,
constructs a Brian2 Network, and runs the simulation. It can also interact
with an MEA for targeted stimulation.
"""

import brian2 as b2
import numpy as np 
from ..organoid.organoid import Organoid 
from ..mea.mea import MEA 
from ..electrophysiology import brian_monitors as pbg_monitors
import traceback # For more detailed error printing during debugging phases

class Simulator:
    """
    Orchestrates Brian2 simulations for a given pyneurorg Organoid,
    optionally interacting with an MEA for stimulation.
    """

    def __init__(self, organoid: Organoid, mea: MEA = None, brian2_dt=None):
        """
        Initializes a new Simulator instance.

        Parameters
        ----------
        organoid : pyneurorg.organoid.organoid.Organoid
            The pyneurorg Organoid instance to be simulated.
        mea : pyneurorg.mea.mea.MEA, optional
            An MEA instance associated with this simulation for stimulation
            and potentially recording (default: None).
        brian2_dt : brian2.units.fundamentalunits.Quantity, optional
            The default clock dt for the simulation. If None, Brian2's default
            will be used (typically 0.1*ms).
        """
        if not isinstance(organoid, Organoid):
            raise TypeError("organoid must be an instance of pyneurorg.organoid.Organoid.")
        if mea is not None and not isinstance(mea, MEA):
            raise TypeError("mea must be an instance of pyneurorg.mea.MEA or None.")

        self.organoid = organoid
        self.mea = mea
        self.brian_network = None
        self.monitors = {}  # Stores user-named monitors: {'monitor_key': brian2_monitor_object}
        
        if brian2_dt is not None:
            if not isinstance(brian2_dt, b2.Quantity) or not (brian2_dt.dimensions == b2.second.dimensions):
                raise TypeError("brian2_dt must be a Brian2 Quantity with time units.")
            self.brian_dt = brian2_dt
            b2.defaultclock.dt = self.brian_dt  # Set the default clock for this simulation context
        else:
            self.brian_dt = b2.defaultclock.dt # Use Brian2's current default dt
        
        # Collect all Brian2 objects that need to be part of the network
        self._network_objects = list(self.organoid.brian2_objects) 
        self._stimulus_current_sources = [] # To keep references to TimedArray objects used for stimuli
        self._stimulus_namespace_counter = 0 # For generating unique names for TimedArrays in namespaces
        # Tracks (group_name, cumulative_stim_var_name) for which a reset operation has been added
        self._cumulative_stim_vars_reset_added = set() 

    def set_mea(self, mea_instance: MEA):
        """
        Sets or updates the MEA associated with this simulator.

        Parameters
        ----------
        mea_instance : pyneurorg.mea.mea.MEA
            The MEA instance to associate.
        """
        if not isinstance(mea_instance, MEA):
            raise TypeError("mea_instance must be an instance of pyneurorg.mea.MEA.")
        self.mea = mea_instance
        print(f"Simulator MEA set to: {mea_instance.name}")

    def add_stimulus(self, electrode_id: int, stimulus_waveform: b2.TimedArray,
                     target_group_name: str, influence_radius,
                     cumulative_stim_var: str = 'I_stimulus_sum',
                     flag_variable_template: str = "stf{id}"):
        """
        Adds a stimulus to be applied via a specified MEA electrode to nearby neurons.

        This method configures a boolean flag (e.g., 'stf0') for targeted neurons 
        within the specified NeuronGroup. It then uses Brian2's `run_regularly` 
        mechanism to update a `cumulative_stim_var` (e.g., 'I_stimulus_sum') 
        in the neuron model. 
        A reset operation for `cumulative_stim_var` is added once per group to ensure
        it's zeroed at the start of each time step before stimuli are summed.
        The actual stimulus application uses boolean multiplication within the 
        `run_regularly` code, effectively applying the `stimulus_waveform` only 
        to neurons where their specific flag is True.

        Parameters
        ----------
        electrode_id : int
            The ID (index) of the MEA electrode from which the stimulus originates.
        stimulus_waveform : brian2.input.timedarray.TimedArray
            The pre-generated stimulus current (e.g., from stimulus_generator module).
            Its values should have current dimensions (e.g., b2.amp).
        target_group_name : str
            The name of the NeuronGroup within the organoid to target.
        influence_radius : float or brian2.units.fundamentalunits.Quantity
            The radius around the electrode within which neurons are considered targets.
            If a float, it is assumed to be in micrometers (um).
        cumulative_stim_var : str, optional
            The name of the variable in the target neuron model that accumulates 
            stimulus currents (default: 'I_stimulus_sum'). This variable must be 
            defined in the neuron's equations (e.g., `I_stimulus_sum : amp`).
        flag_variable_template : str, optional
            A template string for the boolean flag variable name in the neuron model.
            '{id}' will be replaced by `electrode_id`.
            Example: "stf{id}" results in "stf0", "stf1", etc. Default is "stf{id}".
            This flag variable must exist in the neuron model's equations.
        """
        if self.mea is None: 
            raise ValueError("No MEA has been set for this simulator. Call set_mea() or provide at __init__.")
        if not isinstance(stimulus_waveform, b2.TimedArray): 
            raise TypeError("stimulus_waveform must be a Brian2 TimedArray.")

        target_ng = self.organoid.get_neuron_group(target_group_name)

        if cumulative_stim_var not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' must have a variable "
                                 f"'{cumulative_stim_var}' for summing stimuli. "
                                 f"Available variables: {list(target_ng.variables.keys())}")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        if current_flag_name not in target_ng.variables:
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have the boolean flag variable "
                f"'{current_flag_name}' defined in its equations. (Template: '{flag_variable_template}'). "
                f"Ensure your neuron model (e.g., via num_stim_flags) defines this variable."
            )

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            organoid=self.organoid, neuron_group_name=target_group_name,
            electrode_id=electrode_id, radius=influence_radius
        )

        if len(target_neuron_indices_np) == 0:
            print(f"Warning: No neurons found within radius {influence_radius} of electrode {electrode_id} "
                  f"in group '{target_group_name}'. Stimulus will not be applied for this call.")
            return

        # 1. Set the specific boolean flag for the targeted neurons
        # It's assumed the neuron model initializes these flags to False.
        # If add_stimulus is called multiple times for the same electrode but different params,
        # this will reset the flag for previous targets of this specific flag.
        getattr(target_ng, current_flag_name)[:] = False 
        getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True
        
        # 2. Ensure TimedArray is in the NeuronGroup's namespace with a unique name
        # This name will be used in the run_regularly code string.
        ta_name_in_ns = stimulus_waveform.name
        is_generic_ta_name = ta_name_in_ns is None or \
                             ta_name_in_ns.startswith(('_timedarray', 'timedarray')) # Common Brian2 default prefixes
        
        if is_generic_ta_name or \
           (ta_name_in_ns in target_ng.namespace and \
            target_ng.namespace[ta_name_in_ns] is not stimulus_waveform): # Name collision with a different TA
            ta_name_in_ns = f'pyneurorg_stim_ta_e{electrode_id}_{self._stimulus_namespace_counter}'
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform
        
        # 3. Ensure there's an operation to reset the cumulative_stim_var at the start of each time step.
        # This reset operation is added only ONCE per (target_group_name, cumulative_stim_var) combination.
        reset_op_key = (target_group_name, cumulative_stim_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_stim_var}'
            
            # Determine unit for reset code (e.g. amp or amp/meter**2 for HH)
            var_to_reset_unit_str = "amp" # Default
            if target_ng.variables[cumulative_stim_var].dim == (b2.amp/b2.meter**2).dim:
                 var_to_reset_unit_str = "amp/meter**2"
            reset_code = f"{cumulative_stim_var} = 0*{var_to_reset_unit_str}"
            
            reset_operation = target_ng.run_regularly(
                code=reset_code, 
                dt=self.brian_dt, # Run every simulation step
                when='start',     # Run at the very beginning of the step
                order=-1,         # Run before other 'start' operations that might sum to this variable
                name=reset_op_name 
            )
            if reset_operation not in self._network_objects:
                self._network_objects.append(reset_operation)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)
            print(f"Added reset operation ('{reset_op_name}') for '{cumulative_stim_var}' in group '{target_group_name}'.")

        # 4. Create the operation to SUM this specific stimulus waveform
        #    to the cumulative_stim_var if the neuron's flag is True, using boolean multiplication.
        sum_code = f"{cumulative_stim_var} = {cumulative_stim_var} + ({current_flag_name} * {ta_name_in_ns}(t))"
        
        op_name = f'sum_stim_e{electrode_id}_to_{cumulative_stim_var}_in_{target_group_name}'
        
        try:
            stim_sum_operation = target_ng.run_regularly(
                code=sum_code, 
                dt=self.brian_dt, 
                when='start', # Run at the start of the step
                order=0,      # Run after the reset operation (order -1 by default)
                name=op_name
            )
            if stim_sum_operation not in self._network_objects:
                self._network_objects.append(stim_sum_operation)
            self._stimulus_current_sources.append(stimulus_waveform) # Keep reference to TA
            print(f"Summing stimulus operation '{op_name}' (using flag '{current_flag_name}') added for electrode {electrode_id}.")
        except Exception as e:
            print(f"Error configuring summing run_regularly for stimulus on '{cumulative_stim_var}': {e}")
            traceback.print_exc() # Print full traceback for detailed error
            # Clean up namespace for TimedArray if summing op failed to prevent issues
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform:
                del target_ng.namespace[ta_name_in_ns]
            raise

    def add_recording(self, monitor_name: str, monitor_type: str, target_group_name: str, **kwargs):
        if monitor_name in self.monitors:
            raise ValueError(f"Monitor with name '{monitor_name}' already exists.")
        target_group = self.organoid.get_neuron_group(target_group_name)
        monitor_object = None
        # Ensure Brian2 monitor object has a unique name if user doesn't provide one
        brian2_monitor_internal_name = kwargs.pop('name', f"pyneurorg_mon_{monitor_name}_{target_group.name}")
        if monitor_type.lower() == "spike":
            monitor_object = pbg_monitors.setup_spike_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "state":
            if 'variables' not in kwargs: raise KeyError("'variables' (str or list) is required for 'state' monitor.")
            monitor_object = pbg_monitors.setup_state_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "population_rate":
            monitor_object = pbg_monitors.setup_population_rate_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        else:
            raise ValueError(f"Unsupported monitor_type: '{monitor_type}'. Supported: 'spike', 'state', 'population_rate'.")
        
        if monitor_object is not None:
            self.monitors[monitor_name] = monitor_object # Store by user-defined name
            if monitor_object not in self._network_objects: 
                self._network_objects.append(monitor_object)
        return monitor_object

    def build_network(self, **network_kwargs):
        # All NeuronGroups, Synapses, Monitors, and run_regularly operations are in _network_objects
        self.brian_network = b2.Network(self._network_objects, **network_kwargs)

    def run(self, duration: b2.units.fundamentalunits.Quantity, report=None, report_period=10*b2.second, **run_kwargs):
        if not isinstance(duration, b2.Quantity) or not (duration.dimensions == b2.second.dimensions):
            raise TypeError("duration must be a Brian2 Quantity with time units.")
        if self.brian_network is None: 
            self.build_network(**run_kwargs.pop('network_kwargs', {})) # Pass network_kwargs if provided
        if self.brian_network is None: 
            raise RuntimeError("Brian2 Network could not be built or is still None after build_network().")
        self.brian_network.run(duration, report=report, report_period=report_period, **run_kwargs)

    def get_data(self, monitor_name: str):
        if monitor_name not in self.monitors: 
            raise KeyError(f"Monitor with name '{monitor_name}' not found. Available monitors: {list(self.monitors.keys())}")
        return self.monitors[monitor_name]

    def store_simulation(self, filename="pyneurorg_sim_state"):
        if self.brian_network is None: 
            print("Warning: Network not built. Nothing to store.")
            return
        self.brian_network.store(name=filename) 
        print(f"Simulation state stored in '{filename}.bri'")

    def restore_simulation(self, filename="pyneurorg_sim_state"):
        # Note: Brian2's restore function restores to the global Brian2 namespace.
        # The current Simulator instance's brian_network object might become stale.
        if self.brian_network is None: # Or even if it exists, it will be replaced
            print("Warning: Network not explicitly built, or will be replaced by restored state.")
        
        b2.restore(name=filename) 
        print(f"Simulation state restored from '{filename}.bri'. Network may need to be rebuilt on next run call.")
        # After restore, all Brian2 objects are updated in the global scope.
        # The Simulator's internal Network object needs to be rebuilt to reflect this.
        self.brian_network = None 
        # Also update the Simulator's dt to the one from the restored defaultclock
        self.brian_dt = b2.defaultclock.dt 

    def __str__(self):
        status = "Built" if self.brian_network else "Not Built"
        num_monitors = len(self.monitors)
        return (f"<Simulator for Organoid '{self.organoid.name}' "
                f"with {num_monitors} user-defined monitor(s). Network Status: {status}>")

    def __repr__(self): 
        return self.__str__()
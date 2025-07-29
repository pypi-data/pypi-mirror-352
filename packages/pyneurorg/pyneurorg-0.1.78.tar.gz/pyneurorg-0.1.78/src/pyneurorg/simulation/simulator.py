# src/pyneurorg/simulation/simulator.py

"""
Defines the Simulator class for orchestrating pyneurorg simulations.

The Simulator class takes an Organoid instance, allows adding monitors,
constructs a Brian2 Network, and runs the simulation.
"""

import brian2 as b2
import numpy as np
from ..organoid.organoid import Organoid
from ..mea.mea import MEA
from ..electrophysiology import brian_monitors as pbg_monitors
from brian2.units.fundamentalunits import DIMENSIONLESS # For dimensionless currents

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
            will be used.
        """
        if not isinstance(organoid, Organoid):
            raise TypeError("organoid must be an instance of pyneurorg.organoid.Organoid.")
        if mea is not None and not isinstance(mea, MEA): # Allow mea to be None initially
            raise TypeError("mea must be an instance of pyneurorg.mea.MEA or None.")

        self.organoid = organoid
        self.mea = mea
        self.brian_network = None
        self.monitors = {}

        if brian2_dt is not None:
            if not isinstance(brian2_dt, b2.Quantity) or not (brian2_dt.dimensions == b2.second.dimensions):
                raise TypeError("brian2_dt must be a Brian2 Quantity with time units.")
            self.brian_dt = brian2_dt
            b2.defaultclock.dt = self.brian_dt
        else:
            self.brian_dt = b2.defaultclock.dt

        self._network_objects = list(self.organoid.brian2_objects)
        self._stimulus_current_sources = [] # To keep track of TimedArray objects
        self._stimulus_namespace_counter = 0
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

    def add_stimulus(self, electrode_id: int, stimulus_waveform: b2.TimedArray,
                     target_group_name: str, influence_radius,
                     cumulative_stim_var: str = 'I_stimulus_sum',
                     flag_variable_template: str = "stf{id}",
                     area_variable_name: str = "area_val"):
        """
        Adds a stimulus to be applied via a specified MEA electrode to nearby neurons.

        Configures a boolean flag for targeted neurons and uses `run_regularly`
        operations to sum the stimulus current into `cumulative_stim_var`.
        If `cumulative_stim_var` is a current density, this method will attempt
        to use `area_variable_name` from the neuron model to convert the
        `stimulus_waveform` (whose values should be in Amperes) to a current density.

        Parameters
        ----------
        electrode_id : int
            The MEA electrode ID to apply the stimulus from.
        stimulus_waveform : brian2.TimedArray
            The stimulus current waveform. Its `dimensions` attribute should reflect
            the physical dimensions of its values (e.g., amp, or dimensionless).
        target_group_name : str
            Name of the NeuronGroup to target.
        influence_radius : brian2.Quantity or float
            Radius around the electrode to affect neurons (in um if float).
        cumulative_stim_var : str, optional
            Name of the variable in the neuron model where stimulus current is summed.
            (default: 'I_stimulus_sum').
        flag_variable_template : str, optional
            Template for the boolean flag variable in neurons (e.g., "stf{id}").
            (default: "stf{id}").
        area_variable_name : str, optional
            Name of the variable in the neuron model representing neuron area (in m^2),
            used if `cumulative_stim_var` is a current density. (default: "area_val").
        """
        if self.mea is None:
            raise ValueError("No MEA set for this simulator. Call set_mea() first.")
        if not isinstance(stimulus_waveform, b2.TimedArray):
            raise TypeError("stimulus_waveform must be a TimedArray.")
        if not (isinstance(influence_radius, b2.Quantity) and influence_radius.dimensions == b2.metre.dimensions) and \
           not isinstance(influence_radius, (int, float)):
            raise TypeError("influence_radius must be a Brian2 Quantity with length units or a number (assumed um).")

        target_ng = self.organoid.get_neuron_group(target_group_name)

        if cumulative_stim_var not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' must have a variable "
                                 f"'{cumulative_stim_var}'. Available: {list(target_ng.variables.keys())}")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        if current_flag_name not in target_ng.variables:
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have the flag variable "
                f"'{current_flag_name}'. (Template: '{flag_variable_template}')"
            )

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            organoid=self.organoid, neuron_group_name=target_group_name,
            electrode_id=electrode_id, radius=influence_radius
        )

        if len(target_neuron_indices_np) == 0:
            print(f"Warning: No neurons found for stimulus from electrode {electrode_id} in group '{target_group_name}'.")
            return

        # 1. Set the specific boolean flag for the targeted neurons
        getattr(target_ng, current_flag_name)[:] = False
        getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True

        # 2. Ensure TimedArray is in the NeuronGroup's namespace with a unique name
        ta_name_in_ns = stimulus_waveform.name
        is_generic_name = ta_name_in_ns is None or \
                          ta_name_in_ns.startswith(('_timedarray', 'timedarray'))
        if is_generic_name or \
           (ta_name_in_ns in target_ng.namespace and \
            target_ng.namespace[ta_name_in_ns] is not stimulus_waveform):
            ta_name_in_ns = f'pyneurorg_stim_ta_{self._stimulus_namespace_counter}'
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform
        
        # 3. Ensure reset operation for cumulative_stim_var is added only once per group/variable
        reset_op_key = (target_group_name, cumulative_stim_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_stim_var}_{np.random.randint(10000)}'
            
            var_to_reset_unit_dim = target_ng.variables[cumulative_stim_var].dim
            if var_to_reset_unit_dim == b2.amp.dim:
                reset_code = f"{cumulative_stim_var} = 0*amp"
            elif var_to_reset_unit_dim == (b2.amp/b2.meter**2).dim:
                reset_code = f"{cumulative_stim_var} = 0*amp/meter**2"
            elif var_to_reset_unit_dim == DIMENSIONLESS: # For dimensionless currents
                 reset_code = f"{cumulative_stim_var} = 0*1"
            else:
                raise TypeError(f"Unsupported unit dimension for {cumulative_stim_var} for reset: {var_to_reset_unit_dim}")

            reset_operation = target_ng.run_regularly(
                reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name
            )
            if reset_operation not in self._network_objects:
                self._network_objects.append(reset_operation)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)

        # 4. Prepare the stimulus application term based on units
        stimulus_application_term = f"{ta_name_in_ns}(t)"
        stim_var_target_dim = target_ng.variables[cumulative_stim_var].dim 
        
        # Correct way to get dimensions of a TimedArray's values
        stimulus_waveform_dim = stimulus_waveform.dimensions 

        if stim_var_target_dim == (b2.amp/b2.meter**2).dim: # Target is current density
            if stimulus_waveform_dim != b2.amp.dim: # TimedArray values must be in Amperes for this conversion
                 raise TypeError(f"Stimulus waveform for current density target '{cumulative_stim_var}' "
                                 f"must have values with current dimensions (e.g., amp), but has {stimulus_waveform_dim}.")
            
            if area_variable_name not in target_ng.variables:
                raise AttributeError(f"NeuronGroup '{target_group_name}' needs an '{area_variable_name}' variable (in m^2) "
                                     f"to convert stimulus current to current density for '{cumulative_stim_var}'.")
            
            area_var_obj_dim = target_ng.variables[area_variable_name].dim
            if area_var_obj_dim != b2.meter.dim**2:
                raise TypeError(f"Variable '{area_variable_name}' in NeuronGroup '{target_group_name}' must have "
                                f"units of area (e.g., m^2), but has dimensions {area_var_obj_dim}.")
            
            if area_variable_name not in target_ng.namespace and hasattr(target_ng, area_variable_name):
                 pass # Assume accessible if it's a state variable

            stimulus_application_term = f"({ta_name_in_ns}(t) / {area_variable_name})"
            print(f"INFO: Stimulus for '{cumulative_stim_var}' will be applied as current density using '{area_variable_name}'.")
        
        elif stim_var_target_dim != stimulus_waveform_dim: 
             raise TypeError(f"Stimulus waveform has dimensions {stimulus_waveform_dim} "
                             f"but target variable '{cumulative_stim_var}' has dimensions {stim_var_target_dim}.")

        # 5. Code for summing stimulus using boolean multiplication
        sum_code = f"{cumulative_stim_var} = {cumulative_stim_var} + ({current_flag_name} * {stimulus_application_term})"
        op_name = f'sum_stim_e{electrode_id}_to_{cumulative_stim_var}_in_{target_group_name}_{np.random.randint(10000)}'
        
        try:
            stim_sum_operation = target_ng.run_regularly(
                sum_code, dt=self.brian_dt, when='start', order=0, name=op_name
            )
            if stim_sum_operation not in self._network_objects:
                self._network_objects.append(stim_sum_operation)
            self._stimulus_current_sources.append(stimulus_waveform)
            print(f"Summing stimulus operation '{op_name}' added for electrode {electrode_id}.")
        except Exception as e:
            print(f"Error configuring summing run_regularly for stimulus on '{cumulative_stim_var}': {e}")
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform:
                del target_ng.namespace[ta_name_in_ns]
            raise

    def add_recording(self, monitor_name: str, monitor_type: str, target_group_name: str, **kwargs):
        """
        Adds a Brian2 monitor to record data from a specified NeuronGroup or Synapses.
        """
        if monitor_name in self.monitors:
            raise ValueError(f"Monitor with name '{monitor_name}' already exists.")
        
        target_object = None
        if target_group_name in self.organoid.neuron_groups:
            target_object = self.organoid.get_neuron_group(target_group_name)
        elif target_group_name in self.organoid.synapses:
            target_object = self.organoid.get_synapses(target_group_name)
        else:
            raise KeyError(f"Target group/object '{target_group_name}' not found in organoid's "
                           f"neuron_groups or synapses.")

        monitor_object = None
        brian2_monitor_internal_name = kwargs.pop('name', f"pyb_mon_{monitor_name}_{target_object.name}_{np.random.randint(10000)}")

        if monitor_type.lower() == "spike":
            if not isinstance(target_object, b2.NeuronGroup):
                raise TypeError("SpikeMonitor can only target NeuronGroup.")
            monitor_object = pbg_monitors.setup_spike_monitor(target_object, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "state":
            if 'variables' not in kwargs:
                raise KeyError("'variables' (str or list) is required for 'state' monitor.")
            monitor_object = pbg_monitors.setup_state_monitor(target_object, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "population_rate":
            if not isinstance(target_object, b2.NeuronGroup):
                raise TypeError("PopulationRateMonitor can only target NeuronGroup.")
            monitor_object = pbg_monitors.setup_population_rate_monitor(target_object, name=brian2_monitor_internal_name, **kwargs)
        else:
            raise ValueError(f"Unsupported monitor_type: '{monitor_type}'. Supported: 'spike', 'state', 'population_rate'.")

        if monitor_object is not None:
            self.monitors[monitor_name] = monitor_object
            if monitor_object not in self._network_objects:
                self._network_objects.append(monitor_object)
        return monitor_object

    def build_network(self, **network_kwargs):
        """
        Constructs the Brian2 Network object from all components.
        """
        self.brian_network = b2.Network(self._network_objects, **network_kwargs)

    def run(self, duration: b2.units.fundamentalunits.Quantity, report=None, report_period=10*b2.second, **run_kwargs):
        """
        Runs the simulation for the specified duration.
        """
        if not isinstance(duration, b2.Quantity) or not (duration.dimensions == b2.second.dimensions):
            raise TypeError("duration must be a Brian2 Quantity with time units.")
        if self.brian_network is None:
            self.build_network(**run_kwargs.pop('network_kwargs', {}))
        if self.brian_network is None: 
            raise RuntimeError("Brian2 Network could not be built.")
        self.brian_network.run(duration, report=report, report_period=report_period, **run_kwargs)

    def get_data(self, monitor_name: str):
        """
        Retrieves a configured monitor object by its user-defined name.
        """
        if monitor_name not in self.monitors:
            raise KeyError(f"Monitor '{monitor_name}' not found. Available: {list(self.monitors.keys())}")
        return self.monitors[monitor_name]

    def store_simulation(self, filename="pyneurorg_sim_state", schedule_name=None):
        """
        Stores the current state of the simulation network.
        """
        if self.brian_network is None:
            print("Warning: Network not built. Nothing to store.")
            return
        self.brian_network.store(name=filename, schedule=schedule_name)
        print(f"Simulation state stored with name '{filename}'.")

    def restore_simulation(self, filename="pyneurorg_sim_state", schedule_name=None):
        """
        Restores a previously stored simulation state.
        Note: This replaces the current network and objects in Brian2's global store.
        The Simulator instance might need to be re-initialized or network rebuilt to reflect changes.
        """
        b2.restore(name=filename, schedule=schedule_name)
        self.brian_dt = b2.defaultclock.dt 
        print(f"Simulation state restored from name '{filename}'.")
        self.brian_network = None 
        self._network_objects = [] 

    def __str__(self):
        status = "Built" if self.brian_network else "Not Built"
        num_monitors = len(self.monitors)
        return (f"<Simulator for Organoid '{self.organoid.name}' "
                f"with {num_monitors} user-defined monitor(s). Network Status: {status}>")

    def __repr__(self):
        return self.__str__()
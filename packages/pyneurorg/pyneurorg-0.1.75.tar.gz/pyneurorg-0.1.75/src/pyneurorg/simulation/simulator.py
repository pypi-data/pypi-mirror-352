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
        """
        if not isinstance(mea_instance, MEA):
            raise TypeError("mea_instance must be an instance of pyneurorg.mea.MEA.")
        self.mea = mea_instance

    def add_stimulus(self, electrode_id: int, stimulus_waveform: b2.TimedArray,
                     target_group_name: str, influence_radius,
                     cumulative_stim_var: str = 'I_stimulus_sum',
                     flag_variable_template: str = "stf{id}",
                     area_variable_name: str = "area_val"): # New parameter
        """
        Adds a stimulus to be applied via a specified MEA electrode to nearby neurons.

        Configures a boolean flag for targeted neurons and uses `run_regularly`
        operations to sum the stimulus current into `cumulative_stim_var`.
        If `cumulative_stim_var` is a current density, this method will attempt
        to use `area_variable_name` from the neuron model to convert the
        `stimulus_waveform` (assumed to be in Amperes) to a current density.

        Parameters
        ----------
        electrode_id : int
            The MEA electrode ID to apply the stimulus from.
        stimulus_waveform : brian2.TimedArray
            The stimulus current waveform (values should be in Amperes).
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

        getattr(target_ng, current_flag_name)[:] = False
        getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True

        ta_name_in_ns = stimulus_waveform.name
        is_generic_name = ta_name_in_ns is None or \
                          ta_name_in_ns.startswith(('_timedarray', 'timedarray'))
        if is_generic_name or \
           (ta_name_in_ns in target_ng.namespace and \
            target_ng.namespace[ta_name_in_ns] is not stimulus_waveform):
            ta_name_in_ns = f'pyneurorg_stim_ta_{self._stimulus_namespace_counter}'
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform
        
        # Ensure reset operation for cumulative_stim_var is added only once
        reset_op_key = (target_group_name, cumulative_stim_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_stim_var}'
            
            # Determine the correct reset code based on the variable's unit
            var_to_reset_unit = target_ng.variables[cumulative_stim_var].dim
            if var_to_reset_unit == b2.amp.dim:
                reset_code = f"{cumulative_stim_var} = 0*amp"
            elif var_to_reset_unit == (b2.amp/b2.meter**2).dim:
                reset_code = f"{cumulative_stim_var} = 0*amp/meter**2"
            elif var_to_reset_unit == b2.DIMENSIONLESS: # For dimensionless currents (e.g. FHN)
                 reset_code = f"{cumulative_stim_var} = 0*1"
            else:
                raise TypeError(f"Unsupported unit dimension for {cumulative_stim_var}: {var_to_reset_unit}")

            reset_operation = target_ng.run_regularly(
                reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name
            )
            if reset_operation not in self._network_objects:
                self._network_objects.append(reset_operation)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)

        # Prepare the stimulus application term
        stimulus_application_term = f"{ta_name_in_ns}(t)"
        stim_var_dim = target_ng.variables[cumulative_stim_var].dim

        if stim_var_dim == (b2.amp/b2.meter**2).dim: # Needs conversion to current density
            if area_variable_name not in target_ng.variables:
                raise AttributeError(f"NeuronGroup '{target_group_name}' needs an '{area_variable_name}' variable (in m^2) "
                                     f"to convert stimulus current to current density for '{cumulative_stim_var}'.")
            
            area_var_obj = target_ng.variables[area_variable_name]
            if area_var_obj.dim != b2.meter.dim**2:
                raise TypeError(f"Variable '{area_variable_name}' in NeuronGroup '{target_group_name}' must have "
                                f"units of area (e.g., m^2), but has {area_var_obj.dim}.")
            
            # Ensure area_variable_name is in the local namespace for run_regularly if it's a parameter
            # If it's a state variable, it's already accessible.
            # If it's a parameter (constant for the group), it should be in ng.namespace
            # or directly accessible. For safety, we ensure it's in the namespace.
            if area_variable_name not in target_ng.namespace and hasattr(target_ng, area_variable_name):
                target_ng.namespace[area_variable_name] = getattr(target_ng, area_variable_name)

            stimulus_application_term = f"({ta_name_in_ns}(t) / {area_variable_name})"
            print(f"INFO: Stimulus for '{cumulative_stim_var}' will be applied as current density using '{area_variable_name}'.")
        
        elif stim_var_dim != stimulus_waveform.values.dim: # Check if stimulus waveform unit matches target var (if not density)
             # stimulus_waveform.values is a Quantity. stimulus_waveform itself is TimedArray.
             # stimulus_waveform.unit gives the unit.
             if stimulus_waveform.unit.dim != stim_var_dim:
                raise TypeError(f"Stimulus waveform has units {stimulus_waveform.unit.dim} "
                                f"but target variable '{cumulative_stim_var}' has units {stim_var_dim}.")


        sum_code = f"{cumulative_stim_var} = {cumulative_stim_var} + ({current_flag_name} * {stimulus_application_term})"
        op_name = f'sum_stim_e{electrode_id}_to_{cumulative_stim_var}_in_{target_group_name}_{np.random.randint(10000)}'
        
        try:
            stim_sum_operation = target_ng.run_regularly(
                sum_code, dt=self.brian_dt, when='start', order=0, name=op_name
            )
            if stim_sum_operation not in self._network_objects:
                self._network_objects.append(stim_sum_operation)
            self._stimulus_current_sources.append(stimulus_waveform) # Keep track of the TimedArray itself
            print(f"Summing stimulus operation '{op_name}' added for electrode {electrode_id}.")
        except Exception as e:
            print(f"Error configuring summing run_regularly for stimulus on '{cumulative_stim_var}': {e}")
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform:
                del target_ng.namespace[ta_name_in_ns]
            raise

    def add_recording(self, monitor_name: str, monitor_type: str, target_group_name: str, **kwargs):
        if monitor_name in self.monitors:
            raise ValueError(f"Monitor with name '{monitor_name}' already exists.")
        
        target_object = None
        if target_group_name in self.organoid.neuron_groups:
            target_object = self.organoid.get_neuron_group(target_group_name)
        elif target_group_name in self.organoid.synapses: # Allow monitoring synapse variables
            target_object = self.organoid.get_synapses(target_group_name)
        else:
            raise KeyError(f"Target group/object '{target_group_name}' not found in organoid.")

        monitor_object = None
        # Ensure unique internal Brian2 name for the monitor
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
        # Ensure all TimedArray objects are explicitly added to the network
        # if they weren't implicitly through NeuronGroup namespace in older Brian2 versions.
        # Modern Brian2 usually handles this, but good to be aware.
        # self._network_objects already contains NeuronGroups which hold TimedArrays in their namespace.
        self.brian_network = b2.Network(self._network_objects, **network_kwargs)
        # print(f"Network built with objects: {[obj.name for obj in self._network_objects]}")


    def run(self, duration: b2.units.fundamentalunits.Quantity, report=None, report_period=10*b2.second, **run_kwargs):
        if not isinstance(duration, b2.Quantity) or not (duration.dimensions == b2.second.dimensions):
            raise TypeError("duration must be a Brian2 Quantity with time units.")
        if self.brian_network is None:
            self.build_network(**run_kwargs.pop('network_kwargs', {}))
        if self.brian_network is None: # Should not happen if build_network is successful
            raise RuntimeError("Brian2 Network could not be built.")
        self.brian_network.run(duration, report=report, report_period=report_period, **run_kwargs)

    def get_data(self, monitor_name: str):
        if monitor_name not in self.monitors:
            raise KeyError(f"Monitor '{monitor_name}' not found. Available: {list(self.monitors.keys())}")
        return self.monitors[monitor_name]

    def store_simulation(self, filename="pyneurorg_sim_state", schedule_name=None):
        if self.brian_network is None:
            print("Warning: Network not built. Nothing to store.")
            return
        self.brian_network.store(name=filename, schedule=schedule_name)
        print(f"Simulation state stored with name '{filename}'.")

    def restore_simulation(self, filename="pyneurorg_sim_state", schedule_name=None):
        # Restoring a network also restores the defaultclock.dt
        # The current network and its objects will be replaced.
        b2.restore(name=filename, schedule=schedule_name)
        self.brian_dt = b2.defaultclock.dt
        print(f"Simulation state restored from name '{filename}'.")
        # After restore, self.brian_network and self._network_objects might be stale.
        # It's often best to re-initialize the Simulator or rebuild the network
        # with the restored objects if further modifications are needed.
        # For simplicity here, we assume the user will re-run or re-build if necessary.
        self.brian_network = None # Mark as not built to force rebuild if run() is called again
        self._network_objects = [] # Clear old objects; they are now part of Brian2's global store
                                   # or need to be re-retrieved.
                                   # A more robust restore would re-populate these.


    def __str__(self):
        status = "Built" if self.brian_network else "Not Built"
        num_monitors = len(self.monitors)
        return (f"<Simulator for Organoid '{self.organoid.name}' "
                f"with {num_monitors} user-defined monitor(s). Network Status: {status}>")

    def __repr__(self):
        return self.__str__()
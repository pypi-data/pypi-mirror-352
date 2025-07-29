# src/pyneurorg/simulation/simulator.py

"""
Defines the Simulator class for orchestrating pyneurorg simulations.

The Simulator class takes an Organoid instance, allows adding monitors,
constructs a Brian2 Network, and runs the simulation. It can also interact
with an MEA for targeted stimulation, supporting both current-based and
current-density-based stimuli.
"""

import brian2 as b2
import numpy as np
from ..organoid.organoid import Organoid
from ..mea.mea import MEA
from ..electrophysiology import brian_monitors as pbg_monitors
from brian2.units.fundamentalunits import DIMENSIONLESS # For dimensionless currents
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
        self.monitors = {}

        if brian2_dt is not None:
            if not isinstance(brian2_dt, b2.Quantity) or not (brian2_dt.dimensions == b2.second.dimensions):
                raise TypeError("brian2_dt must be a Brian2 Quantity with time units.")
            self.brian_dt = brian2_dt
            b2.defaultclock.dt = self.brian_dt
        else:
            self.brian_dt = b2.defaultclock.dt

        self._network_objects = list(self.organoid.brian2_objects)
        self._stimulus_current_sources = []
        self._stimulus_namespace_counter = 0
        self._cumulative_stim_vars_reset_added = set()

    def set_mea(self, mea_instance: MEA):
        """
        Sets or updates the MEA associated with this simulator.
        """
        if not isinstance(mea_instance, MEA):
            raise TypeError("mea_instance must be an instance of pyneurorg.mea.MEA.")
        self.mea = mea_instance
        # print(f"Simulator MEA set to: {mea_instance.name}") # Optional for verbose feedback

    def add_stimulus(self, electrode_id: int, stimulus_waveform: b2.TimedArray,
                     target_group_name: str, influence_radius,
                     cumulative_stim_var: str = 'I_stimulus_sum',
                     flag_variable_template: str = "stf{id}"):
        """
        Adds a current-based stimulus to be applied via a specified MEA electrode.

        This method configures a boolean flag for targeted neurons and uses
        `run_regularly` operations to sum the stimulus current into a
        `cumulative_stim_var` in the neuron model using boolean multiplication.
        It assumes the `stimulus_waveform` values have current units (e.g., Amperes)
        and the `cumulative_stim_var` also has current units.

        Parameters
        ----------
        electrode_id : int
            The MEA electrode ID.
        stimulus_waveform : brian2.TimedArray
            The stimulus waveform. Its `values` attribute (a Brian2 Quantity) should
            have current dimensions (e.g., amp).
        target_group_name : str
            Name of the NeuronGroup to target.
        influence_radius : float or brian2.Quantity
            Radius around the electrode (in um if float).
        cumulative_stim_var : str, optional
            Name of the variable in the neuron model that accumulates stimulus current
            (default: 'I_stimulus_sum'). Expected to have current dimensions.
        flag_variable_template : str, optional
            Template for the boolean flag variable (default: "stf{id}").
        """
        if self.mea is None:
            raise ValueError("No MEA has been set for this simulator. Call set_mea() or provide at __init__.")
        if not isinstance(stimulus_waveform, b2.TimedArray):
            raise TypeError("stimulus_waveform must be a Brian2 TimedArray.")

        target_ng = self.organoid.get_neuron_group(target_group_name)

        if cumulative_stim_var not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' must have variable '{cumulative_stim_var}'.")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        if current_flag_name not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' lacks flag '{current_flag_name}'.")

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            self.organoid, target_group_name, electrode_id, influence_radius
        )

        if len(target_neuron_indices_np) == 0:
            print(f"Warning: No neurons for stimulus from E{electrode_id} in '{target_group_name}'.")
            return

        getattr(target_ng, current_flag_name)[:] = False
        getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True
        
        ta_name_in_ns = stimulus_waveform.name
        is_generic = ta_name_in_ns is None or ta_name_in_ns.startswith(('_timedarray', 'timedarray'))
        if is_generic or (ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is not stimulus_waveform):
            ta_name_in_ns = f'pyorg_stim_ta_e{electrode_id}_{self._stimulus_namespace_counter}'
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform
        
        reset_op_key = (target_group_name, cumulative_stim_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_stim_var}_{np.random.randint(10000)}'
            var_dim = target_ng.variables[cumulative_stim_var].dim
            if var_dim == b2.amp.dim: reset_code = f"{cumulative_stim_var} = 0*amp"
            elif var_dim == DIMENSIONLESS: reset_code = f"{cumulative_stim_var} = 0*1"
            else: raise TypeError(f"Unsupported unit for {cumulative_stim_var} in add_stimulus: {var_dim}")
            
            op = target_ng.run_regularly(reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)

        stim_val_dim = stimulus_waveform.values.dimensions
        if target_ng.variables[cumulative_stim_var].dim != stim_val_dim:
            raise TypeError(f"Stimulus waveform values have dimensions {stim_val_dim}, "
                            f"but target var '{cumulative_stim_var}' has {target_ng.variables[cumulative_stim_var].dim}.")

        sum_code = f"{cumulative_stim_var} = {cumulative_stim_var} + ({current_flag_name} * {ta_name_in_ns}(t))"
        op_name = f'sum_stim_e{electrode_id}_to_{cumulative_stim_var}_in_{target_group_name}_{np.random.randint(10000)}'
        
        try:
            op = target_ng.run_regularly(sum_code, dt=self.brian_dt, when='start', order=0, name=op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._stimulus_current_sources.append(stimulus_waveform)
            print(f"Summing current stimulus op '{op_name}' added for E{electrode_id}.")
        except Exception as e: # pragma: no cover
            print(f"Error in add_stimulus for '{cumulative_stim_var}': {e}")
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform:
                del target_ng.namespace[ta_name_in_ns]
            raise

    def add_current_density_stimulus(self, electrode_id: int, stimulus_waveform_density: b2.TimedArray,
                                     target_group_name: str, influence_radius,
                                     cumulative_density_var: str = 'I_stimulus_sum',
                                     flag_variable_template: str = "stf{id}",
                                     area_variable_name: str = "area_val"):
        """
        Adds a stimulus defined as a current density to be applied via a MEA electrode.

        The `stimulus_waveform_density` values must have current density units.
        The `cumulative_density_var` in the neuron model must also have current
        density units. An `area_variable_name` (e.g., 'area_val' in m^2) must exist
        in the target NeuronGroup for converting the current density stimulus to a current
        if the `cumulative_density_var` expects total current, or for direct application
        if `cumulative_density_var` itself is a density. This method now correctly
        divides the TimedArray (assumed to be current in Amperes) by area_variable_name
        if the target variable is a current density.

        Parameters
        ----------
        electrode_id : int
            The MEA electrode ID.
        stimulus_waveform_density : brian2.TimedArray
            The stimulus waveform. Its `values` attribute (a Brian2 Quantity) should
            have current dimensions (e.g., amp). This method will handle the division
            by area if the target variable is a density.
        target_group_name : str
            Name of the NeuronGroup to target.
        influence_radius : float or brian2.Quantity
            Radius around the electrode (in um if float).
        cumulative_density_var : str, optional
            Name of the variable in the neuron model that accumulates stimulus
            (default: 'I_stimulus_sum'). Expected to have current density dimensions.
        flag_variable_template : str, optional
            Template for the boolean flag variable (default: "stf{id}").
        area_variable_name : str, optional
            Name of the variable in the neuron model representing neuron area (in m^2),
            used to convert the current stimulus to current density. (default: "area_val").
        """
        if self.mea is None:
            raise ValueError("No MEA has been set. Call set_mea() or provide at __init__.")
        if not isinstance(stimulus_waveform_density, b2.TimedArray):
            raise TypeError("stimulus_waveform_density must be a Brian2 TimedArray.")

        target_ng = self.organoid.get_neuron_group(target_group_name)

        if cumulative_density_var not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' must have variable '{cumulative_density_var}'.")

        target_var_dim = target_ng.variables[cumulative_density_var].dimensions
        expected_density_dim = (b2.amp / b2.meter**2).dimensions

        if target_var_dim != expected_density_dim:
            raise TypeError(f"Target variable '{cumulative_density_var}' in '{target_group_name}' "
                            f"must have current density dimensions {expected_density_dim}, but has {target_var_dim}.")

        stimulus_waveform_val_dim = stimulus_waveform_density.values.dimensions
        if stimulus_waveform_val_dim != b2.amp.dim: # Input TimedArray for this function must be in Amperes
            raise TypeError(f"stimulus_waveform_density for '{cumulative_density_var}' must have "
                            f"values with current dimensions (amp), but has {stimulus_waveform_val_dim}.")
            
        if area_variable_name not in target_ng.variables:
            raise AttributeError(f"NeuronGroup '{target_group_name}' needs an '{area_variable_name}' variable (in m^2) "
                                 f"to convert stimulus current to current density for '{cumulative_density_var}'.")
        
        area_var_obj_dim = target_ng.variables[area_variable_name].dimensions
        if area_var_obj_dim != b2.meter.dim**2:
            raise TypeError(f"Variable '{area_variable_name}' in NeuronGroup '{target_group_name}' must have "
                            f"units of area (e.g., m^2), but has dimensions {area_var_obj_dim}.")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        if current_flag_name not in target_ng.variables: # pragma: no cover
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have the flag variable "
                f"'{current_flag_name}'. (Template: '{flag_variable_template}')"
            )

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            self.organoid, target_group_name, electrode_id, influence_radius
        )

        if len(target_neuron_indices_np) == 0: # pragma: no cover
            print(f"Warning: No neurons for density stimulus from E{electrode_id} in '{target_group_name}'.")
            return

        getattr(target_ng, current_flag_name)[:] = False
        getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True
        
        ta_name_in_ns = stimulus_waveform_density.name
        is_generic = ta_name_in_ns is None or ta_name_in_ns.startswith(('_timedarray', 'timedarray'))
        if is_generic or (ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is not stimulus_waveform_density):
            ta_name_in_ns = f'pyorg_stim_density_ta_e{electrode_id}_{self._stimulus_namespace_counter}'
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform_density
        
        reset_op_key = (target_group_name, cumulative_density_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_density_var}_{np.random.randint(10000)}'
            # Reset code should match the unit of the cumulative_density_var
            reset_code = f"{cumulative_density_var} = 0*amp/meter**2" # As target_var_dim is checked to be this
            
            op = target_ng.run_regularly(reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)

        # Stimulus is current (TimedArray), target is density, so divide by area
        stimulus_application_term = f"({ta_name_in_ns}(t) / {area_variable_name})"
        print(f"INFO: Stimulus for '{cumulative_density_var}' will be applied as current density using '{area_variable_name}'.")
        
        sum_code = f"{cumulative_density_var} = {cumulative_density_var} + ({current_flag_name} * {stimulus_application_term})"
        op_name = f'sum_stim_density_e{electrode_id}_to_{cumulative_density_var}_in_{target_group_name}_{np.random.randint(10000)}'
        
        try:
            op = target_ng.run_regularly(sum_code, dt=self.brian_dt, when='start', order=0, name=op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._stimulus_current_sources.append(stimulus_waveform_density)
            print(f"Summing current density stimulus op '{op_name}' added for E{electrode_id}.")
        except Exception as e: # pragma: no cover
            print(f"Error in add_current_density_stimulus for '{cumulative_density_var}': {e}")
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform_density:
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
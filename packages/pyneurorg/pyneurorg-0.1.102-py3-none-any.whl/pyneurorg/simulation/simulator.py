# src/pyneurorg/simulation/simulator.py

"""
Defines the Simulator class for orchestrating pyneurorg simulations.

The Simulator class takes an Organoid instance, allows adding monitors,
constructs a Brian2 Network, and runs the simulation. It can also interact
with an MEA for targeted stimulation, including current and current density stimuli.
"""

import brian2 as b2
import numpy as np
from ..organoid.organoid import Organoid
from ..mea.mea import MEA
from ..electrophysiology import brian_monitors as pbg_monitors
import traceback # For more detailed error printing if issues arise
from brian2.units.fundamentalunits import DIMENSIONLESS


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
            b2.defaultclock.dt = self.brian_dt 
        else:
            self.brian_dt = b2.defaultclock.dt 
        
        self._network_objects = list(self.organoid.brian2_objects) 
        self._stimulus_current_sources = [] 
        self._stimulus_namespace_counter = 0 
        self._cumulative_stim_vars_reset_added = set()
        self._applied_stimuli_configs = [] # MODIFICAÇÃO: Para logar configurações de estímulos

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
                     flag_variable_template: str = "stf{id}"):
        """
        Adds a stimulus (total current or dimensionless) to be applied via a specified MEA electrode to nearby neurons.
        """
        # ... (código existente do método como você forneceu) ...
        if self.mea is None: raise ValueError("No MEA set for this simulator.")
        if not isinstance(stimulus_waveform, b2.TimedArray): raise TypeError("stimulus_waveform must be a TimedArray.")

        target_ng = self.organoid.get_neuron_group(target_group_name)

        if cumulative_stim_var not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' must have variable '{cumulative_stim_var}'.")
        
        target_var_dim = target_ng.variables[cumulative_stim_var].dim
        
        if isinstance(stimulus_waveform.values, b2.Quantity):
            if stimulus_waveform.values.dim != target_var_dim:
                 raise TypeError(f"stimulus_waveform values have dimensions {stimulus_waveform.values.dim}, "
                                 f"but target variable '{cumulative_stim_var}' has dimensions {target_var_dim}.")
        elif target_var_dim != b2.amp.dim and target_var_dim != DIMENSIONLESS:
             print(f"Warning: stimulus_waveform.values are numerical. Target variable '{cumulative_stim_var}' has "
                   f"dimensions {target_var_dim}. Ensure TimedArray was created with matching units (e.g., values * unit).")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        if current_flag_name not in target_ng.variables:
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have flag variable '{current_flag_name}'.")

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
            
            if target_var_dim == b2.amp.dim:
                reset_code = f"{cumulative_stim_var} = 0*amp"
            elif target_var_dim == DIMENSIONLESS:
                reset_code = f"{cumulative_stim_var} = 0*1"
            else:
                 raise TypeError(f"Unsupported unit dimension for {cumulative_stim_var} in add_stimulus: {target_var_dim}.")
            
            op = target_ng.run_regularly(reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)

        sum_code = f"{cumulative_stim_var} = {cumulative_stim_var} + ({current_flag_name} * {ta_name_in_ns}(t))"
        op_name = f'sum_stim_e{electrode_id}_to_{cumulative_stim_var}_in_{target_group_name}_{np.random.randint(10000)}'
        
        try:
            op = target_ng.run_regularly(sum_code, dt=self.brian_dt, when='start', order=0, name=op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._stimulus_current_sources.append(stimulus_waveform)
            print(f"Summing stimulus op '{op_name}' added for E{electrode_id}.")

            # MODIFICAÇÃO: Logar a configuração do estímulo
            stim_config = {
                "mea_electrode_id": electrode_id,
                "target_group_name_pyneurorg": target_group_name,
                "stimulus_type": "current" if target_var_dim == b2.amp.dim else "dimensionless",
                "waveform_name": ta_name_in_ns, # ou stimulus_waveform.name se quiser o original
                "cumulative_var_name": cumulative_stim_var,
                "flag_template": flag_variable_template,
                "influence_radius": influence_radius, # Será serializado com unidade pelo writer
                "stimulus_params_json": {} # Placeholder para parâmetros do stimulus_generator
                                          # Idealmente, stimulus_waveform teria metadados ou seriam passados.
            }
            self._applied_stimuli_configs.append(stim_config)

        except Exception as e: 
            print(f"Error configuring summing run_regularly for '{cumulative_stim_var}': {e}")
            traceback.print_exc()
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform:
                del target_ng.namespace[ta_name_in_ns]
            raise

    def add_current_density_stimulus(self, electrode_id: int, stimulus_waveform_current: b2.TimedArray,
                                     target_group_name: str, influence_radius,
                                     cumulative_density_var: str = 'I_stimulus_sum',
                                     flag_variable_template: str = "stf{id}",
                                     area_variable_name: str = "area_val"):
        """
        Adds a stimulus that will be applied as a current density to targeted neurons.
        """
        # ... (código existente do método como você forneceu) ...
        if self.mea is None:
            raise ValueError("No MEA has been set for this simulator. Call set_mea() or provide at __init__.")
        if not isinstance(stimulus_waveform_current, b2.TimedArray):
            raise TypeError("stimulus_waveform_current must be a Brian2 TimedArray.")

        target_ng = self.organoid.get_neuron_group(target_group_name)

        if cumulative_density_var not in target_ng.variables:
            raise AttributeError(f"Target NeuronGroup '{target_group_name}' must have variable '{cumulative_density_var}'.")

        target_var_dim = target_ng.variables[cumulative_density_var].dim
        expected_density_dim = (b2.amp / b2.meter**2).dimensions 
        if target_var_dim != expected_density_dim:
            raise TypeError(f"Target variable '{cumulative_density_var}' in '{target_group_name}' "
                            f"must have current density dimensions {expected_density_dim}, but has {target_var_dim}.")

        if isinstance(stimulus_waveform_current.values, b2.Quantity):
            if stimulus_waveform_current.values.dim != b2.amp.dim:
                 raise TypeError(f"If stimulus_waveform_current.values is a Quantity, it must have current dimensions (amp), but has {stimulus_waveform_current.values.dim}.")
        
        if area_variable_name not in target_ng.variables:
            raise AttributeError(f"NeuronGroup '{target_group_name}' needs an '{area_variable_name}' variable (in m^2) "
                                 f"to convert stimulus current to current density for '{cumulative_density_var}'.")
        
        area_var_obj_dim = target_ng.variables[area_variable_name].dim 
        if area_var_obj_dim != b2.meter.dim**2: 
            raise TypeError(f"Variable '{area_variable_name}' in NeuronGroup '{target_group_name}' must have "
                            f"units of area (e.g., m^2), but has dimensions {area_var_obj_dim}.")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        if current_flag_name not in target_ng.variables: 
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have the flag variable "
                f"'{current_flag_name}'. (Template: '{flag_variable_template}')"
            )

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            self.organoid, target_group_name, electrode_id, influence_radius
        )

        if len(target_neuron_indices_np) == 0: 
            print(f"Warning: No neurons for density stimulus from E{electrode_id} in '{target_group_name}'.")
            return

        getattr(target_ng, current_flag_name)[:] = False
        getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True
        
        ta_name_in_ns = stimulus_waveform_current.name
        is_generic = ta_name_in_ns is None or ta_name_in_ns.startswith(('_timedarray', 'timedarray'))
        if is_generic or (ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is not stimulus_waveform_current):
            ta_name_in_ns = f'pyorg_stim_density_ta_e{electrode_id}_{self._stimulus_namespace_counter}'
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform_current
        
        reset_op_key = (target_group_name, cumulative_density_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_density_var}_{np.random.randint(10000)}'
            reset_code = f"{cumulative_density_var} = 0*amp/meter**2" 
            
            op = target_ng.run_regularly(reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)

        if area_variable_name not in target_ng.namespace and hasattr(target_ng, area_variable_name):
             if isinstance(getattr(target_ng, area_variable_name), b2.Quantity): 
                target_ng.namespace[area_variable_name] = getattr(target_ng, area_variable_name)

        stimulus_application_term = f"({ta_name_in_ns}(t) / {area_variable_name})"
        sum_code = f"{cumulative_density_var} = {cumulative_density_var} + ({current_flag_name} * {stimulus_application_term})"
        op_name = f'sum_stim_density_e{electrode_id}_to_{cumulative_density_var}_in_{target_group_name}_{np.random.randint(10000)}'
        
        try:
            op = target_ng.run_regularly(sum_code, dt=self.brian_dt, when='start', order=0, name=op_name)
            if op not in self._network_objects: self._network_objects.append(op)
            self._stimulus_current_sources.append(stimulus_waveform_current) 
            print(f"Summing current density stimulus op '{op_name}' added for E{electrode_id}.")

            # MODIFICAÇÃO: Logar a configuração do estímulo
            stim_config = {
                "mea_electrode_id": electrode_id,
                "target_group_name_pyneurorg": target_group_name,
                "stimulus_type": "current_density",
                "waveform_name": ta_name_in_ns,
                "cumulative_var_name": cumulative_density_var,
                "flag_template": flag_variable_template,
                "influence_radius": influence_radius,
                "area_variable_name": area_variable_name,
                "stimulus_params_json": {} # Placeholder
            }
            self._applied_stimuli_configs.append(stim_config)

        except Exception as e: 
            print(f"Error in add_current_density_stimulus for '{cumulative_density_var}': {e}")
            traceback.print_exc()
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform_current:
                del target_ng.namespace[ta_name_in_ns]
            raise

    def add_recording(self, monitor_name: str, monitor_type: str, target_group_name: str, **kwargs):
        # ... (código existente do método como você forneceu) ...
        if monitor_name in self.monitors:
            raise ValueError(f"Monitor with name '{monitor_name}' already exists.")
        
        target_object = None
        if target_group_name in self.organoid.neuron_groups:
            target_object = self.organoid.get_neuron_group(target_group_name)
        elif target_group_name in self.organoid.synapses: 
            target_object = self.organoid.get_synapses(target_group_name)
        else:
            raise KeyError(f"Target group/object '{target_group_name}' not found in organoid.")

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
        # ... (código existente do método como você forneceu) ...
        self.brian_network = b2.Network(self._network_objects, **network_kwargs)


    def run(self, duration: b2.Quantity, report=None, report_period=10*b2.second, **run_kwargs):
        # ... (código existente do método como você forneceu) ...
        if not isinstance(duration, b2.Quantity) or not (duration.dimensions == b2.second.dimensions):
            raise TypeError("duration must be a Brian2 Quantity with time units.")
        if self.brian_network is None:
            self.build_network(**run_kwargs.pop('network_kwargs', {}))
        if self.brian_network is None: 
            raise RuntimeError("Brian2 Network could not be built.")
        self.brian_network.run(duration, report=report, report_period=report_period, **run_kwargs)

    def get_data(self, monitor_name: str):
        # ... (código existente do método como você forneceu) ...
        if monitor_name not in self.monitors:
            raise KeyError(f"Monitor '{monitor_name}' not found. Available: {list(self.monitors.keys())}")
        return self.monitors[monitor_name]

    def store_simulation(self, filename="pyneurorg_sim_state", schedule_name=None):
        # ... (código existente do método como você forneceu) ...
        if self.brian_network is None:
            print("Warning: Network not built. Nothing to store.")
            return
        self.brian_network.store(name=filename, schedule=schedule_name)
        print(f"Simulation state stored with name '{filename}'.")

    def restore_simulation(self, filename="pyneurorg_sim_state", schedule_name=None):
        # ... (código existente do método como você forneceu) ...
        b2.restore(name=filename, schedule=schedule_name)
        self.brian_dt = b2.defaultclock.dt
        print(f"Simulation state restored from name '{filename}'.")
        self.brian_network = None 
        self._network_objects = [] 

    def __str__(self):
        # ... (código existente do método como você forneceu) ...
        status = "Built" if self.brian_network else "Not Built"
        num_monitors = len(self.monitors)
        return (f"<Simulator for Organoid '{self.organoid.name}' "
                f"with {num_monitors} monitor(s). Network Status: {status}>")

    def __repr__(self):
        return self.__str__()
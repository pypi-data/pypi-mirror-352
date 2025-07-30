# src/pyneurorg/organoid/organoid.py

import brian2 as b2
import numpy as np
from ..core import neuron_models as pbg_neuron_models
from ..core import synapse_models as pbg_synapse_models
from . import spatial as pbg_spatial
from brian2.units.fundamentalunits import DIMENSIONLESS # Para inicializações adimensionais

class Organoid:
    def __init__(self, name="pyneurorg_organoid", default_brian2_prefs=None):
        self.name = name
        self.neuron_groups = {}
        self.synapses = {}
        self.positions = {} 
        self.brian2_objects = []
        if default_brian2_prefs:
            for key, value in default_brian2_prefs.items():
                b2.prefs[key] = value
        # self._neuron_id_counter = 0 # Não usado atualmente

    def add_neurons(self, name, num_neurons, model_name, model_params=None,
                    positions=None, spatial_distribution_func=None, spatial_params=None,
                    initial_values=None, **kwargs):
        if name in self.neuron_groups:
            raise ValueError(f"Neuron group with name '{name}' already exists.")
        
        original_model_params = model_params.copy() if model_params is not None else {}
        original_spatial_params = spatial_params.copy() if spatial_params is not None else {}
        current_model_params_for_func = model_params.copy() if model_params is not None else {}

        try:
            model_func = getattr(pbg_neuron_models, model_name)
        except AttributeError:
            if model_name in globals() and callable(globals()[model_name]):
                model_func = globals()[model_name]
            elif hasattr(pbg_neuron_models, model_name) and callable(getattr(pbg_neuron_models, model_name)):
                 model_func = getattr(pbg_neuron_models, model_name) 
            else:
                raise ValueError(f"Neuron model function '{model_name}' not found in pyneurorg.core.neuron_models or globals.")
        
        model_def = model_func(**current_model_params_for_func)

        neuron_positions_um_qty = None
        if positions is not None:
            if isinstance(positions, b2.Quantity):
                if positions.dimensions == b2.metre.dimensions:
                    neuron_positions_um_qty = (positions / b2.um) * b2.um
                else:
                    raise TypeError("Provided 'positions' Quantity must have length dimensions.")
            elif isinstance(positions, (np.ndarray, list, tuple)):
                try:
                    positions_arr = np.asarray(positions, dtype=float)
                    if positions_arr.ndim == 1 and positions_arr.shape[0] == 3 and num_neurons == 1:
                        positions_arr = positions_arr.reshape(1,3)
                    elif positions_arr.ndim != 2 or positions_arr.shape[1] != 3:
                        raise ValueError("If 'positions' is array/list, it must be N x 3 or 1x3 for single neuron.")
                    neuron_positions_um_qty = positions_arr * b2.um
                except Exception as e:
                    raise TypeError(f"Could not interpret 'positions' as coordinate array (assumed um): {e}")
            else:
                raise TypeError("Provided 'positions' must be a Brian2 Quantity, or array-like (assumed um).")
            if neuron_positions_um_qty.shape[0] != num_neurons:
                 raise ValueError(f"Positions shape mismatch: {neuron_positions_um_qty.shape[0]} vs {num_neurons}.")
        elif spatial_distribution_func is not None:
            current_spatial_params_for_func = spatial_params.copy() if spatial_params is not None else {}
            current_spatial_params_for_func['N'] = num_neurons
            try:
                spatial_func = getattr(pbg_spatial, spatial_distribution_func)
            except AttributeError:
                raise ValueError(f"Spatial function '{spatial_distribution_func}' not found in pyneurorg.organoid.spatial.")
            neuron_positions_um_qty = spatial_func(**current_spatial_params_for_func)
            if not (isinstance(neuron_positions_um_qty, b2.Quantity) and neuron_positions_um_qty.dimensions == b2.metre.dimensions):
                 raise TypeError(f"Spatial function '{spatial_distribution_func}' must return Quantity with length.")
            if neuron_positions_um_qty.shape != (num_neurons, 3):
                raise ValueError(f"Spatial function '{spatial_distribution_func}' returned incorrect shape ({neuron_positions_um_qty.shape} vs {(num_neurons, 3)}).")
        else:
            print(f"Warning: No 'positions' or 'spatial_distribution_func' for NeuronGroup '{name}'. Defaulting to (0,0,0) for all {num_neurons} neurons.")
            neuron_positions_um_qty = np.zeros((num_neurons, 3)) * b2.um

        final_initial_values = {}
        model_namespace_defaults = model_def.get('namespace', {})
        for key, val in model_namespace_defaults.items():
            if key.endswith('_default_init'):
                var_name = key[:-len('_default_init')]
                final_initial_values[var_name] = val
        
        model_eqs_str = model_def.get('model', '')
        common_vars_unit_str = "amp" 
        if "I_stimulus_sum : amp/meter**2" in model_eqs_str:
            common_vars_unit_str = "amp/meter**2"
        elif "I_stimulus_sum : 1" in model_eqs_str:
            common_vars_unit_str = "1"

        default_common_var_unit_obj = b2.amp
        if common_vars_unit_str == "amp/meter**2": default_common_var_unit_obj = b2.amp/b2.meter**2
        elif common_vars_unit_str == "1": default_common_var_unit_obj = b2.Quantity(1, dim=DIMENSIONLESS)

        for current_var_to_init in ['I_stimulus_sum', 'I_synaptic']:
            if current_var_to_init in model_eqs_str and current_var_to_init not in final_initial_values:
                final_initial_values[current_var_to_init] = 0 * default_common_var_unit_obj
        
        num_flags = current_model_params_for_func.get('num_stim_flags', 16)
        for i in range(num_flags):
            flag_name = f"stf{i}"
            if flag_name in model_eqs_str and flag_name not in final_initial_values:
                 final_initial_values[flag_name] = False
        
        if 'x : metre' in model_eqs_str and 'x' not in final_initial_values:
            final_initial_values['x'] = neuron_positions_um_qty[:, 0]
        if 'y : metre' in model_eqs_str and 'y' not in final_initial_values:
            final_initial_values['y'] = neuron_positions_um_qty[:, 1]
        if 'z : metre' in model_eqs_str and 'z' not in final_initial_values:
            final_initial_values['z'] = neuron_positions_um_qty[:, 2]

        if initial_values: 
            final_initial_values.update(initial_values)

        ng = b2.NeuronGroup(
            N=num_neurons, model=model_def['model'],
            threshold=model_def.get('threshold'), reset=model_def.get('reset'),
            refractory=model_def.get('refractory', False),
            method=kwargs.pop('method', model_def.get('method', 'auto')),
            namespace=model_namespace_defaults, name=name, **kwargs
        )

        for var_name_init, value_init in final_initial_values.items():
            if hasattr(ng, var_name_init):
                try: 
                    setattr(ng, var_name_init, value_init)
                except Exception as e_init: 
                    print(f"Warning: Could not set initial value for '{var_name_init}' in NeuronGroup '{name}': {e_init}")
        
        ng._pyneurorg_model_name = model_name
        ng._pyneurorg_model_params = original_model_params
        ng._pyneurorg_spatial_func = spatial_distribution_func
        ng._pyneurorg_spatial_params = original_spatial_params
        
        self.neuron_groups[name] = ng
        self.positions[name] = neuron_positions_um_qty 
        self.brian2_objects.append(ng)
        return ng

    def add_synapses(self, name, pre_group_name, post_group_name,
                     model_name, model_params=None,
                     connect_condition=None, connect_prob=None, connect_n=None,
                     on_pre_params=None, on_post_params=None,
                     synaptic_params=None, **kwargs):
        if name in self.synapses:
            raise ValueError(f"Synapse group with name '{name}' already exists.")
        if pre_group_name not in self.neuron_groups:
            raise ValueError(f"Presynaptic neuron group '{pre_group_name}' not found.")
        if post_group_name not in self.neuron_groups:
            raise ValueError(f"Postsynaptic neuron group '{post_group_name}' not found.")

        original_model_params = model_params.copy() if model_params is not None else {}
        current_model_params_for_func = model_params.copy() if model_params is not None else {}
        
        pre_ng = self.neuron_groups[pre_group_name]
        post_ng = self.neuron_groups[post_group_name]

        try:
            model_func = getattr(pbg_synapse_models, model_name)
        except AttributeError:
            raise ValueError(f"Synapse model function '{model_name}' not found in pyneurorg.core.synapse_models.")

        model_def = model_func(**current_model_params_for_func)

        final_namespace = model_def.get('namespace', {}).copy()
        user_namespace_from_kwargs = kwargs.pop('namespace', None) 
        if user_namespace_from_kwargs:
            final_namespace.update(user_namespace_from_kwargs)

        syn = b2.Synapses(
            source=pre_ng,
            target=post_ng,
            model=model_def['model'],
            on_pre=model_def.get('on_pre'),
            on_post=model_def.get('on_post'), 
            namespace=final_namespace,
            method=kwargs.pop('method', model_def.get('method', 'auto')),
            name=name, 
            **kwargs
        )

        connect_rule_description_str = "N/A"
        if connect_condition is not None: 
            syn.connect(condition=connect_condition)
            connect_rule_description_str = f"condition: {connect_condition}"
        elif connect_prob is not None: 
            syn.connect(p=connect_prob)
            connect_rule_description_str = f"probability: {connect_prob}"
        elif connect_n is not None: 
            syn.connect(n=connect_n)
            connect_rule_description_str = f"n (outgoing per pre): {connect_n}"
        else:
            if len(pre_ng) * len(post_ng) > 0 : 
                 if len(pre_ng) * len(post_ng) < 100000 or \
                    (len(pre_ng) == 1 and len(post_ng) == 1): 
                     syn.connect() 
                     connect_rule_description_str = "all-to-all (default or small N)"
                 else: 
                     print(f"Warning: No connection rule for synapses '{name}' and N_pre*N_post >= 100k. Skipping default all-to-all.")
                     connect_rule_description_str = "None (skipped default all-to-all)"
        
        if synaptic_params:
            for param_name, value in synaptic_params.items():
                if hasattr(syn, param_name):
                    try:
                        setattr(syn, param_name, value)
                    except Exception as e_syn_param:
                        print(f"Warning: Could not set synaptic_param '{param_name}' for '{name}': {e_syn_param}")
                else:
                    print(f"Warning: Synaptic parameter '{param_name}' not found on Synapses object '{name}'.")
        
        if on_pre_params:
             for param_name, value in on_pre_params.items():
                 if param_name == 'delay': 
                     syn.delay = value
        
        # Store pyneurorg metadata for logging <<< MOVIDO PARA DENTRO DO MÉTODO
        syn._pyneurorg_model_name = model_name
        syn._pyneurorg_model_params = original_model_params
        syn._pyneurorg_connect_rule = connect_rule_description_str
        
        self.synapses[name] = syn
        self.brian2_objects.append(syn)
        return syn

    def get_neuron_group(self, name):
        if name not in self.neuron_groups:
            raise KeyError(f"Neuron group '{name}' not found.")
        return self.neuron_groups[name]

    def get_synapses(self, name):
        if name not in self.synapses:
            raise KeyError(f"Synapses group '{name}' not found.")
        return self.synapses[name]

    def get_positions(self, neuron_group_name):
        if neuron_group_name not in self.positions:
            raise KeyError(f"Positions for neuron group '{neuron_group_name}' not found.")
        return self.positions[neuron_group_name]

    def __str__(self):
        return (f"<Organoid '{self.name}' with {len(self.neuron_groups)} neuron group(s) "
                f"and {len(self.synapses)} synapse group(s)>")

    def __repr__(self):
        return self.__str__()
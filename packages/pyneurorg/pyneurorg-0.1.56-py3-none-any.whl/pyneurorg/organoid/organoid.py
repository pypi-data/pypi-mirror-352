# src/pyneurorg/organoid/organoid.py

import brian2 as b2
import numpy as np
from ..core import neuron_models as pbg_neuron_models
from ..core import synapse_models as pbg_synapse_models
from . import spatial as pbg_spatial
# from .spatial import _ensure_um_quantity # If needed directly

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
        self._neuron_id_counter = 0

    def add_neurons(self, name, num_neurons, model_name, model_params=None,
                    positions=None, spatial_distribution_func=None, spatial_params=None,
                    initial_values=None, **kwargs):
        if name in self.neuron_groups:
            raise ValueError(f"Neuron group with name '{name}' already exists.")
        
        current_model_params = model_params.copy() if model_params is not None else {}

        try:
            model_func = getattr(pbg_neuron_models, model_name)
        except AttributeError:
            raise ValueError(f"Neuron model function '{model_name}' not found in pyneurorg.core.neuron_models.")
        
        model_def = model_func(**current_model_params)

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
            current_spatial_params = spatial_params.copy() if spatial_params is not None else {}
            current_spatial_params['N'] = num_neurons
            try:
                spatial_func = getattr(pbg_spatial, spatial_distribution_func)
            except AttributeError:
                raise ValueError(f"Spatial function '{spatial_distribution_func}' not found.")
            neuron_positions_um_qty = spatial_func(**current_spatial_params)
            if not (isinstance(neuron_positions_um_qty, b2.Quantity) and neuron_positions_um_qty.dimensions == b2.metre.dimensions):
                 raise TypeError(f"Spatial function '{spatial_distribution_func}' must return Quantity with length.")
            if neuron_positions_um_qty.shape != (num_neurons, 3):
                raise ValueError(f"Spatial function '{spatial_distribution_func}' returned incorrect shape.")
        else:
            raise ValueError("Either 'positions' or 'spatial_distribution_func' must be provided.")

        final_initial_values = {}
        model_namespace_defaults = model_def.get('namespace', {})
        for key, val in model_namespace_defaults.items():
            if key.endswith('_default_init'):
                var_name = key[:-len('_default_init')]
                final_initial_values[var_name] = val
        
        model_eqs_str = model_def.get('model', '')
        # Ensure key currents are initialized if not covered by model defaults
        for current_var_to_init in ['I_stimulus_sum', 'I_synaptic']:
            if current_var_to_init in model_eqs_str and current_var_to_init not in final_initial_values:
                # Determine unit from model_eqs_str (e.g. amp or amp/meter**2 for HH)
                unit_for_current = b2.amp # Default
                if "amp/meter**2" in model_eqs_str and current_var_to_init in model_eqs_str: # Crude check for HH
                    unit_for_current = b2.amp/b2.meter**2
                final_initial_values[current_var_to_init] = 0 * unit_for_current
        
        if initial_values:
            final_initial_values.update(initial_values)

        ng = b2.NeuronGroup(
            N=num_neurons, model=model_def['model'],
            threshold=model_def.get('threshold'), reset=model_def.get('reset'),
            refractory=model_def.get('refractory', False),
            method=kwargs.pop('method', model_def.get('method', 'auto')),
            namespace=model_namespace_defaults, name=name, **kwargs
        )

        for var_name, value in final_initial_values.items():
            if hasattr(ng, var_name):
                try: setattr(ng, var_name, value)
                except Exception as e: print(f"Warning: Could not set initial value for '{var_name}': {e}")
        
        self.neuron_groups[name] = ng
        self.positions[name] = neuron_positions_um_qty
        self.brian2_objects.append(ng)
        return ng

    # ... (add_synapses e outros getters como na versão anterior completa) ...
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

        current_model_params = model_params.copy() if model_params is not None else {}
        current_on_pre_params = on_pre_params.copy() if on_pre_params is not None else {}
        # current_on_post_params = on_post_params.copy() if on_post_params is not None else {} # Not used below
        current_synaptic_params = synaptic_params.copy() if synaptic_params is not None else {}


        pre_ng = self.neuron_groups[pre_group_name]
        post_ng = self.neuron_groups[post_group_name]

        try:
            model_func = getattr(pbg_synapse_models, model_name)
        except AttributeError:
            raise ValueError(f"Synapse model function '{model_name}' not found in pyneurorg.core.synapse_models.")

        model_def = model_func(**current_model_params)

        syn = b2.Synapses(
            source=pre_ng,
            target=post_ng,
            model=model_def['model'],
            on_pre=model_def.get('on_pre'),
            on_post=model_def.get('on_post'), # Keep if synapse models use it
            namespace=model_def.get('namespace', {}),
            method=kwargs.pop('method', model_def.get('method', 'auto')),
            name=name, 
            **kwargs
        )

        if connect_condition is not None: syn.connect(condition=connect_condition)
        elif connect_prob is not None: syn.connect(p=connect_prob)
        elif connect_n is not None: syn.connect(n=connect_n)
        else:
            if len(pre_ng) * len(post_ng) > 0 : 
                 if len(pre_ng) * len(post_ng) < 100000: 
                     syn.connect() 
                 else: # Only print warning if not connecting due to size
                     print(f"Warning: No connection rule for synapses '{name}' and N_pre*N_post >= 100k. Skipping default all-to-all.")
        
        for param_name, value in current_synaptic_params.items():
            if hasattr(syn, param_name):
                setattr(syn, param_name, value)
            else:
                print(f"Warning: Synaptic parameter '{param_name}' not found in model for synapses '{name}'.")
        
        for param_name, value in current_on_pre_params.items():
             if param_name == 'delay': 
                 syn.delay = value
        
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
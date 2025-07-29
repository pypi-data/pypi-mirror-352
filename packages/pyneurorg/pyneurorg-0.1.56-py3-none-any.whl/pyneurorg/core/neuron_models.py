# src/pyneurorg/core/neuron_models.py

"""
Collection of predefined neuron models for use with Brian2 in pyneurorg simulations.

All models include common variables for synaptic input ('I_synaptic'),
summed external stimulus input ('I_stimulus_sum'), and a tonic base current ('I_tonic_val').
They also include boolean flags 'stfX : boolean' (where X is an ID from 0 
to num_stim_flags-1) for targeted stimulation.
"""

import brian2 as b2
# from brian2.units.fundamentalunits import DIMENSIONLESS # Only if checking phase units etc.


def _add_common_stim_syn_vars_and_flags(base_eqs_str: str, 
                                        base_namespace_dict: dict, 
                                        num_stim_flags: int = 16,
                                        current_vars_units: str = "amp"):
    current_declarations = [
        f"I_synaptic : {current_vars_units} # Sum of synaptic currents",
        f"I_stimulus_sum : {current_vars_units} # Sum of external timed stimuli"
    ]
    
    flag_eqs_list = []
    default_flags_init_ns = {}
    for i in range(num_stim_flags):
        flag_name = f"stf{i}" 
        flag_eqs_list.append(f"{flag_name} : boolean") # Esta linha está correta
        default_flags_init_ns[f"{flag_name}_default_init"] = False 

    full_eqs_str_parts = []
    full_eqs_str_parts.extend(current_declarations) 
    full_eqs_str_parts.append(base_eqs_str)         
    if flag_eqs_list:
        full_eqs_str_parts.extend(flag_eqs_list)    
    
    full_eqs_str = "\n".join(filter(None, full_eqs_str_parts)) # filter(None,...) remove strings vazias se houver
                                                              # antes de juntar com newline.
    
    updated_namespace = base_namespace_dict.copy()
    default_current_unit_obj = b2.amp
    if current_vars_units == "amp/meter**2":
        default_current_unit_obj = b2.amp / b2.meter**2
    
    updated_namespace.setdefault('I_synaptic_default_init', 0 * default_current_unit_obj)
    updated_namespace.setdefault('I_stimulus_sum_default_init', 0 * default_current_unit_obj)
    updated_namespace.update(default_flags_init_ns)
    
    return full_eqs_str, updated_namespace

"""
Collection of predefined neuron models for use with Brian2 in pyneurorg simulations.

All models include common variables for synaptic input ('I_synaptic'),
summed external stimulus input ('I_stimulus_sum'), and as_list.append(f"{flag_name} : boolean")
        default_flags_init_ns[f"{flag_name}_default_init"] = False 

    # Combine all equation parts:
    # Start with current declarations, then base model equations, then flags.
    full_eqs_str_parts = []
    full_eqs_str tonic base current ('I_tonic_val').
They also include boolean flags 'stfX : boolean' (where X is an ID from 0 
to num_stim_flags-1) for targeted stimulation.
"""

import brian2 as b2
# from brian2.units.fundamentalunits import DIMENSIONLESS #_parts.extend(current_declarations) # Add I_synaptic, I_stimulus_sum declarations
    full_eqs_str_parts.append(base_eqs_str)         # Add the core model dynamics
    if flag_eqs_list:
        full_eqs_str_parts.extend(flag_eqs_list)    # Add boolean flags
    
    full_eqs_str = "\n".join(filter(None, full Only if checking phase units etc.

def _add_common_stim_syn_vars_and_flags(base_eqs_str: str, 
                                        base_namespace_dict: dict, 
                                        num_stim_flags: int = 16,
                                        current_vars_units: str = "amp"):
    """
    Appends common current variables (I_synaptic, I_stimulus_sum) and
    boolean stimulus flags (stf0, stf1, ...) to model equations and namespace.
    Ensures I_eqs_str_parts)) # Join non-empty parts, filter ensures no empty lines from None
    
    # Update namespace with defaults for these common variables
    updated_namespace = base_namespace_dict.copy()
    
    default_current_unit_obj = b2.amp
    if current_vars_units == "amp/meter**2": # For HH model
        default_current_synaptic and I_stimulus_sum are declared.

    Parameters
    ----------
    base_eqs_str : str
        The base model equations string. This string should already utilize
        I_synaptic and I_stimulus_sum where appropriate (e.g., in a summed current term).
    base_namespace_dict : dict
        _unit_obj = b2.amp / b2.meter**2
    
    # Add default initializers (will be used by Organoid.add_neurons if not overridden by user)
    # setdefault only adds if keyThe base model namespace dictionary.
    num_stim_flags : int, optional
        Number of boolean stimulus target flags to create (stf0, stf1, ...).
        Default is 16.
    current_vars_units : str, optional
        The string representing the units for I_synaptic and I_stimulus_sum
        (e is not already present from base_namespace_dict
    updated_namespace.setdefault('I_synaptic_default_init', 0 * default_current_unit_obj)
    updated_namespace.setdefault('I_stimulus_sum_default_init', 0 * default_current_unit_obj)
    updated_namespace.update(default_flags_init_ns) # Adds.g., "amp" or "amp/meter**2" for current densities). Default is "amp".

    Returns
    -------
    tuple
        (full_equations_string, updated_namespace_dictionary)
    """
    # These current variables will be part of the neuron's state.
    # They are declared here to ensure they exist/overwrites stfX_default_init = False
    
    return full_eqs_str, updated_namespace


def LIFNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
              v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
              refractory_period=2*b2.ms, num in the final model string.
    current_declarations = [
        f"I_synaptic : {current_vars_units} # Sum of synaptic currents",
        f"I_stimulus_sum : {current_vars_units} # Sum of external timed stimuli"
    ]
    
    flag_eqs_list = []
    default_flags_init_ns = {}
    for i in range(num_stim_flags):
        flag_name = f"stf{i}" # Stimulus Target Flag
        flag_eqs_list.append(_stim_flags=16):
    """Leaky Integrate-and-Fire (LIF) neuron model with stimulus capabilities."""
    base_eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    """
    base_namespace = {
        'tau_m_val': tau_m, 
        'v_rest_val': v_rest, 
        'R_m_val': R_m,
        'I_tonic_val': I_tonic, 
        f"{flag_name} : boolean")
        default_flags_init_ns[f"{flag_name}_default_init"] = False 

    # Combine all equation parts:
    # Start with current declarations, then base model equations, then flags.
    full_eqs_str_parts = []
    full_eqs_str_parts.extend(current_declarations) 
    full_eqs_str_parts.append(base_eqs_str)         
    if flag_eqs_list:
        full_eqs_str_parts.extend(flag_eqs_list)    
    
    full_eqs_str = "\n".join(filter(None, full_eqs_str_parts)) 
    
    # Update namespace withv_default_init': v_rest, 
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v > {v_thresh!r}', 
        'reset': f'v = {v_reset!r}',
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'exact'
    }


def IzhikevichNeuron(a=0.02/b2.ms, b=0.2*b2.nS, c=-65*b2.mV, d=2*b2.pA,
                     v_init=-70*b2.mV, u_init=None, C_m=100*b2.pF,
                     k=0.7*b2.nS/b2.mV, v_rest_iz=-60*b2.mV, v_thresh_iz=-40*b2.mV,
                     v_peak=30*b2.mV, I_tonic=0*b2.pA, num_stim_flags=16):
    """Izhikevich neuron model with stimulus capabilities."""
    if u_init is None: 
        # b is conductance (S), (v-vr) is voltage (V), so b*(v-vr) is current (A)
        u_init_val = b * (v_init - v_rest_iz) 
    else: 
        u_init_val = u_init # User provides u_init, must be current

    base_eqs = """
    dv/dt = (k_val * (v - v_rest_iz_val) * (v - v_thresh_iz_val) - u + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt
    du/dt = a_val * (b_val * (v - v_rest_iz_val) - u) : amp / second 
    u : amp  # Explicitly declare 'u' as having current units
    """ 
    

    base_namespace = {
        'a_val': a,           # units: 1/second
        'b_val': b,           # units: siemens (conductance)
        'k_val': k,           # units: siemens/volt or amp/volt^2
        'C_m_val': C_m,         # units: farad
        'v_rest_iz_val': v_rest_iz,
        'v_thresh_iz_val': v_thresh_iz,
        'I_tonic_val': I_tonic, # units: amp
        'v_default_init': v_init,
        'u_default_init': u_init_val, # This is a current (amp)
        # c (volt) and d (amp) are used in reset string
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v >= {v_peak!r}', 
        # d must be a Quantity with current units (e.g., pA)
        'reset': f'v = {c!r}; u += {d!r}', 
        'namespace': full_namespace, 
        'method': 'euler'
    }



def AdExNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
               V_T=-50.4*b2.mV, Delta_T=2*b2.mV, tau_w=144*b2.ms,
               a=4*b2.nS, adex_b_param=0.0805*b2.nA, V_reset=-70.6*b2.mV,
               V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=0*b2.ms,
               num_stim_flags=16):
    """Adaptive Exponential I&F (AdEx) neuron model with stimulus capabilities."""
    base_eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V_T_val)/Delta0*b2.mV, v_thresh_iz=-40*b2.mV,
                     v_peak=30*b2.mV, I_tonic=0*b2.pA, num_stim_flags=16):
    """Izhikevich neuron model with stimulus capabilities."""
    if u_init is None: u_init_val = b * (v_init - v_rest_iz)
    else: u_init_val = u_init
    base_eqs = """
    dv/dt = (k_val * (v - v_rest_iz_val) * (v - v_thresh_iz_val) - u + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt
    du/dt = a_val * (b_val * (v - v_rest_iz_val) - u) : amp / second 
    """ 
    base_namespace = {
        'a_val': a, 'b_val': b, 'k_val': k, 'C_m_val': C_m, 'v_rest_iz_val': v_rest_iz,
        'v_thresh_iz_val': v_thresh_iz, 'I_tonic_val':_T_val) - w + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    dw/dt = (a_val * (v - E_L_val) - w) / tau_w_val : amp (unless refractory)
    """
    base_namespace = {
        'C_m_val': C_m, 'g_L_val': g_L, 'E_L_val': E_L, 'V_T_val': V_T, 'Delta_T_val': Delta_T,
        'tau_w_val': tau_w, 'a_val': a, 'I_tonic_val': I_tonic,
        'v_default_init': E_L, 'w_default_init': 0*b2.nA,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v > {V_peak!r}', 
        'reset': f'v = {V_reset!r}; w += {adex_b_param!r}',
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'euler'
     I_tonic,
        'v_default_init': v_init, 'u_default_init': u_init_val,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v >= {v_peak!r}', 
        'reset': f'v = {c!r}; u += {d!r}', 
        'namespace': full_namespace, 
        'method': 'euler'
    }


def AdExNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
               V_T=-50.4*b2.mV, Delta_T=2*b2.mV, tau_w=144*b2.ms,
               a=4*b2.nS, adex_b_param=0.0805*b2.nA, V_reset=-70.6*b2.mV,
               V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=0*b2.ms,
               num_stim_flags=16):
    """Adaptive Exponential I&F (AdEx) neuron model with stimulus capabilities."""
    base_eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V}


def QIFNeuron(tau_m=20*b2.ms, v_rest=0*b2.mV, v_c=10*b2.mV, 
              v_reset=-10*b2.mV, v_peak=30*b2.mV, R_m=100*b2.Mohm,
              I_tonic=0*b2.nA, refractory_period=1*b2.ms, num_stim_flags=16):
    """Quadratic Integrate-and-Fire (QIF) neuron model with stimulus capabilities."""
    base_eqs = """
    dv/dt = ( (v - v_rest_val) * (v - v_critical_val) / (1*volt) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val) ) / tau_m_val : volt (unless refractory)
    """
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'v_critical_val': v_c,
        'R_m_val': R_m, 'I_tonic_val': I_tonic, 
        'v_default_init': v_rest,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v >= {v_peak!r}', 
        'reset': f'v = {v_reset!r}',
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'euler'
    }


_T_val)/Delta_T_val) - w + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    dw/dt = (a_val * (v - E_L_val) - w) / tau_w_val : amp (unless refractory)
    """ 
    base_namespace = {
        'C_m_val': C_m, 'g_L_val': g_L, 'E_L_val': E_L, 'V_T_val': V_T, 'Delta_T_val': Delta_T,
        'tau_w_val': tau_w, 'a_val': a, 'I_tonic_val': I_tonic,
        'v_default_init': E_L, 'w_default_init': 0*b2.nA,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_varsdef SimpleHHNeuron(C_m=1*b2.uF/b2.cm**2, E_Na=50*b2.mV, E_K=-77*b2.mV, E_L=-54.4*b2.mV,
                   g_Na_bar=120*b2.mS/b2.cm**2, g_K_bar=36*b2.mS/b2.cm**2, g_L_bar=0.3*b2.mS/b2.cm**2,
                   V_T_hh=-60*b2.mV, I_tonic=0*b2.uA/b2.cm**2, refractory_period=0*b2.ms,
                   num_stim_flags=16):
    """Simplified Hodgkin-Huxley (HH) neuron model with stimulus capabilities.
    Currents (I_synaptic, I_stimulus_sum, I_tonic_val) are current densities (A/m^2)."""
    numerical_spike_threshold = 0*b2.mV
    base_eqs = """
    dv/dt = (I_Na + I_K + I_L + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    I_Na = g_Na_bar_val * m**3 * h * (E_Na_val - v) : amp/meter**2
    dm/dt = alpha_m * (1-m) - beta_m * m : 1
    dh/dt = alpha_h * (1-h) - beta_h * h : _units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v > {V_peak!r}', 
        'reset': f'v = {V_reset!r}; w += {adex_b_param!r}',
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'euler'
    }


def QIFNeuron(tau_m=20*b2.ms, v_rest=0*b2.mV, v_c=10*b2.mV, 
              v_reset=-10*b2.mV, v_peak=30*b2.mV, R_m=100*b2.Mohm,
              I_tonic=0*b2.nA, refractory_period=1*b2.ms, num_stim_flags=16):
    """Quadratic Integrate-and-Fire (QIF) neuron model with stimulus capabilities."""
    base_eqs = """
    dv/dt = ( (v - v_rest_val) * (v - v_critical_val) / (1*volt) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val) ) / tau_m_val : volt (unless refractory)
    """
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'v_critical_val': v_c,
        'R_m_val': R_m, 'I_tonic_val': I_tonic, 
        'v_default_init': v_rest,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 
        'threshold': f'v >= {v_peak!r}', 
        'reset': f'v = {v_reset!r}',
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'euler'
    }


def SimpleHHNeuron(C_m=1*b2.uF/b2.cm**2, E_Na=50*b2.mV, E_K=-77*b2.mV, E_L=-54.4*1
    alpha_m = (0.1/mV) * (v - (V_T_hh_val + 25*mV)) / (1 - exp(-(v - (V_T_hh_val + 25*mV))/(10*mV))) / ms : Hz
    beta_m = (4.0) * exp(-(v - (V_T_hh_val + 0*mV))/(18*mV)) / ms : Hz
    alpha_h = (0.07) * exp(-(v - (V_T_hh_val + 0*mV))/(20*mV)) / ms : Hz
    beta_h = (1.0) / (1 + exp(-(v - (V_T_hh_val + 30*mV))/(10*mV))) / ms : Hz
    I_K = g_K_bar_val * n**4 * (E_K_val - v) : amp/meter**2
    dn/dt = alpha_n * (1-n) - beta_n * n : 1
b2.mV,
                   g_Na_bar=120*b2.mS/b2.cm**2, g_K_bar=36*b2.mS/b2.cm**2, g_L_bar=0.3*b2.mS/b2.cm**2,
                   V_T_hh=-60*b2.mV, I_tonic=0*b2.uA/b2.cm**2, refractory_period=0*b2.ms,
                   num_stim_flags=16):
    """Simplified Hodgkin-Huxley (HH) neuron model with stimulus capabilities.
    Currents (I_synaptic, I_stimulus_sum, I_tonic_val) are current densities (A/m^2)."""
    numerical_spike_threshold = 0*b2.mV
    base_eqs = """
    dv/dt = (I_Na + I_K + I_L + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    I_Na = g_Na_bar_val * m**3 * h * (E_Na_val - v) : amp/meter**2
    dm/dt = alpha_m * (1-m) - beta_m * m : 1
    dh/dt = alpha_h * (1-h) - beta_h * h : 1
    alpha_m = (0.1/mV) * (v - (V_T_hh_val + 25*mV)) / (1 - exp(-(v - (V_T_hh_val + 25*mV))/(10*mV))) / ms : Hz
    beta_m = (4.0) * exp(-(v - (V_T_hh_val + 0*mV))/(18*mV)) / ms : Hz
    alpha_h = (0.07) * exp(-(v - (V_T_hh_val + 0*mV))/(20*mV)) / ms : Hz
    beta_h = (1.0) / (1 + exp(-(v - (V_T_hh_val + 30*mV))/(10*mV))) / ms : Hz
    I_K = g_K_bar_val * n**4 * (E_K_val - v) : amp/meter**2
    dn/dt = alpha_n * (1-n) - beta_n * n : 1
    alpha_n = (0.01/mV) * (v - (V_T_hh_val + 10*mV)) / (1 - exp(-(v - (V_T_hh_val + 10*mV))/(10*mV))) / ms : Hz
    beta_n = (0.125) * exp(-(v - (V_T_hh_val + 0*mV))/(80*mV)) / ms : Hz
    I    alpha_n = (0.01/mV) * (v - (V_T_hh_val + 10*mV)) / (1 - exp(-(v - (V_T_hh_val + 10*mV))/(10*mV))) / ms : Hz
    beta_n = (0.125) * exp(-(v - (V_T_hh_val + 0*mV))/(80*mV)) / ms : Hz
    I_L = g_L_bar_val * (E_L_val - v) : amp/meter**2
    """
    base_namespace = {
        'C_m_val': C_m, 'E_Na_val': E_Na, 'E_K_val': E_K, 'E_L_val': E_L,
        'g_Na_bar_val': g_Na_bar, 'g_K_bar_val': g_K_bar, 'g_L_bar_val': g_L_bar,
        'V_T_hh_val': V_T_hh, 'I_tonic_val': I_tonic, # I_tonic is current density
        'v_default_init': E_L, 'm_default_init': 0.05, 
        'h_default_init': 0.6, 'n_default_init': 0.32,
    }
    
    current_density_units_str = "amp/meter**2"
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags,
        current_vars_units=current_density_units_str
    )
    
    # Ensure default initializers for currents added by helper also use density units for HH
    # This is now handled by passing current_vars_units to the helper and using setdefault.
    # The helper already correctly determines the unit object for 0 * unit.

    return {
        'model': full_eqs, 
        'threshold': f'v > {numerical_spike_threshold!r}', 
        'reset': '', 
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'exponential_euler' 
    }

# Example of a neuron model that might use calcium dynamics (conceptual)
def LIFCalciumFluorNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
                          v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
                          refractory_period=2*b2.ms, 
                          tau_ca=50*b2.ms, ca_spike_increment=0.2, # Example Ca params (unitless increment here)
                          tau_f=100*b2.ms, k_f=0.5, # Example Fluor params
                          num_stim_flags=16):
    """LIF neuron with conceptual Calcium and Fluorescence dynamics."""
    base_eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    dCa/dt = -Ca / tau_ca_val : 1 (unless refractory) # Calcium dynamics (unitless Ca here)
    dF/dt = (k_f_val * Ca - F) / tau_f_val : 1 (unless refractory) # Fluorescence dynamics (unitless F)
    """
    # On spike, Ca should be incremented. This is done in the 'reset' action.
    
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'R_m_val': R_m,
        'I_tonic_val': I_tonic, 'v_default_init': v_rest,
        'tau_ca_val': tau_ca, 'tau_f_val': tau_f, 'k_f_val': k_f,
        'Ca_default_init': 0.0, # Initial_L = g_L_bar_val * (E_L_val - v) : amp/meter**2
    """
    base_namespace = {
        'C_m_val': C_m, 'E_Na_val': E_Na, 'E_K_val': E_K, 'E_L_val': E_L,
        'g_Na_bar_val': g_Na_bar, 'g_K_bar_val': g_K_bar, 'g_L_bar_val': g_L_bar,
        'V_T_hh_val': V_T_hh, 'I_tonic_val': I_tonic, 
        'v_default_init': E_L, 'm_default_init': 0.05, 
        'h_default_init': 0.6, 'n_default_init': 0.32,
    }
    
    current_density_units_str = "amp/meter**2"
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags,
        current_vars_units=current_density_units_str
    )
    
    # Ensure default initializers for currents also use density units for HH
    # This is now handled inside the helper by passing current_vars_units
    # and using default_current_unit_obj.
    
    return {
        'model': full_eqs, 
        'threshold': f'v > {numerical_spike_threshold!r}', 
        'reset': '', 
        'refractory': refractory_period, 
        'namespace': full_namespace, 
        'method': 'exponential_euler' 
    }

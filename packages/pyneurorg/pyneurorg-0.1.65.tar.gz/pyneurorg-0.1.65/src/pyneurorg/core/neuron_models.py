# src/pyneurorg/core/neuron_models.py

"""
Collection of predefined neuron models for use with Brian2 in pyneurorg simulations.

All models include common variables for synaptic input ('I_synaptic'),
summed external stimulus input ('I_stimulus_sum'), and a tonic base current ('I_tonic_val').
They also include boolean flags 'stfX : boolean' (where X is an ID from 0
to num_stim_flags-1) for targeted stimulation.
"""

import brian2 as b2
from brian2.units.fundamentalunits import DIMENSIONLESS # For phase in sinusoidal or other dimensionless quantities

def _add_common_stim_syn_vars_and_flags(base_eqs_str: str,
                                        base_namespace_dict: dict,
                                        num_stim_flags: int = 16,
                                        current_vars_units: str = "amp"):
    """
    Appends common current variables (I_synaptic, I_stimulus_sum) and
    boolean stimulus flags (stf0, stf1, ...) to model equations and namespace.
    Ensures I_synaptic and I_stimulus_sum are declared with the specified units.
    """
    current_declarations = [
        f"I_synaptic : {current_vars_units} # Sum of synaptic currents (e.g., from non-conductance based synapses)",
        f"I_stimulus_sum : {current_vars_units} # Sum of external timed stimuli"
    ]

    flag_eqs_list = []
    default_flags_init_ns = {}
    for i in range(num_stim_flags):
        flag_name = f"stf{i}" # Stimulus Target Flag
        flag_eqs_list.append(f"{flag_name} : boolean")
        default_flags_init_ns[f"{flag_name}_default_init"] = False

    full_eqs_str_parts = []
    # Add common declarations first to avoid issues if base_eqs_str tries to use them before declaration
    full_eqs_str_parts.extend(current_declarations)
    if flag_eqs_list: # Add flags next
        full_eqs_str_parts.extend(flag_eqs_list)
    full_eqs_str_parts.append(base_eqs_str) # Then the model-specific equations

    full_eqs_str = "\n".join(filter(None, full_eqs_str_parts))

    updated_namespace = base_namespace_dict.copy()

    default_current_unit_obj = b2.amp
    if current_vars_units == "amp/meter**2":
        default_current_unit_obj = b2.amp / b2.meter**2

    updated_namespace.setdefault('I_synaptic_default_init', 0 * default_current_unit_obj)
    updated_namespace.setdefault('I_stimulus_sum_default_init', 0 * default_current_unit_obj)
    updated_namespace.update(default_flags_init_ns)

    return full_eqs_str, updated_namespace


def LIFNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
              v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
              refractory_period=2*b2.ms, num_stim_flags=16):
    """
    Leaky Integrate-and-Fire (LIF) neuron model.
    I_synaptic is for direct current input, not conductance-based.
    """
    # I_synaptic and I_stimulus_sum will be added by the helper.
    # The model uses them directly as currents.
    base_eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    """
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'R_m_val': R_m,
        'I_tonic_val': I_tonic, 'v_default_init': v_rest,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 'threshold': f'v > {v_thresh!r}', 'reset': f'v = {v_reset!r}',
        'refractory': refractory_period, 'namespace': full_namespace, 'method': 'exact'
    }

def ConductanceLIFNeuron(tau_m=20*b2.ms, v_rest=-65*b2.mV, v_reset=-65*b2.mV,
                         v_thresh=-50*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
                         refractory_period=3*b2.ms,
                         E_exc=0*b2.mV, E_inh=-80*b2.mV,
                         tau_g_exc=5*b2.ms, tau_g_inh=10*b2.ms, # Time constants for conductance decay
                         num_stim_flags=16):
    """
    LIF neuron model with explicit excitatory (g_exc) and inhibitory (g_inh)
    conductances that decay exponentially. Synapses should increment g_exc/g_inh directly.
    I_synaptic is for other non-conductance based current inputs.
    """
    # I_synaptic and I_stimulus_sum will be added by the helper.
    base_eqs = """
    I_conductance = g_exc*(E_exc_val - v) + g_inh*(E_inh_val - v) : amp
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_conductance + I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    dg_exc/dt = -g_exc / tau_g_exc_val : siemens (unless refractory)
    dg_inh/dt = -g_inh / tau_g_inh_val : siemens (unless refractory)
    g_exc : siemens # Excitatory conductance
    g_inh : siemens # Inhibitory conductance
    """
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'R_m_val': R_m,
        'I_tonic_val': I_tonic, 'E_exc_val': E_exc, 'E_inh_val': E_inh,
        'tau_g_exc_val': tau_g_exc, 'tau_g_inh_val': tau_g_inh,
        'v_default_init': v_rest,
        'g_exc_default_init': 0*b2.nS,
        'g_inh_default_init': 0*b2.nS
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs, 'threshold': f'v > {v_thresh!r}', 'reset': f'v = {v_reset!r}',
        'refractory': refractory_period, 'namespace': full_namespace, 'method': 'exact'
    }


def AdExNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
               V_T=-50.4*b2.mV, Delta_T=2*b2.mV, tau_w=144*b2.ms,
               a=4*b2.nS, adex_b_param=0.0805*b2.nA, V_reset=-70.6*b2.mV,
               V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=0*b2.ms,
               num_stim_flags=16):
    """Adaptive Exponential I&F (AdEx) neuron model."""
    base_eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V_T_val)/Delta_T_val) - w + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    dw/dt = (a_val * (v - E_L_val) - w) / tau_w_val : amp (unless refractory)
    """ # w is defined by dw/dt
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
        'method': 'euler' # Or exponential_euler if preferred for AdEx
    }

def FitzHughNagumoNeuron(a_param=0.7, b_param=0.8, tau_param=12.5*b2.ms,
                         I_tonic=0*b2.amp, # Note: I_tonic here is unitless in typical FHN, scale appropriately
                         v_thresh_fhn=0.5, # Arbitrary threshold for spike detection
                         num_stim_flags=16):
    """
    FitzHugh-Nagumo neuron model.
    v is dimensionless voltage-like variable, w is recovery variable.
    I_synaptic, I_stimulus_sum, I_tonic_val are dimensionless currents here.
    """
    # For FHN, currents are often dimensionless.
    # The helper _add_common_stim_syn_vars_and_flags assumes "amp" by default.
    # We need to handle this. For now, let's assume currents are passed as dimensionless
    # and the helper uses "1" as unit string. Or, we scale them inside.
    # Let's make the helper use "1" for dimensionless currents for this model.
    
    base_eqs = """
    dv/dt = (v - v**3 / 3 - w + I_synaptic + I_stimulus_sum + I_tonic_val) / tau_param_val : 1/second (unless refractory)
    dw/dt = (v + a_param_val - b_param_val * w) / tau_param_val : 1/second (unless refractory)
    """ # v and w are dimensionless, defined by dv/dt and dw/dt
    base_namespace = {
        'a_param_val': a_param, 'b_param_val': b_param, 'tau_param_val': tau_param,
        'I_tonic_val': I_tonic, # Assumed dimensionless or scaled appropriately
        'v_default_init': -1.0, # Typical resting v for FHN
        'w_default_init': -0.625, # Approx. w_rest = (v_rest + a)/b for v_rest=-1, a=0.7,b=0.8 -> (-1+0.7)/0.8 = -0.3/0.8 = -0.375. Or set from I_tonic.
                                 # Let's use: w = (v + a_param_val) / b_param_val for steady state with no I.
                                 # w_default_init = (-1.0 + a_param) / b_param if desired.
    }
    # For FHN, I_synaptic and I_stimulus_sum should also be dimensionless.
    # We pass current_vars_units="1" to the helper.
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="1" # Dimensionless
    )
    # Ensure I_tonic_val is also dimensionless in the namespace
    if isinstance(I_tonic, b2.Quantity) and I_tonic.is_dimensionless:
        full_namespace['I_tonic_val'] = I_tonic # It's already a Quantity
    elif isinstance(I_tonic, (int, float)):
         full_namespace['I_tonic_val'] = b2.Quantity(I_tonic, dim=DIMENSIONLESS)
    else: # If it has dimensions, try to make it dimensionless or raise error
        try:
            full_namespace['I_tonic_val'] = float(I_tonic / b2.amp) * b2.amp # Example to scale
            print(f"Warning: FitzHughNagumo I_tonic was {I_tonic}, assuming it should be scaled to dimensionless. Using its value in Amps as dimensionless value.")
            # Or raise ValueError("I_tonic for FitzHughNagumo must be dimensionless or convertible.")
            # For now, let's assume it's passed as a raw number or dimensionless Quantity
            if not (isinstance(I_tonic, b2.Quantity) and I_tonic.is_dimensionless) and not isinstance(I_tonic, (int, float)):
                 raise ValueError("I_tonic for FitzHughNagumo must be dimensionless or a number.")
        except:
             raise ValueError("I_tonic for FitzHughNagumo must be dimensionless or a number.")


    return {
        'model': full_eqs,
        'threshold': f'v > {v_thresh_fhn!r}', # This is a pseudo-threshold for spike detection
        'reset': 'v = -1.0; w += 0.0', # Example reset, can be tuned
        'refractory': 1*b2.ms, # Arbitrary refractory
        'namespace': full_namespace,
        'method': 'euler'
    }


def SimpleHHNeuron(C_m=1*b2.uF/b2.cm**2, E_Na=50*b2.mV, E_K=-77*b2.mV, E_L=-54.4*b2.mV,
                   g_Na_bar=120*b2.mS/b2.cm**2, g_K_bar=36*b2.mS/b2.cm**2, g_L_bar=0.3*b2.mS/b2.cm**2,
                   V_T_hh=-60*b2.mV, I_tonic=0*b2.uA/b2.cm**2, refractory_period=0*b2.ms,
                   num_stim_flags=16, area=1000*b2.um**2): # Added area for convenience
    """
    Simplified Hodgkin-Huxley (HH) neuron model.
    Currents (I_synaptic, I_stimulus_sum, I_tonic_val) are current densities (A/m^2).
    An 'area' parameter is included in the namespace for converting absolute currents to current densities if needed elsewhere.
    """
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
    I_L = g_L_bar_val * (E_L_val - v) : amp/meter**2
    area_val : meter**2 # Neuron area, for converting absolute currents to density
    """ # m, h, n are defined by their d/dt
    base_namespace = {
        'C_m_val': C_m, 'E_Na_val': E_Na, 'E_K_val': E_K, 'E_L_val': E_L,
        'g_Na_bar_val': g_Na_bar, 'g_K_bar_val': g_K_bar, 'g_L_bar_val': g_L_bar,
        'V_T_hh_val': V_T_hh, 'I_tonic_val': I_tonic,
        'v_default_init': E_L,
        'm_default_init': 0.0529,
        'h_default_init': 0.5961,
        'n_default_init': 0.3177,
        'area_val_default_init': area # Add area to namespace and for default init
    }

    current_density_units_str = "amp/meter**2"
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags,
        current_vars_units=current_density_units_str
    )
    # Ensure area_val is correctly in the final namespace if not already handled by _default_init logic
    if 'area_val' not in full_namespace: # Should be added by base_namespace copy
        full_namespace['area_val'] = area # Ensure it's a Brian2 Quantity if passed as number
    elif not isinstance(full_namespace['area_val'], b2.Quantity):
        full_namespace['area_val'] = area * b2.meter**2 # Default if not a Quantity

    return {
        'model': full_eqs,
        'threshold': f'v > {numerical_spike_threshold!r}',
        'reset': '',
        'refractory': refractory_period,
        'namespace': full_namespace,
        'method': 'exponential_euler'
    }

def LIFCalciumFluorNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
                          v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
                          refractory_period=2*b2.ms,
                          tau_ca=50*b2.ms, ca_spike_increment=0.2,
                          tau_f=100*b2.ms, k_f=0.5,
                          num_stim_flags=16):
    """LIF neuron with conceptual Calcium and Fluorescence dynamics."""
    base_eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    dCa/dt = -Ca / tau_ca_val : 1 (unless refractory)
    dF/dt = (k_f_val * Ca - F) / tau_f_val : 1 (unless refractory)
    """ # Ca and F are defined by dCa/dt and dF/dt
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'R_m_val': R_m, 'I_tonic_val': I_tonic,
        'tau_ca_val': tau_ca, 'tau_f_val': tau_f, 'k_f_val': k_f,
        'v_default_init': v_rest,
        'Ca_default_init': 0.0,
        'F_default_init': 0.0,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags, current_vars_units="amp"
    )
    full_namespace['ca_spike_increment_val'] = ca_spike_increment

    return {
        'model': full_eqs,
        'threshold': f'v > {v_thresh!r}',
        'reset': f'v = {v_reset!r}; Ca += ca_spike_increment_val',
        'refractory': refractory_period,
        'namespace': full_namespace,
        'method': 'euler'
    }
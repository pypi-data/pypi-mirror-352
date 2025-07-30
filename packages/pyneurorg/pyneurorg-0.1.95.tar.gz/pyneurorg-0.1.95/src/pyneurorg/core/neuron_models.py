# src/pyneurorg/core/neuron_models.py

"""
Collection of predefined neuron models for use with Brian2 in pyneurorg simulations.
(Resto da docstring como antes)
"""

import brian2 as b2
from brian2.units.fundamentalunits import DIMENSIONLESS
import numpy as np

def _add_common_stim_syn_vars_and_flags(base_eqs_str: str,
                                        base_namespace_dict: dict,
                                        num_stim_flags: int = 16,
                                        current_vars_units: str = "amp"):
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
    full_eqs_str_parts.extend(current_declarations)
    if flag_eqs_list:
        full_eqs_str_parts.extend(flag_eqs_list)
    full_eqs_str_parts.append(base_eqs_str)

    full_eqs_str = "\n".join(filter(None, full_eqs_str_parts))

    updated_namespace = base_namespace_dict.copy()

    default_current_unit_obj = b2.amp
    if current_vars_units == "amp/meter**2":
        default_current_unit_obj = b2.amp / b2.meter**2
    elif current_vars_units == "1": # Dimensionless
        default_current_unit_obj = b2.Quantity(1, dim=DIMENSIONLESS)


    updated_namespace.setdefault('I_synaptic_default_init', 0 * default_current_unit_obj)
    updated_namespace.setdefault('I_stimulus_sum_default_init', 0 * default_current_unit_obj)
    updated_namespace.update(default_flags_init_ns)

    return full_eqs_str, updated_namespace


def LIFNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
              v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
              refractory_period=2*b2.ms, num_stim_flags=16):
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
                         tau_g_exc=5*b2.ms, tau_g_inh=10*b2.ms,
                         num_stim_flags=16):
    base_eqs = """
    I_conductance = g_exc*(E_exc_val - v) + g_inh*(E_inh_val - v) : amp
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_conductance + I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    dg_exc/dt = -g_exc / tau_g_exc_val : siemens (unless refractory)
    dg_inh/dt = -g_inh / tau_g_inh_val : siemens (unless refractory)
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
        'refractory': refractory_period, 'namespace': full_namespace,
        'method': 'euler'
    }


def AdExNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
               V_T=-50.4*b2.mV, Delta_T=2*b2.mV, tau_w=144*b2.ms,
               a=4*b2.nS, adex_b_param=0.0805*b2.nA, V_reset=-70.6*b2.mV,
               V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=0*b2.ms,
               num_stim_flags=16):
    base_eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V_T_val)/Delta_T_val) - w + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    dw/dt = (a_val * (v - E_L_val) - w) / tau_w_val : amp (unless refractory)
    """
    temp_base_namespace = {
        'C_m_val': C_m, 'g_L_val': g_L, 'E_L_val': E_L, 'V_T_val': V_T, 'Delta_T_val': Delta_T,
        'tau_w_val': tau_w, 'a_val': a, 'I_tonic_val': I_tonic,
        'v_default_init': E_L, 'w_default_init': 0*b2.nA,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, temp_base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs,
        'threshold': f'v > {V_peak!r}',
        'reset': f'v = {V_reset!r}; w += {adex_b_param!r}',
        'refractory': refractory_period,
        'namespace': full_namespace,
        'method': 'euler' 
    }

def SimpleEIFNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
                    V_T=-50.4*b2.mV, Delta_T=2*b2.mV, V_reset=-70.6*b2.mV,
                    V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=2*b2.ms,
                    num_stim_flags=16):
    """
    Simple Exponential Integrate-and-Fire (EIF) neuron model.
    This is the AdEx model without the adaptation variable 'w'.
    """
    base_eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V_T_val)/Delta_T_val) + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    """
    temp_base_namespace = {
        'C_m_val': C_m, 'g_L_val': g_L, 'E_L_val': E_L, 'V_T_val': V_T, 'Delta_T_val': Delta_T,
        'I_tonic_val': I_tonic,
        'v_default_init': E_L,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, temp_base_namespace, num_stim_flags, current_vars_units="amp"
    )
    return {
        'model': full_eqs,
        'threshold': f'v > {V_peak!r}',
        'reset': f'v = {V_reset!r}', # No w to update
        'refractory': refractory_period,
        'namespace': full_namespace,
        'method': 'euler' # Euler or exponential_euler
    }


def SimpleHHNeuron(C_m=1*b2.uF/b2.cm**2, E_Na=50*b2.mV, E_K=-77*b2.mV, E_L=-54.4*b2.mV,
                   g_Na_bar=120*b2.mS/b2.cm**2, g_K_bar=36*b2.mS/b2.cm**2, g_L_bar=0.3*b2.mS/b2.cm**2,
                   V_T_hh=-60*b2.mV, I_tonic=0*b2.uA/b2.cm**2, refractory_period=0*b2.ms,
                   num_stim_flags=16, area=1000*b2.um**2):
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
    area_val : meter**2 
    """
    base_namespace = {
        'C_m_val': C_m, 'E_Na_val': E_Na, 'E_K_val': E_K, 'E_L_val': E_L,
        'g_Na_bar_val': g_Na_bar, 'g_K_bar_val': g_K_bar, 'g_L_bar_val': g_L_bar,
        'V_T_hh_val': V_T_hh, 'I_tonic_val': I_tonic,
        'v_default_init': E_L,
        'm_default_init': 0.0529,
        'h_default_init': 0.5961,
        'n_default_init': 0.3177,
        'area_val_default_init': area 
    }

    current_density_units_str = "amp/meter**2"
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, base_namespace, num_stim_flags,
        current_vars_units=current_density_units_str
    )
    if 'area_val' not in full_namespace:
         full_namespace['area_val'] = area 
    if not isinstance(full_namespace['area_val'], b2.Quantity):
        if isinstance(full_namespace['area_val'], (int, float)): #pragma: no cover
            full_namespace['area_val'] = full_namespace['area_val'] * b2.meter**2
        else: 
            try: #pragma: no cover
                full_namespace['area_val'] = full_namespace['area_val'].in_units(b2.meter**2)
            except: #pragma: no cover
                raise TypeError("area_val for SimpleHHNeuron must be convertible to meter**2")


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
    base_eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    dCa/dt = -Ca / tau_ca_val : 1 (unless refractory)
    dF/dt = (k_f_val * Ca - F) / tau_f_val : 1 (unless refractory)
    """
    temp_base_namespace = { 
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'R_m_val': R_m,
        'I_tonic_val': I_tonic, 
        'tau_ca_val': tau_ca, 'tau_f_val': tau_f, 'k_f_val': k_f,
        'v_default_init': v_rest,
        'Ca_default_init': 0.0,
        'F_default_init': 0.0,
    }
    full_eqs, full_namespace = _add_common_stim_syn_vars_and_flags(
        base_eqs, temp_base_namespace, num_stim_flags, current_vars_units="amp"
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
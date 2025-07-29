# src/pyneurorg/core/synapse_models.py

"""
Collection of predefined synapse models for use with Brian2 in pyneurorg simulations.

These models typically describe how a presynaptic spike influences a postsynaptic neuron,
often by modulating a conductance variable (e.g., 'g_exc', 'g_inh', 'g_nmda')
in the postsynaptic neuron's model. The decay dynamics of these conductances
are generally assumed to be handled by the postsynaptic neuron model itself,
unless specified otherwise by a particular synapse model that defines its own
internal state variables for conductance.
"""

import brian2 as b2

def StaticConductionSynapse(weight_increment=1.0*b2.nS, target_conductance_var='g_exc'):
    """
    A simple synapse that causes an instantaneous, fixed increase in the
    `target_conductance_var` of the postsynaptic neuron upon a presynaptic spike.

    The decay of this conductance is assumed to be handled by the postsynaptic
    neuron model (e.g., if it has an equation like `dg_exc/dt = -g_exc/tau_exc`).

    Parameters
    ----------
    weight_increment : brian2.units.Quantity, optional
        The amount of conductance to add (default: 1.0 nS). This will be assigned
        to the 'w_inc' parameter of the synapse.
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron
        (e.g., 'g_exc', 'g_ampa').
    """
    model_eqs = """
    w_inc : siemens (constant) # Weight increment per spike
    """
    on_pre_action = f'{target_conductance_var}_post += w_inc'

    # The namespace here can hold defaults for model parameters if they were
    # part of the model_eqs and not set per-synapse.
    # For w_inc, it's a per-synapse parameter, so its value will be set
    # when connections are made or via S.w_inc = ...
    # The 'weight_increment' argument to this function serves as the value
    # to be used by Organoid/Simulator when setting S.w_inc.
    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {} # Empty as w_inc is set via synaptic_params in Organoid
    }

def ExponentialIncrementSynapse(weight_increment=0.5*b2.nS, target_conductance_var='g_exc'):
    """
    Synapse that causes an instantaneous increase in the `target_conductance_var`
    of the postsynaptic neuron.

    The name implies an expectation of exponential decay for this conductance,
    but the decay dynamics *must* be implemented in the postsynaptic neuron model.
    This synapse model itself does not implement decay for the target_conductance_var.

    Parameters
    ----------
    weight_increment : brian2.units.Quantity, optional
        The amount of conductance to add (default: 0.5 nS). Assigned to 'w_inc'.
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron.
    """
    model_eqs = """
    w_inc : siemens (constant) # Weight increment per spike
    """
    on_pre_action = f'{target_conductance_var}_post += w_inc'

    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {}
    }

def STPSynapse(U_stp=0.5, tau_facilitation=50*b2.ms, tau_depression=200*b2.ms,
               base_weight=1.0*b2.nS, target_conductance_var='g_exc'):
    """
    Conductance-based synapse with short-term plasticity (Tsodyks-Markram model).
    The synaptic efficacy changes based on recent presynaptic activity.
    The actual conductance decay is handled by the postsynaptic neuron.

    Parameters are typically set per synapse group, but can be made heterogeneous
    if defined as (constant) per synapse and set individually.

    Parameters
    ----------
    U_stp : float, optional
        Utilization of synaptic efficacy (default: 0.5). This will be 'U_stp_val'.
    tau_facilitation : brian2.units.Quantity, optional
        Time constant for recovery of facilitation variable `u_stp` (default: 50 ms). This will be 'tau_f_val'.
    tau_depression : brian2.units.Quantity, optional
        Time constant for recovery of depression variable `x_stp` (default: 200 ms). This will be 'tau_d_val'.
    base_weight : brian2.units.Quantity, optional
        Baseline conductance increment when u_stp=U_stp and x_stp=1 (default: 1.0 nS). This will be 'w_base'.
    target_conductance_var : str, optional
        Name of the conductance variable in the postsynaptic neuron.
    """
    model_eqs = """
    dx_stp/dt = (1 - x_stp) / tau_d_val : 1 (clock-driven)
    du_stp/dt = -u_stp / tau_f_val : 1 (clock-driven)
    
    # Synapse-specific parameters that can be set during synapse creation/connection
    # These are treated as (constant) if not specified as (constant over dt) or per-synapse
    U_stp_val : 1            # Utilization factor
    tau_f_val : second       # Facilitation time constant
    tau_d_val : second       # Depression time constant
    w_base    : siemens      # Baseline weight/conductance increment
    """
    # x_stp and u_stp are the state variables of the synapse for plasticity
    
    on_pre_action = f"""
    u_stp_effective = u_stp + U_stp_val * (1 - u_stp)     # u_stp is the current value of the facilitation variable
    {target_conductance_var}_post += w_base * u_stp_effective * x_stp # x_stp is current value of depression variable
    u_stp = u_stp_effective                               # Update u_stp for next spike
    x_stp = x_stp * (1 - u_stp_effective)                 # Update x_stp
    """
    # Initial values for u_stp and x_stp are important.
    # u_stp usually starts at 0, x_stp at 1.
    # These will be set by Organoid.add_synapses via synaptic_params if needed,
    # or default to 0 if not explicitly initialized by Brian2 for state variables.
    # It's better to provide defaults in the namespace.
    
    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {
            # Defaults for parameters if not overridden by synaptic_params in Organoid
            # These are for parameters *within* the synapse model, not the state variables themselves.
            # Brian2's Synapses will use these if synaptic_params in Organoid.add_synapses
            # doesn't set them for U_stp_val, tau_f_val, tau_d_val, w_base.
            # State variables like x_stp, u_stp need default inits too.
            'U_stp_val_default_init': U_stp, # This is a bit redundant if they are (constant) & set by Organoid
            'tau_f_val_default_init': tau_facilitation,
            'tau_d_val_default_init': tau_depression,
            'w_base_default_init': base_weight,
            'x_stp_default_init': 1.0, # Initial value for the state variable x_stp
            'u_stp_default_init': 0.0  # Initial value for the state variable u_stp
        },
        'method': 'exact' # Linear ODEs for x_stp and u_stp
    }

def NMDASynapse(weight_nmda=0.5*b2.nS, target_conductance_var='g_nmda'):
    """
    NMDA receptor-mediated conductance synapse.
    This model only increments the `target_conductance_var` (e.g., 'g_nmda').
    The postsynaptic neuron model *must* implement the voltage-dependent
    magnesium block B(V) and the decay dynamics for g_nmda.

    Parameters
    ----------
    weight_nmda : brian2.units.Quantity, optional
        The amount of g_nmda conductance to add on a spike (default: 0.5 nS). Assigned to 'w_nmda_inc'.
    target_conductance_var : str, optional
        Name of the NMDA conductance variable in the postsynaptic neuron.
    """
    model_eqs = """
    w_nmda_inc : siemens (constant) # NMDA conductance increment per spike
    """
    on_pre_action = f'{target_conductance_var}_post += w_nmda_inc'
    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {}
    }

def GABAaIncrementSynapse(weight_gabaa=1.0*b2.nS, target_conductance_var='g_inh'):
    """
    GABA_A receptor-mediated inhibitory synapse (fast inhibition).
    Increments `target_conductance_var` (e.g., 'g_gabaa' or 'g_inh') in the postsynaptic neuron.
    The decay of this conductance is handled by the postsynaptic neuron.

    Parameters
    ----------
    weight_gabaa : brian2.units.Quantity, optional
        Amount of conductance to add on a spike (default: 1.0 nS). Assigned to 'w_gabaa_inc'.
    target_conductance_var : str, optional
        Name of the GABA_A conductance variable.
    """
    model_eqs = """
    w_gabaa_inc : siemens (constant)
    """
    on_pre_action = f'{target_conductance_var}_post += w_gabaa_inc'
    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {}
    }

def GABABIncrementSynapse(weight_gabab=0.2*b2.nS, target_conductance_var='g_inh'):
    """
    Simplified GABA_B receptor-mediated inhibitory synapse (slower inhibition).
    Increments `target_conductance_var` in the postsynaptic neuron.
    The postsynaptic neuron is assumed to have a slower decay time constant for this
    conductance compared to GABA_A.

    Parameters
    ----------
    weight_gabab : brian2.units.Quantity, optional
        Amount of conductance to add on a spike (default: 0.2 nS). Assigned to 'w_gabab_inc'.
    target_conductance_var : str, optional
        Name of the GABA_B conductance variable (e.g., 'g_gabab' or 'g_inh').
    """
    model_eqs = """
    w_gabab_inc : siemens (constant)
    """
    on_pre_action = f'{target_conductance_var}_post += w_gabab_inc'
    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {}
    }

def GapJunctionSynapse(gap_conductance_val=0.1*b2.nS): # Renamed for clarity
    """
    Electrical synapse (gap junction).
    The current `I_gap = g_gap * (v_pre - v_post)` is summed into a variable
    (e.g., `I_gap_summed`) in the postsynaptic neuron model.

    The postsynaptic neuron model must have a variable like `I_gap_summed : amp`
    in its equations, which will be the target of the summed current from
    all connected gap junctions. This variable should then be part of the
    neuron's total current calculation in its dv/dt equation.

    Parameters
    ----------
    gap_conductance_val : brian2.units.Quantity, optional
        Conductance of the gap junction (default: 0.1 nS). This will be assigned
        to the 'g_gap' parameter of the synapse.
    """
    model_eqs = """
    g_gap : siemens (constant) # Gap junction conductance, set per synapse
    # The current is summed into the postsynaptic neuron.
    # The postsynaptic neuron must define 'I_gap_summed : amp' or similar.
    # This is achieved by connecting this synapse's 'I_gap_term' to it.
    # Brian2 does this by linking 'variable_post = variable_pre (summed)'
    # or through a direct current injection term in the synapse.
    # Let's define the current directly here.
    # The target variable in the neuron should be named `I_gap_summed`
    I_gap_summed_post = g_gap * (v_pre - v_post) : amp (summed)
    """
    # No 'on_pre' is strictly needed as the current is continuous.
    # The 'namespace' can hold defaults for g_gap if it were not set per synapse.
    # Here, g_gap is a per-synapse parameter set by Organoid.
    return {
        'model': model_eqs,
        'on_pre': '', # No explicit action on spike for current calculation itself
        'namespace': {}
    }
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
        The amount of conductance to add (default: 1.0 nS).
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron
        (e.g., 'g_exc', 'g_ampa').
    """
    model_eqs = """
    w_inc : siemens (constant) # Weight increment per spike
    """
    on_pre_action = f'{target_conductance_var}_post += w_inc'

    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {
            # w_inc is a per-synapse parameter.
            # The `weight_increment` arg can be used as a default when creating connections,
            # which will be assigned to S.w_inc by the Organoid/Simulator.
        }
    }

def ExponentialIncrementSynapse(weight_increment=0.5*b2.nS, target_conductance_var='g_exc'):
    """
    Synapse that causes an instantaneous increase in the `target_conductance_var`
    of the postsynaptic neuron.

    The name implies an expectation of exponential decay for this conductance,
    but the decay dynamics *must* be implemented in the postsynaptic neuron model.
    This synapse model itself does not implement decay.

    Parameters
    ----------
    weight_increment : brian2.units.Quantity, optional
        The amount of conductance to add (default: 0.5 nS).
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron.
    """
    # Functionally identical to StaticConductionSynapse in its implementation,
    # the name difference is conceptual for the user.
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

    Parameters
    ----------
    U_stp : float, optional
        Utilization of synaptic efficacy (fraction of resources used by a spike, unitless, default: 0.5).
    tau_facilitation : brian2.units.Quantity, optional
        Time constant for recovery of facilitation variable `u_stp` (default: 50 ms).
    tau_depression : brian2.units.Quantity, optional
        Time constant for recovery of depression variable `x_stp` (default: 200 ms).
    base_weight : brian2.units.Quantity, optional
        The baseline synaptic weight/conductance increment when u_stp=U_stp and x_stp=1 (default: 1.0 nS).
    target_conductance_var : str, optional
        The name of the conductance variable in the postsynaptic neuron.
    """
    model_eqs = """
    dx_stp/dt = (1 - x_stp) / tau_d_val : 1 (clock-driven) # Recovery of available resources
    du_stp/dt = -u_stp / tau_f_val : 1 (clock-driven)     # Recovery of facilitation factor
    
    # Per-synapse parameters (can be made heterogeneous)
    U_stp_val : 1 (constant)
    tau_f_val : second (constant)
    tau_d_val : second (constant)
    w_base : siemens (constant) # Baseline weight
    """
    # On a presynaptic spike:
    # 1. Conductance change: g_post += w_base * u_eff * x_eff
    #    (u_eff and x_eff are values of u_stp and x_stp *before* this spike's update)
    # 2. Update u_stp (facilitation): u_stp_new = u_stp + U_stp_val * (1 - u_stp)
    # 3. Update x_stp (depression): x_stp_new = x_stp * (1 - u_eff_for_this_spike)
    #    where u_eff_for_this_spike is the (updated) u_stp
    #
    # Brian2's on_pre executes statements sequentially.
    # We need to use u_stp and x_stp *before* they are updated for the current spike's effect.
    # A common way is to calculate the effective u for this spike, then apply conductance, then update x.
    
    on_pre_action = f"""
    u_eff_stp = u_stp_val + U_stp_val * (1 - u_stp_val) # Effective u for this spike (facilitated)
    conductance_change = w_base * u_eff_stp * x_stp_val # Calculate conductance change
    {target_conductance_var}_post += conductance_change  # Apply to postsynaptic neuron

    u_stp_val = u_eff_stp             # Update u_stp for the next spike
    x_stp_val = x_stp_val * (1 - u_eff_stp) # Update x_stp (depression based on the used u_eff_stp)
    """
    # Note: The above formulation for u_eff_stp might be slightly different from some Tsodyks-Markram versions.
    # A common version:
    # on_pre:
    #   g_post += A * u * x
    #   u = u + U * (1-u)
    #   x = x * (1-u_prev_spike) where u_prev_spike is u *before* U is added.
    # Let's use a formulation closer to Brian2 examples:
    on_pre_action_v2 = f"""
    effective_u = u_stp + U_stp_val * (1 - u_stp)
    {target_conductance_var}_post += w_base * effective_u * x_stp
    u_stp = effective_u
    x_stp = x_stp * (1 - effective_u)
    """
    # Initial values for u_stp and x_stp are important.
    # u_stp usually starts at 0 or U_stp, x_stp at 1.

    return {
        'model': model_eqs,
        'on_pre': on_pre_action_v2, # Use v2 which is more standard
        'namespace': {
            'U_stp_val_default_init': U_stp, # Default for the parameter U_stp_val if not set
            'tau_f_val_default_init': tau_facilitation,
            'tau_d_val_default_init': tau_depression,
            'w_base_default_init': base_weight,
            'x_stp_default_init': 1.0, # Start with full resources
            'u_stp_default_init': 0.0  # Start with no facilitation (will jump to U_stp on first spike)
                                      # or U_stp if u_eff_stp is u_stp_val in the on_pre
                                      # If on_pre is u_stp = u_stp + U(1-u_stp), then u_stp should start at 0.
                                      # If on_pre is u_stp = U + u_stp*(1-U), then u_stp should start at U.
                                      # The v2 uses u_stp_default_init = 0.0 and first spike u_eff = U.
        },
        'method': 'exact' # ODEs for x_stp and u_stp are linear
    }

def NMDASynapse(weight_nmda=0.5*b2.nS, target_conductance_var='g_nmda',
                mg_conc=1.0, eta_nmda=0.08, gamma_nmda=0.062):
    """
    NMDA receptor-mediated conductance synapse with voltage-dependent magnesium block.
    The actual conductance decay (e.g., for g_nmda) is handled by the postsynaptic neuron.
    This synapse model calculates the effective current based on g_nmda and voltage block.

    This model assumes the postsynaptic neuron has 'g_nmda' which this synapse increments,
    AND the postsynaptic neuron's dv/dt includes a term like:
    `I_nmda_current = g_nmda * (1.0 / (1.0 + eta_nmda_val * mg_conc_val * exp(-gamma_nmda_val * v_post/mV))) * (E_nmda - v_post)`
    OR, this synapse can directly write to a current I_nmda_summed : amp.

    Let's choose the simpler path: this synapse increments target_conductance_var,
    and the postsynaptic neuron model *must* implement the B(V) term in its equations.

    Parameters
    ----------
    weight_nmda : brian2.units.Quantity, optional
        The amount of g_nmda conductance to add on a spike (default: 0.5 nS).
    target_conductance_var : str, optional
        Name of the NMDA conductance variable in the postsynaptic neuron (e.g., 'g_nmda').
    mg_conc, eta_nmda, gamma_nmda : float, optional
        Parameters for the magnesium block function B(V). These would typically be
        part of the postsynaptic neuron's namespace if B(V) is computed there.
        If this synapse were to compute the current directly, they'd be here.
        Since we are only incrementing a conductance, these are not directly used
        by *this synapse model's equations or on_pre*, but are listed for conceptual completeness
        as they are essential for the NMDA current calculation in the postsynaptic neuron.
    """
    model_eqs = """
    w_nmda_inc : siemens (constant) # NMDA conductance increment per spike
    """
    on_pre_action = f'{target_conductance_var}_post += w_nmda_inc'

    # The namespace for this synapse model itself is minimal if it only increments.
    # The parameters mg_conc, eta_nmda, gamma_nmda would be needed by the
    # postsynaptic neuron model.
    return {
        'model': model_eqs,
        'on_pre': on_pre_action,
        'namespace': {}
    }

def GABAAIncrementSynapse(weight_gabaa=1.0*b2.nS, target_conductance_var='g_gabaa'):
    """
    GABA_A receptor-mediated inhibitory synapse (fast inhibition).
    Increments `target_conductance_var` (e.g., 'g_gabaa') in the postsynaptic neuron.
    The decay of this conductance is handled by the postsynaptic neuron.

    Parameters
    ----------
    weight_gabaa : brian2.units.Quantity, optional
        Amount of g_gabaa conductance to add on a spike (default: 1.0 nS).
    target_conductance_var : str, optional
        Name of the GABA_A conductance variable (e.g., 'g_gabaa', 'g_inh').
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

def GABABIncrementSynapse(weight_gabab=0.2*b2.nS, target_conductance_var='g_gabab'):
    """
    Simplified GABA_B receptor-mediated inhibitory synapse (slower inhibition).
    Increments `target_conductance_var` (e.g., 'g_gabab') in the postsynaptic neuron.
    The postsynaptic neuron is assumed to have a slower decay time constant for this
    conductance compared to GABA_A.

    Parameters
    ----------
    weight_gabab : brian2.units.Quantity, optional
        Amount of g_gabab conductance to add on a spike (default: 0.2 nS).
    target_conductance_var : str, optional
        Name of the GABA_B conductance variable (e.g., 'g_gabab').
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


def GapJunctionSynapse(gap_conductance=0.1*b2.nS):
    """
    Electrical synapse (gap junction).
    Allows direct flow of current between connected neurons proportional to
    their voltage difference and `gap_conductance`.

    The current `I_gap_post = g_gap * (v_pre - v_post)` is injected into the
    postsynaptic neuron. The postsynaptic neuron model should include a variable
    like `I_gap_summed : amp` in its equations, which this synapse will target.
    The `(summed)` flag for `I_gap_summed` in the neuron handles multiple gap junctions.

    Parameters
    ----------
    gap_conductance : brian2.units.Quantity, optional
        Conductance of the gap junction (default: 0.1 nS).
    """
    # This model defines a current that is continuously active, not just on_pre.
    # Brian2 handles this by defining the equation that links pre and post.
    # The variable I_gap_summed_post will be summed into the postsynaptic neuron.
    # The postsynaptic neuron must have a variable I_gap_summed : amp.
    model_eqs = """
    g_gap : siemens (constant) # Gap junction conductance
    I_gap_summed_post = g_gap * (v_pre - v_post) : amp (summed)
    """
    # No on_pre or on_post needed as current flows based on voltage difference.
    return {
        'model': model_eqs,
        'on_pre': '', # No action on presynaptic spike per se for current flow
        'namespace': {
            # g_gap is a per-synapse parameter.
            # The `gap_conductance` arg can be used as default.
        }
    }
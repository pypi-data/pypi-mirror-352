# pyneurorg/visualization/spike_plotter.py

"""
Functions for visualizing spike train data and membrane potential traces
from pyneurorg simulations, using Matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
import brian2 as b2
from brian2.units.fundamentalunits import DIMENSIONLESS # Para o ThetaNeuron

def plot_raster(spike_indices, spike_times, duration=None, ax=None,
                marker_size=2, marker_color='black', title="Raster Plot",
                time_unit_display=b2.ms, ylabel="Neuron Index"):
    """
    Generates a raster plot of spike activity.
    (Docstring como antes)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    try:
        plot_times_val = np.asarray(spike_times / time_unit_display)
    except AttributeError: 
        plot_times_val = np.asarray(spike_times)
    except Exception as e:
        raise TypeError(f"Could not process spike_times. Expected Brian2 VariableView/Quantity or array-like. Error: {e}")

    plot_indices_val = np.asarray(spike_indices)
    if not (plot_indices_val.ndim == 1 and plot_times_val.ndim == 1 and len(plot_indices_val) == len(plot_times_val)):
        if len(plot_indices_val) == 0 and len(plot_times_val) == 0:
            pass
        else:
            raise ValueError("spike_indices and spike_times must be 1D arrays of the same length.")


    plot_duration_val = None
    if duration is not None:
        if isinstance(duration, b2.Quantity):
            if duration.dimensions != b2.second.dimensions:
                raise TypeError("duration must have time dimensions if it's a Brian2 Quantity.")
            plot_duration_val = float(duration / time_unit_display)
        elif isinstance(duration, (int, float)):
            plot_duration_val = float(duration)
        else:
            raise TypeError("duration must be a Brian2 Quantity, a number, or None.")

    if len(plot_times_val) > 0 or plot_duration_val is not None:
        ax.plot(plot_times_val, plot_indices_val, '|', markersize=marker_size, color=marker_color)
        ax.set_xlabel(f"Time ({time_unit_display!s})")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        if plot_duration_val is not None:
            ax.set_xlim([0, plot_duration_val])
        elif len(plot_times_val) > 0:
            min_t, max_t = np.min(plot_times_val), np.max(plot_times_val)
            padding = 0.05 * (max_t - min_t) if (max_t - min_t) > 1e-9 else 0.05 * max_t
            if padding == 0 and max_t == 0 : padding = 1.0
            ax.set_xlim([max(0, min_t - padding), max_t + padding])
        else:
            ax.set_xlim([0, 1])

        if len(plot_indices_val) > 0:
            ax.set_ylim([np.min(plot_indices_val) - 0.5, np.max(plot_indices_val) + 0.5])
        else:
            ax.set_ylim([-0.5, 0.5])
    else:
        ax.set_xlabel(f"Time ({time_unit_display!s})")
        ax.set_ylabel(ylabel)
        ax.set_title(title + " (No data)")
        ax.set_xlim([0,1]); ax.set_ylim([-0.5, 0.5])

    ax.grid(True, linestyle=':', alpha=0.7)
    return ax


def plot_vm_traces(state_monitor, neuron_indices=None, time_unit_display=b2.ms, 
                   voltage_unit_display=b2.mV, # Default for Vm
                   ax=None, title="State Variable Traces", # Title mais genérico
                   xlabel=None, ylabel=None, legend_loc="best", alpha=0.8,
                   default_max_traces_to_plot=7): # Novo parâmetro
    """
    Plots state variable traces (e.g., Vm, theta) for selected neurons from a StateMonitor.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    times_qty = state_monitor.t 
    
    # Determinar qual variável primária plotar (v ou theta)
    main_recorded_var_name = ""
    main_var_data_raw = None
    main_var_display_unit = voltage_unit_display # Default para Vm
    y_axis_label_base = "Vm" # Default

    if hasattr(state_monitor, 'v'): 
        main_recorded_var_name = 'v'
        main_var_data_raw = state_monitor.v
        main_var_display_unit = voltage_unit_display
        y_axis_label_base = "Vm"
    elif hasattr(state_monitor, 'theta'): # Para ThetaNeuron
        main_recorded_var_name = 'theta'
        main_var_data_raw = state_monitor.theta
        main_var_display_unit = b2.Quantity(1, dim=DIMENSIONLESS) # Theta é adimensional
        y_axis_label_base = "Theta"
    elif state_monitor.variables: 
        first_var_key = list(state_monitor.variables.keys())[0]
        main_recorded_var_name = first_var_key
        main_var_data_raw = getattr(state_monitor, first_var_key)
        # Tentar inferir unidade de display para variáveis genéricas
        if isinstance(main_var_data_raw, b2.Quantity):
             main_var_display_unit = b2.Quantity(1.0, dim=main_var_data_raw.dimensions).get_best_unit().dimensions
        else: # Se for VariableView de array numpy, assumir unitless ou raw
            main_var_display_unit = b2.Quantity(1, dim=DIMENSIONLESS) 
        y_axis_label_base = main_recorded_var_name
        print(f"Info: Plotting variable '{main_recorded_var_name}' as the main trace.")
    else:
        raise AttributeError("StateMonitor does not seem to have recorded 'v', 'theta', or any other variables.")
    
    if main_var_data_raw is None:
        raise AttributeError(f"Could not extract primary data ('v' or 'theta') from StateMonitor.")

    try:
        times_val = np.asarray(times_qty / time_unit_display)
    except Exception as e:
        raise TypeError(f"Could not process StateMonitor.t. Error: {e}")
    
    # Processar a variável principal
    main_var_plot_values = np.asarray(main_var_data_raw) # Assume já é array numérico após getattr
    if isinstance(main_var_data_raw, b2.Quantity): # Se for Quantity, converte
        if main_var_display_unit.is_dimensionless:
            main_var_plot_values = np.asarray(main_var_data_raw / b2.Quantity(1, dim=DIMENSIONLESS)) # Dividir por 1 para manter valor
        else:
            try:
                main_var_plot_values = np.asarray(main_var_data_raw / main_var_display_unit)
            except Exception as e:
                 raise TypeError(f"Could not process StateMonitor variable '{main_recorded_var_name}' with unit {main_var_display_unit}. Error: {e}")
    
    num_actually_recorded_neurons = main_var_plot_values.shape[0]
    indices_in_monitor_to_plot = []

    if neuron_indices is None:
        if num_actually_recorded_neurons <= default_max_traces_to_plot:
            indices_in_monitor_to_plot = list(range(num_actually_recorded_neurons))
        elif num_actually_recorded_neurons > 0:
            print(f"Warning: {num_actually_recorded_neurons} neurons recorded by StateMonitor and neuron_indices=None. "
                  f"Plotting first {default_max_traces_to_plot} traces. Specify 'neuron_indices' for more control.")
            indices_in_monitor_to_plot = list(range(default_max_traces_to_plot))
    elif isinstance(neuron_indices, int):
        if not (0 <= neuron_indices < num_actually_recorded_neurons):
            raise ValueError(f"neuron_index {neuron_indices} out of bounds for monitor's data (0-{num_actually_recorded_neurons-1}).")
        indices_in_monitor_to_plot = [neuron_indices]
    elif isinstance(neuron_indices, (list, slice, np.ndarray)):
        if isinstance(neuron_indices, slice):
            indices_in_monitor_to_plot = list(range(*neuron_indices.indices(num_actually_recorded_neurons)))
        else: 
            indices_in_monitor_to_plot = list(neuron_indices)
        for idx_mon in indices_in_monitor_to_plot:
            if not (0 <= idx_mon < num_actually_recorded_neurons):
                raise ValueError(f"Neuron index {idx_mon} out of bounds for monitor's data (0-{num_actually_recorded_neurons-1}).")
    else:
        raise TypeError("neuron_indices must be None, int, list, slice, or np.ndarray.")

    if not indices_in_monitor_to_plot and num_actually_recorded_neurons > 0:
        print("Warning: No specific neuron indices selected for plotting traces.")
    elif num_actually_recorded_neurons == 0:
        print("Warning: StateMonitor recorded no data or no neurons for the primary variable.")

    for monitor_idx_to_plot in indices_in_monitor_to_plot:
        original_neuron_label = ""
        if isinstance(state_monitor.record, (list, np.ndarray)): 
            original_neuron_label = f"Neuron {state_monitor.record[monitor_idx_to_plot]}"
        elif isinstance(state_monitor.record, slice):
            start = state_monitor.record.start if state_monitor.record.start is not None else 0
            step = state_monitor.record.step if state_monitor.record.step is not None else 1
            original_neuron_label = f"Neuron {start + monitor_idx_to_plot * step}"
        elif state_monitor.record is True: 
            original_neuron_label = f"Neuron {monitor_idx_to_plot}"
        else: 
            original_neuron_label = f"Trace {monitor_idx_to_plot}"
        ax.plot(times_val, main_var_plot_values[monitor_idx_to_plot, :], label=original_neuron_label, alpha=alpha)

    ax.set_title(title)
    ax.set_xlabel(xlabel if xlabel is not None else f"Time ({time_unit_display!s})")
    
    y_unit_str_for_label = str(main_var_display_unit) if not main_var_display_unit.is_dimensionless else "(dimless)"
    if main_var_display_unit == b2.volt: y_unit_str_for_label = "mV" # Prefer mV if it's volt
    
    ax.set_ylabel(ylabel if ylabel is not None else f"{y_axis_label_base} ({y_unit_str_for_label})")

    if legend_loc and len(indices_in_monitor_to_plot) > 0:
        ax.legend(loc=legend_loc, fontsize='small')

    ax.grid(True, linestyle=':', alpha=0.7)
    return ax
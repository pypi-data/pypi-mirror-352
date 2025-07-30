# src/pyneurorg/electrophysiology/data_persistence/persistent_simulator.py

"""
Defines PersistentSimulator, a version of the Simulator that integrates
SQLite data persistence for simulation metadata, setup, and results.
"""

import brian2 as b2
import numpy as np
import uuid
from datetime import datetime
import traceback
import json # Para serializar record_details_json dos monitores

# Importar do pacote principal pyneurorg
from ...organoid.organoid import Organoid
from ...mea.mea import MEA
from ...electrophysiology import brian_monitors as pbg_monitors
from ...simulation.simulator import Simulator as BaseSimulator # Importar como Base
from .sqlite_writer import SQLiteWriter
from ... import __version__ as pyneurorg_version # Para logar a versão

# Bitvector Flags for Logging Options
LOG_NOTHING = 0
LOG_SIM_METADATA = 1       # 00001
LOG_ORGANOID_SETUP = 2     # 00010 (NeuronGroups, SynapseGroups, Stimuli)
LOG_MONITOR_METADATA = 4   # 00100 (Information about monitors)
LOG_SPIKE_DATA = 8         # 01000
LOG_STATE_DATA = 16        # 10000
LOG_RATE_DATA = 32         # 100000
LOG_ALL_SETUP = LOG_SIM_METADATA | LOG_ORGANOID_SETUP | LOG_MONITOR_METADATA
LOG_ALL_RESULTS = LOG_SPIKE_DATA | LOG_STATE_DATA | LOG_RATE_DATA
LOG_EVERYTHING = LOG_ALL_SETUP | LOG_ALL_RESULTS


class PersistentSimulator(BaseSimulator):
    """
    A Simulator that logs simulation setup and results to an SQLite database.
    """
    def __init__(self, organoid: Organoid, db_path: str, mea: MEA = None, brian2_dt=None):
        """
        Initializes the PersistentSimulator.

        Parameters
        ----------
        organoid : Organoid
            The pyneurorg Organoid instance.
        db_path : str
            Path to the SQLite database file for logging.
        mea : MEA, optional
            An MEA instance.
        brian2_dt : Quantity, optional
            The default clock dt for the simulation.
        """
        super().__init__(organoid, mea, brian2_dt)
        
        self.db_path = db_path
        self.writer = None 
        self.current_sim_id = None
        self.current_organoid_db_id = None
        self.monitor_db_ids = {} 

    def _prepare_logging(self, sim_name_user=None, sim_notes=None):
        """Initializes SQLiteWriter and logs initial simulation metadata."""
        try:
            self.writer = SQLiteWriter(self.db_path)
            
            b2_ver = b2.__version__ if hasattr(b2, '__version__') else "Unknown"
            np_ver = np.__version__ if hasattr(np, '__version__') else "Unknown"

            self.current_sim_id = self.writer.log_simulation_metadata(
                sim_name=sim_name_user if sim_name_user else f"Sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sim_uuid=str(uuid.uuid4()),
                notes=sim_notes,
                brian2_dt=self.brian_dt, 
                pyneurorg_version=pyneurorg_version,
                brian2_version=b2_ver,
                numpy_version=np_ver
            )
            if self.current_sim_id is None:
                raise ConnectionError("Failed to log simulation metadata and get sim_id.")
            
            print(f"PersistentSimulator: Logging to DB. Sim ID: {self.current_sim_id}")
            return True
        except Exception as e:
            print(f"Error preparing logging: {e}")
            traceback.print_exc()
            self.current_sim_id = None
            if self.writer:
                self.writer.close()
                self.writer = None
            return False

    def _log_organoid_setup(self):
        """Logs the organoid structure (neuron groups, synapses, stimuli)."""
        if not self.writer or self.current_sim_id is None:
            print("Warning: SQLiteWriter not initialized or no sim_id. Skipping organoid setup logging.")
            return

        self.current_organoid_db_id = self.writer.log_organoid_details(
            sim_id=self.current_sim_id,
            organoid_name=self.organoid.name,
            creation_params={} 
        )
        if self.current_organoid_db_id is None:
            print("Warning: Failed to log organoid details.")
            return

        for ng_name, ng_obj in self.organoid.neuron_groups.items():
            positions_array = self.organoid.get_positions(ng_name)
            positions_json = self.writer._serialize_params({'positions_um': positions_array / b2.um})

            self.writer.log_neuron_group(
                organoid_id=self.current_organoid_db_id,
                ng_name_pyneurorg=ng_name,
                ng_name_brian2=ng_obj.name,
                num_neurons=len(ng_obj),
                neuron_model_pyneurorg=getattr(ng_obj, '_pyneurorg_model_name', 'Unknown'),
                model_params_json=self.writer._serialize_params(getattr(ng_obj, '_pyneurorg_model_params', {})),
                spatial_distribution_func=getattr(ng_obj, '_pyneurorg_spatial_func', None),
                spatial_params_json=self.writer._serialize_params(getattr(ng_obj, '_pyneurorg_spatial_params', {})),
                positions_json=positions_json # Pass the serialized positions
            )
            
        for sg_name, sg_obj in self.organoid.synapses.items():
            self.writer.log_synapse_group(
                organoid_id=self.current_organoid_db_id,
                sg_name_pyneurorg=sg_name,
                sg_name_brian2=sg_obj.name,
                pre_ng_name=sg_obj.source.name, 
                post_ng_name=sg_obj.target.name, 
                synapse_model_pyneurorg=getattr(sg_obj, '_pyneurorg_model_name', 'Unknown'),
                model_params_json=self.writer._serialize_params(getattr(sg_obj, '_pyneurorg_model_params', {})),
                connect_rule_desc=str(getattr(sg_obj, '_pyneurorg_connect_rule', 'N/A')),
                num_synapses=len(sg_obj)
            )
        
        # Log stimuli configurations that were stored by the base Simulator's add_stimulus methods
        if hasattr(self, '_applied_stimuli_configs') and self._applied_stimuli_configs:
            for stim_config in self._applied_stimuli_configs:
                # Prepare stimulus_params_json - currently a placeholder in base simulator
                # If add_stimulus stored actual generator params, they would be here
                stim_params_to_log = stim_config.get("stimulus_params_json", {})
                
                # Ensure influence_radius is handled for serialization (value and unit)
                # The writer's log_stimulus_applied will handle Quantity object
                radius_val = stim_config.get("influence_radius")

                self.writer.log_stimulus_applied(
                    sim_id=self.current_sim_id, 
                    mea_electrode_id=stim_config.get("mea_electrode_id"),
                    target_group_name=stim_config.get("target_group_name_pyneurorg"),
                    stimulus_type=stim_config.get("stimulus_type"),
                    waveform_name=stim_config.get("waveform_name"),
                    cumulative_var_name=stim_config.get("cumulative_var_name"),
                    flag_template=stim_config.get("flag_template"),
                    influence_radius=radius_val, # Pass as is, writer will extract parts
                    stimulus_params_json=self.writer._serialize_params(stim_params_to_log)
                    # Add area_variable_name if it's part of stim_config for density stimuli
                )

    def _log_monitor_metadata(self):
        """Logs metadata for all configured monitors."""
        if not self.writer or self.current_sim_id is None:
            print("Warning: SQLiteWriter not initialized or no sim_id. Skipping monitor metadata logging.")
            return

        for monitor_key, monitor_obj in self.monitors.items():
            # Try to get the pyneurorg name of the target. If source is a group, it has a .name
            # If source was just passed as a string (not typical for monitors), this might need adjustment.
            target_name = monitor_obj.source.name if hasattr(monitor_obj.source, 'name') else 'UnknownTarget'
            monitor_type = type(monitor_obj).__name__
            
            record_details = {}
            if isinstance(monitor_obj, b2.StateMonitor):
                record_details['variables'] = list(monitor_obj.variables.keys())
                if isinstance(monitor_obj.record, (list, np.ndarray)):
                    record_details['record_indices'] = np.asarray(monitor_obj.record).tolist()
                elif monitor_obj.record is not True: 
                    record_details['record_repr'] = repr(monitor_obj.record)
            elif isinstance(monitor_obj, b2.SpikeMonitor):
                if isinstance(monitor_obj.record, (list, np.ndarray)):
                     record_details['record_indices'] = np.asarray(monitor_obj.record).tolist()
                elif monitor_obj.record is not True:
                     record_details['record_repr'] = repr(monitor_obj.record)
            
            monitor_db_id = self.writer.log_monitor_metadata(
                sim_id=self.current_sim_id,
                monitor_name_pyneurorg=monitor_key,
                monitor_name_brian2=monitor_obj.name,
                monitor_type=monitor_type,
                target_name_pyneurorg=target_name, 
                record_details_json=self.writer._serialize_params(record_details)
            )
            if monitor_db_id:
                self.monitor_db_ids[monitor_key] = monitor_db_id
            else:
                print(f"Warning: Failed to log metadata for monitor '{monitor_key}'.")

    def _log_monitor_data(self):
        """Logs data from all configured monitors."""
        if not self.writer or self.current_sim_id is None:
            print("Warning: SQLiteWriter not initialized or no sim_id. Skipping monitor data logging.")
            return

        for monitor_key, monitor_obj in self.monitors.items():
            monitor_db_id = self.monitor_db_ids.get(monitor_key)
            if not monitor_db_id:
                print(f"Warning: No DB ID found for monitor '{monitor_key}'. Skipping data log.")
                continue

            print(f"Logging data for monitor: {monitor_key} (DB ID: {monitor_db_id})")
            try:
                if isinstance(monitor_obj, b2.SpikeMonitor):
                    self.writer.log_spike_data(monitor_db_id, monitor_obj)
                elif isinstance(monitor_obj, b2.StateMonitor):
                    self.writer.log_state_data(monitor_db_id, monitor_obj)
                elif isinstance(monitor_obj, b2.PopulationRateMonitor):
                    self.writer.log_population_rate_data(monitor_db_id, monitor_obj)
                else:
                    print(f"Warning: Unknown monitor type for '{monitor_key}'. Cannot log data.")
            except Exception as e_log_data:
                 print(f"Error logging data for monitor '{monitor_key}': {e_log_data}")
                 traceback.print_exc()


    def run(self, duration: b2.Quantity, 
            log_options: int = LOG_EVERYTHING, 
            sim_name: str = None, 
            sim_notes: str = None,
            report=None, report_period=10*b2.second, **run_kwargs):
        """
        Builds the network and runs the simulation, with integrated logging.
        (Docstring como antes)
        """
        logging_prepared = False
        if log_options != LOG_NOTHING:
            logging_prepared = self._prepare_logging(sim_name_user=sim_name, sim_notes=sim_notes)
            if not logging_prepared:
                print("Critical: Logging preparation failed. Simulation run will proceed without logging.")
                # Decide if to abort or just warn:
                # raise ConnectionError("Logging preparation failed, aborting run.")

        try:
            if logging_prepared and (log_options & LOG_ORGANOID_SETUP):
                print("PersistentSimulator: Logging organoid setup...")
                self._log_organoid_setup()
            
            if logging_prepared and (log_options & LOG_MONITOR_METADATA):
                print("PersistentSimulator: Logging monitor metadata...")
                self._log_monitor_metadata()

            # Call the base class's run method
            super().run(duration, report=report, report_period=report_period, **run_kwargs)
            # print("PersistentSimulator: Brian2 simulation run (from BaseSimulator.run) finished.")

            if logging_prepared and self.current_sim_id:
                self.writer.update_simulation_timestamp_end(self.current_sim_id)
                dur_val, dur_unit = self.writer._get_brian2_quantity_parts(duration)
                if self.writer.cursor: # Check if writer is still active
                    update_sql = "UPDATE Simulations SET duration_run_value = ?, duration_run_unit = ? WHERE sim_id = ?"
                    self.writer.cursor.execute(update_sql, (dur_val, dur_unit, self.current_sim_id))
                    self.writer.conn.commit()

            if logging_prepared and (log_options & LOG_ALL_RESULTS):
                print("PersistentSimulator: Logging monitor results...")
                self._log_monitor_data()

        except Exception as e:
            print(f"Error during PersistentSimulator.run: {e}")
            traceback.print_exc()
        finally:
            if self.writer:
                self.writer.close()
                self.writer = None
            # Reset for next potential run (current_sim_id should ideally be set per run)
            # self.current_sim_id = None 
            # self.current_organoid_db_id = None
            # self.monitor_db_ids = {}
            print("PersistentSimulator: Run method finished. Logging session (if any) concluded.")
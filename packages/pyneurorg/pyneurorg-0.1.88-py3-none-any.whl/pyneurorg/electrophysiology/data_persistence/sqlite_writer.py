# src/pyneurorg/electrophysiology/data_persistence/sqlite_writer.py

import sqlite3
import json
import uuid
from datetime import datetime
import numpy as np
import brian2 as b2

from . import db_schema # Importa as strings CREATE TABLE
from brian2.units.fundamentalunits import DIMENSIONLESS # Para _get_brian2_quantity_parts


class SQLiteWriter:
    """
    Handles writing pyneurorg simulation data to an SQLite database.
    """
    def __init__(self, db_path: str):
        """
        Initializes the SQLiteWriter and connects to the database.
        Creates tables if they don't exist.

        Parameters
        ----------
        db_path : str
            Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database {self.db_path}: {e}")
            raise

    def _create_tables(self):
        """Creates all defined tables in the database if they do not already exist."""
        if not self.conn:
            print("Error: No database connection established.")
            return
        try:
            for table_sql in db_schema.ALL_TABLES:
                self.cursor.execute(table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            raise

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # --- Helper methods for data conversion ---
    def _serialize_params(self, params_dict):
        """Serializes a dictionary of parameters to JSON, handling Brian2 Quantities."""
        if params_dict is None:
            return None
        serializable_params = {}
        for key, value in params_dict.items():
            if isinstance(value, b2.Quantity):
                if hasattr(value, 'size') and value.size > 1 and not isinstance(value.item(), (int, float, bool)): # Array Quantity
                    serializable_params[key] = {
                        'value_array': np.asarray(value / value.unit).tolist(), # Store as list of numbers
                        'unit': str(value.unit)
                    }
                else: # Scalar Quantity
                    serializable_params[key] = {'value': float(value), 'unit': str(value.unit)}
            elif isinstance(value, (np.ndarray, list, tuple)):
                try:
                    serializable_params[key] = np.asarray(value).tolist() # Store as JSON list
                except TypeError:
                    serializable_params[key] = str(value)
            elif isinstance(value, (int, float, str, bool, type(None))):
                serializable_params[key] = value
            else:
                serializable_params[key] = str(value)
        return json.dumps(serializable_params)

    def _get_brian2_quantity_parts(self, quantity_obj):
        """Returns value and unit string from a Brian2 Quantity or number."""
        if isinstance(quantity_obj, b2.Quantity):
            return float(quantity_obj / quantity_obj.unit), str(quantity_obj.unit)
        elif isinstance(quantity_obj, (int, float)):
            return float(quantity_obj), "1" # Assume dimensionless
        return None, None
        
    # --- Logging methods ---

    def log_simulation_metadata(self, sim_name=None, sim_uuid=None, notes=None, 
                                brian2_dt=None, duration_run=None, 
                                pyneurorg_version=None, brian2_version=None, numpy_version=None):
        """Logs metadata about the simulation run. Returns the sim_id."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        sim_ts_start = datetime.now().isoformat()
        current_uuid = sim_uuid if sim_uuid else str(uuid.uuid4())
        b2_dt_val, b2_dt_unit = self._get_brian2_quantity_parts(brian2_dt)
        run_dur_val, run_dur_unit = self._get_brian2_quantity_parts(duration_run)

        sql = db_schema.CREATE_SIMULATIONS_TABLE.split("(",1)[0].replace("IF NOT EXISTS", "") # Hack to get "INSERT INTO Simulations"
        sql = sql.replace("CREATE TABLE", "INSERT INTO") + """
              (sim_uuid, sim_name, sim_timestamp_start, brian2_dt_value, brian2_dt_unit,
               duration_run_value, duration_run_unit, pyneurorg_version, brian2_version, 
               numpy_version, notes)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            self.cursor.execute(sql, (current_uuid, sim_name, sim_ts_start,
                                      b2_dt_val, b2_dt_unit,
                                      run_dur_val, run_dur_unit,
                                      pyneurorg_version, brian2_version, numpy_version, notes))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging simulation metadata: {e}")
            self.conn.rollback()
            return None

    def update_simulation_timestamp_end(self, sim_id):
        """Updates the simulation end timestamp."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        sim_ts_end = datetime.now().isoformat()
        sql = "UPDATE Simulations SET sim_timestamp_end = ? WHERE sim_id = ?"
        try:
            self.cursor.execute(sql, (sim_ts_end, sim_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating simulation end timestamp: {e}")
            self.conn.rollback()

    def log_organoid_details(self, sim_id, organoid_name, creation_params=None):
        """Logs details of the organoid. Returns the organoid_id."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        params_json = self._serialize_params(creation_params)
        sql = "INSERT INTO Organoids (sim_id, organoid_name, creation_params_json) VALUES (?, ?, ?)"
        try:
            self.cursor.execute(sql, (sim_id, organoid_name, params_json))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging organoid details: {e}")
            self.conn.rollback()
            return None

    def log_neuron_group(self, organoid_id, ng_name_pyneurorg, ng_name_brian2,
                         num_neurons, neuron_model_pyneurorg, model_params_json,
                         spatial_distribution_func=None, spatial_params_json=None,
                         positions_json=None): # Added positions_json
        """Logs details of a neuron group. Returns the ng_id."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        # We'll add a positions_json column to the table if we decide to store it this way.
        # For now, let's assume the schema might be updated or it's part of model_params_json for simplicity.
        # For the CREATE_NEURON_GROUPS_TABLE, we could add:
        # positions_json TEXT, -- JSON blob of Nx3 position array (um)
        sql = """
        INSERT INTO NeuronGroups 
            (organoid_id, ng_name_pyneurorg, ng_name_brian2, num_neurons, 
             neuron_model_pyneurorg, model_params_json, 
             spatial_distribution_func, spatial_params_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
        """ # positions_json would be another ? if added
        try:
            self.cursor.execute(sql, (organoid_id, ng_name_pyneurorg, ng_name_brian2,
                                      num_neurons, neuron_model_pyneurorg, model_params_json,
                                      spatial_distribution_func, spatial_params_json))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging neuron group '{ng_name_pyneurorg}': {e}")
            self.conn.rollback()
            return None

    def log_synapse_group(self, organoid_id, sg_name_pyneurorg, sg_name_brian2,
                          pre_ng_name, post_ng_name, synapse_model_pyneurorg,
                          model_params_json, connect_rule_desc, num_synapses):
        """Logs details of a synapse group. Returns the sg_id."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        sql = """
        INSERT INTO SynapseGroups
            (organoid_id, sg_name_pyneurorg, sg_name_brian2, pre_ng_name_pyneurorg, 
             post_ng_name_pyneurorg, synapse_model_pyneurorg, model_params_json, 
             connect_rule_description, num_synapses_created)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(sql, (organoid_id, sg_name_pyneurorg, sg_name_brian2,
                                      pre_ng_name, post_ng_name, synapse_model_pyneurorg,
                                      model_params_json, connect_rule_desc, num_synapses))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging synapse group '{sg_name_pyneurorg}': {e}")
            self.conn.rollback()
            return None

    def log_stimulus_applied(self, sim_id, target_group_name, stimulus_type,
                             waveform_name=None, cumulative_var_name=None, flag_template=None,
                             mea_electrode_id=None, influence_radius=None, stimulus_params_json=None):
        """Logs details of an applied stimulus. Returns the stim_record_id."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        
        radius_val, radius_unit = self._get_brian2_quantity_parts(influence_radius)

        sql = """
        INSERT INTO StimuliApplied
            (sim_id, mea_electrode_id, target_group_name_pyneurorg, stimulus_type,
             waveform_name, cumulative_var_name, flag_template, 
             influence_radius_value, influence_radius_unit, stimulus_params_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(sql, (sim_id, mea_electrode_id, target_group_name, stimulus_type,
                                      waveform_name, cumulative_var_name, flag_template,
                                      radius_val, radius_unit, stimulus_params_json))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging stimulus applied to '{target_group_name}': {e}")
            self.conn.rollback()
            return None

    def log_monitor_metadata(self, sim_id, monitor_name_pyneurorg, monitor_name_brian2,
                             monitor_type, target_name_pyneurorg, record_details_json=None):
        """Logs metadata for a monitor. Returns the monitor_db_id."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        sql = """
        INSERT INTO Monitors
            (sim_id, monitor_name_pyneurorg, monitor_name_brian2, 
             monitor_type, target_name_pyneurorg, record_details_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(sql, (sim_id, monitor_name_pyneurorg, monitor_name_brian2,
                                      monitor_type, target_name_pyneurorg, record_details_json))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging monitor metadata for '{monitor_name_pyneurorg}': {e}")
            self.conn.rollback()
            return None

    def log_spike_data(self, monitor_db_id, spike_monitor: b2.SpikeMonitor):
        """Logs all spike data from a Brian2 SpikeMonitor."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        if not len(spike_monitor.i): # No spikes
            return

        spike_time_val, spike_time_unit = self._get_brian2_quantity_parts(spike_monitor.t[0]) # Get unit from first spike
        if spike_time_unit is None: spike_time_unit = "s" # Default if somehow unitless

        # Convert all spike times to their numerical value in the determined unit
        # spike_monitor.t is a Quantity if spikes occurred, otherwise might be empty list/array
        if isinstance(spike_monitor.t, b2.Quantity):
            all_spike_times_numeric = np.asarray(spike_monitor.t / b2.Unit(spike_time_unit))
        else: # Handle empty case or if t is already numeric (less likely for brian monitor)
            all_spike_times_numeric = np.asarray(spike_monitor.t)


        spikes_to_insert = []
        for i in range(len(spike_monitor.i)):
            neuron_idx = int(spike_monitor.i[i])
            time_val = float(all_spike_times_numeric[i])
            spikes_to_insert.append((monitor_db_id, neuron_idx, time_val, spike_time_unit))

        sql = "INSERT INTO SpikeData (monitor_db_id, neuron_index, spike_time_value, spike_time_unit) VALUES (?, ?, ?, ?)"
        try:
            self.cursor.executemany(sql, spikes_to_insert)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging spike data for monitor_db_id {monitor_db_id}: {e}")
            self.conn.rollback()

    def log_state_data(self, monitor_db_id, state_monitor: b2.StateMonitor):
        """Logs all state data from a Brian2 StateMonitor."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        
        recorded_vars = list(state_monitor.variables.keys())
        if not recorded_vars or not hasattr(state_monitor, 't') or not len(state_monitor.t):
            print(f"Warning: No variables or no time points recorded for monitor_db_id {monitor_db_id}.")
            return

        time_val_numeric, time_unit = self._get_brian2_quantity_parts(state_monitor.t[0])
        if time_unit is None: time_unit = "s"
            
        all_times_numeric = np.asarray(state_monitor.t / b2.Unit(time_unit))

        states_to_insert = []
        # state_monitor.record contains the indices of neurons that were actually recorded
        # If True, it's 0 to N-1. If a list/array, it's those specific indices.
        recorded_neuron_indices_in_group = state_monitor.record
        if recorded_neuron_indices_in_group is True: # Recorded all neurons
            num_recorded_neurons = getattr(state_monitor.source, 'N', 0)
            if num_recorded_neurons == 0 and hasattr(state_monitor, recorded_vars[0]): # try to infer from data shape
                num_recorded_neurons = getattr(state_monitor, recorded_vars[0]).shape[0]
            recorded_neuron_indices_in_group = np.arange(num_recorded_neurons)


        for var_name in recorded_vars:
            if not hasattr(state_monitor, var_name):
                print(f"Warning: Variable '{var_name}' not found in StateMonitor data for monitor_db_id {monitor_db_id}.")
                continue
            
            var_data_view = getattr(state_monitor, var_name) # This is a VariableView
            
            # Determine unit of the variable
            var_unit_str = "1" # Default for dimensionless
            if isinstance(var_data_view, b2.Quantity) and not var_data_view.is_dimensionless:
                var_unit_str = str(var_data_view.unit)
                var_data_numeric = np.asarray(var_data_view / var_data_view.unit)
            elif isinstance(var_data_view, b2.Quantity) and var_data_view.is_dimensionless:
                var_data_numeric = np.asarray(var_data_view / b2.Quantity(1, dim=DIMENSIONLESS))
            else: # Assume it's already a plain numpy array (e.g. for boolean flags)
                var_data_numeric = np.asarray(var_data_view)


            # var_data_numeric should be (num_recorded_neurons, num_time_steps)
            if var_data_numeric.ndim == 2:
                for i, neuron_original_idx in enumerate(recorded_neuron_indices_in_group):
                    for t_idx, t_val in enumerate(all_times_numeric):
                        value_real = None
                        value_text = None
                        if isinstance(var_data_numeric[i, t_idx], (np.bool_, bool)):
                             value_text = str(var_data_numeric[i, t_idx])
                        else:
                             value_real = float(var_data_numeric[i, t_idx])

                        states_to_insert.append((monitor_db_id, t_idx, t_val, time_unit,
                                                 int(neuron_original_idx), var_name,
                                                 value_real, value_text, var_unit_str))
            elif var_data_numeric.ndim == 1 and len(recorded_neuron_indices_in_group) == 1 : # Single neuron recorded
                neuron_original_idx = recorded_neuron_indices_in_group[0]
                for t_idx, t_val in enumerate(all_times_numeric):
                    value_real = None
                    value_text = None
                    if isinstance(var_data_numeric[t_idx], (np.bool_, bool)):
                         value_text = str(var_data_numeric[t_idx])
                    else:
                         value_real = float(var_data_numeric[t_idx])
                    states_to_insert.append((monitor_db_id, t_idx, t_val, time_unit,
                                             int(neuron_original_idx), var_name,
                                             value_real, value_text, var_unit_str))
            else:
                print(f"Warning: Unexpected data shape for variable '{var_name}' in monitor_db_id {monitor_db_id}. Shape: {var_data_numeric.shape}")


        sql = """
        INSERT INTO StateData 
            (monitor_db_id, time_step_index, time_value, time_unit, neuron_index, 
             variable_name, variable_value_real, variable_value_text, variable_unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            if states_to_insert: # Only execute if there's data
                self.cursor.executemany(sql, states_to_insert)
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging state data for monitor_db_id {monitor_db_id}: {e}")
            self.conn.rollback()

    def log_population_rate_data(self, monitor_db_id, rate_monitor: b2.PopulationRateMonitor):
        """Logs data from a PopulationRateMonitor."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        if not hasattr(rate_monitor, 't') or not len(rate_monitor.t):
            return

        time_val_numeric, time_unit = self._get_brian2_quantity_parts(rate_monitor.t[0])
        if time_unit is None: time_unit = "s"
        all_times_numeric = np.asarray(rate_monitor.t / b2.Unit(time_unit))

        rate_val_numeric, rate_unit = self._get_brian2_quantity_parts(rate_monitor.rate[0])
        if rate_unit is None: rate_unit = "Hz"
        all_rates_numeric = np.asarray(rate_monitor.rate / b2.Unit(rate_unit))
            
        rates_to_insert = []
        for i in range(len(all_times_numeric)):
            rates_to_insert.append((monitor_db_id, float(all_times_numeric[i]), time_unit,
                                    float(all_rates_numeric[i]), rate_unit))
        
        sql = """
        INSERT INTO PopulationRateData 
            (monitor_db_id, time_value, time_unit, rate_value, rate_unit)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            self.cursor.executemany(sql, rates_to_insert)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging population rate data for monitor_db_id {monitor_db_id}: {e}")
            self.conn.rollback()

if __name__ == '__main__':
    db_file = "test_pyneurorg_writer.db"
    import os
    if os.path.exists(db_file):
        os.remove(db_file) 

    try:
        with SQLiteWriter(db_file) as writer:
            print(f"Database '{db_file}' initialized.")
            sim_id = writer.log_simulation_metadata(sim_name="FullWriterTest")
            print(f"Sim ID: {sim_id}")
            if sim_id:
                org_id = writer.log_organoid_details(sim_id, "TestOrganoid")
                print(f"Org ID: {org_id}")
                if org_id:
                    ng_id = writer.log_neuron_group(
                        organoid_id=org_id,
                        ng_name_pyneurorg="Excitatory",
                        ng_name_brian2="Excitatory_0",
                        num_neurons=10,
                        neuron_model_pyneurorg="LIFNeuron",
                        model_params_json=writer._serialize_params({'tau_m': 20*b2.ms, 'v_thresh': -50*b2.mV}),
                        spatial_distribution_func="random_positions_in_cube",
                        spatial_params_json=writer._serialize_params({'side_length': 100*b2.um})
                    )
                    print(f"NG ID: {ng_id}")

                    sg_id = writer.log_synapse_group(
                        organoid_id=org_id,
                        sg_name_pyneurorg="ExcToExc",
                        sg_name_brian2="ExcToExc_0",
                        pre_ng_name="Excitatory",
                        post_ng_name="Excitatory",
                        synapse_model_pyneurorg="StaticConductionSynapse",
                        model_params_json=writer._serialize_params({'target_conductance_var': 'g_exc'}),
                        connect_rule_desc="p=0.1",
                        num_synapses=5 # Example
                    )
                    print(f"SG ID: {sg_id}")
                
                stim_rec_id = writer.log_stimulus_applied(
                    sim_id=sim_id,
                    target_group_name="Excitatory",
                    stimulus_type="current",
                    waveform_name="step_current_0",
                    cumulative_var_name="I_stimulus_sum"
                )
                print(f"Stim Record ID: {stim_rec_id}")

                # Mock Brian2 Monitors for testing
                class MockMonitor:
                    def __init__(self, name, source_name, rec_details=None):
                        self.name = name # Brian2 internal name
                        self.source = type('Source', (), {'name': source_name})()
                        self.variables = {}
                        self.record = True # Default for spike/poprate, or all neurons for state
                        if rec_details and 'variables' in rec_details:
                            for v in rec_details['variables']:
                                self.variables[v] = None # Placeholder
                        if rec_details and 'record' in rec_details:
                             self.record = rec_details['record']


                mock_spike_mon = MockMonitor("brian2_spike_0", "Excitatory")
                mock_spike_mon.i = np.array([0, 1, 0, 2, 1])
                mock_spike_mon.t = np.array([10, 12, 20, 22, 30]) * b2.ms
                
                mon_spike_db_id = writer.log_monitor_metadata(sim_id, "user_spike_monitor", mock_spike_mon.name, 
                                                            "SpikeMonitor", mock_spike_mon.source.name)
                if mon_spike_db_id:
                    print(f"Spike Monitor DB ID: {mon_spike_db_id}")
                    writer.log_spike_data(mon_spike_db_id, mock_spike_mon)
                    print("Logged spike data.")

                mock_state_mon = MockMonitor("brian2_state_0", "Excitatory", 
                                             rec_details={'variables': ['v', 'is_active'], 'record': [0,1]}) # Record neuron 0 and 1
                mock_state_mon.t = np.array([0, 1, 2]) * b2.ms
                mock_state_mon.v = np.array([[-70, -65, -60], [-70, -68, -62]]) * b2.mV # (2 neurons, 3 time steps)
                mock_state_mon.is_active = np.array([[False, True, True], [False, False, True]]) # Example boolean
                mock_state_mon.variables = {'v': None, 'is_active': None} # To mimic structure


                mon_state_db_id = writer.log_monitor_metadata(sim_id, "user_state_monitor", mock_state_mon.name,
                                                             "StateMonitor", mock_state_mon.source.name,
                                                             record_details_json=json.dumps({'variables': ['v', 'is_active'], 'record': [0,1]}))
                if mon_state_db_id:
                    print(f"State Monitor DB ID: {mon_state_db_id}")
                    writer.log_state_data(mon_state_db_id, mock_state_mon)
                    print("Logged state data.")

                mock_pop_rate_mon = MockMonitor("brian2_poprate_0", "Excitatory")
                mock_pop_rate_mon.t = np.array([0, 50, 100]) * b2.ms
                mock_pop_rate_mon.rate = np.array([0, 10, 5]) * b2.Hz

                mon_pop_db_id = writer.log_monitor_metadata(sim_id, "user_pop_rate_monitor", mock_pop_rate_mon.name,
                                                           "PopulationRateMonitor", mock_pop_rate_mon.source.name)
                if mon_pop_db_id:
                    print(f"PopRate Monitor DB ID: {mon_pop_db_id}")
                    writer.log_population_rate_data(mon_pop_db_id, mock_pop_rate_mon)
                    print("Logged population rate data.")

                writer.update_simulation_timestamp_end(sim_id)


    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    # finally:
    #     if os.path.exists(db_file) and __name__ == '__main__':
    #         os.remove(db_file)
    #         print(f"Cleaned up test database: {db_file}")
# src/pyneurorg/electrophysiology/data_persistence/sqlite_reader.py

import sqlite3
import json
import numpy as np
import brian2 as b2
from brian2.units.fundamentalunits import DIMENSIONLESS

class SQLiteReader:
    """
    Handles reading pyneurorg simulation data from an SQLite database.
    """
    def __init__(self, db_path: str):
        """
        Initializes the SQLiteReader and connects to the database.

        Parameters
        ----------
        db_path : str
            Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row # Access columns by name
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database {self.db_path}: {e}")
            raise

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # --- Helper methods for data deserialization ---
    def _deserialize_params(self, params_json_str):
        """Deserializes a JSON string of parameters back into a dict, converting units if possible."""
        if params_json_str is None:
            return {}
        try:
            params_dict = json.loads(params_json_str)
        except json.JSONDecodeError:
            # print(f"Warning: Could not decode JSON: {params_json_str}")
            return {"raw_json_string": params_json_str} # Return raw if not valid JSON

        deserialized_params = {}
        for key, value in params_dict.items():
            if isinstance(value, dict) and 'value' in value and 'unit' in value:
                try:
                    # Attempt to reconstruct Brian2 Quantity
                    unit_str = value['unit']
                    if unit_str == "1": # Dimensionless
                        deserialized_params[key] = b2.Quantity(value['value'], dim=DIMENSIONLESS)
                    else:
                        # Brian2 can often parse unit strings directly
                        deserialized_params[key] = value['value'] * getattr(b2, unit_str.split(" ")[-1], b2.Unit(1, dim=DIMENSIONLESS))
                        # A more robust way to parse units:
                        # unit_obj = b2.Unit.from_string(unit_str)
                        # deserialized_params[key] = value['value'] * unit_obj
                except (AttributeError, TypeError, ValueError) as e:
                    # print(f"Warning: Could not reconstruct Quantity for {key}: {value}. Error: {e}")
                    deserialized_params[key] = value # Keep as dict if reconstruction fails
            elif isinstance(value, dict) and 'value_array' in value and 'unit' in value: # Array Quantity
                 try:
                    unit_str = value['unit']
                    if unit_str == "1":
                        deserialized_params[key] = np.array(value['value_array']) * b2.Quantity(1, dim=DIMENSIONLESS)
                    else:
                        deserialized_params[key] = np.array(value['value_array']) * getattr(b2, unit_str.split(" ")[-1], b2.Unit(1, dim=DIMENSIONLESS))
                 except Exception as e:
                    # print(f"Warning: Could not reconstruct array Quantity for {key}: {value}. Error: {e}")
                    deserialized_params[key] = value
            elif isinstance(value, str): # Potentially a nested JSON string for lists/arrays
                try:
                    # Try to parse if it was a simple list stored as JSON string
                    parsed_list = json.loads(value)
                    if isinstance(parsed_list, list):
                        deserialized_params[key] = parsed_list
                    else:
                        deserialized_params[key] = value # Not a list, keep as string
                except json.JSONDecodeError:
                    deserialized_params[key] = value # Not a JSON string, keep as is
            else:
                deserialized_params[key] = value
        return deserialized_params

    def _get_quantity_from_parts(self, value, unit_str):
        """Reconstructs a Brian2 Quantity from value and unit string."""
        if value is None or unit_str is None:
            return None
        try:
            if unit_str == "1" or unit_str == "" or unit_str.lower() == "dimensionless":
                return b2.Quantity(value, dim=DIMENSIONLESS)
            else:
                # Attempt to parse common units directly or use b2.Unit.from_string
                # Split in case unit string has "N m" format
                base_unit_str = unit_str.split(" ")[-1]
                if hasattr(b2, base_unit_str):
                    return value * getattr(b2, base_unit_str)
                else:
                    return value * b2.Unit.from_string(unit_str) # More robust
        except Exception as e:
            # print(f"Warning: Could not reconstruct Quantity from value '{value}' and unit '{unit_str}'. Error: {e}")
            return f"{value} {unit_str}" # Fallback to string

    # --- Fetching methods ---

    def get_simulations(self, sim_id=None, sim_uuid=None):
        """Fetches simulation metadata. Returns a list of dicts."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        query = "SELECT * FROM Simulations"
        params = []
        if sim_id:
            query += " WHERE sim_id = ?"
            params.append(sim_id)
        elif sim_uuid:
            query += " WHERE sim_uuid = ?"
            params.append(sim_uuid)
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        sim_list = []
        for row in rows:
            sim_dict = dict(row)
            sim_dict['brian2_dt'] = self._get_quantity_from_parts(row['brian2_dt_value'], row['brian2_dt_unit'])
            sim_dict['duration_run'] = self._get_quantity_from_parts(row['duration_run_value'], row['duration_run_unit'])
            sim_list.append(sim_dict)
        return sim_list

    def get_organoid_details(self, sim_id):
        """Fetches organoid details for a given sim_id. Returns a dict or None."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        self.cursor.execute("SELECT * FROM Organoids WHERE sim_id = ?", (sim_id,))
        row = self.cursor.fetchone()
        if row:
            org_dict = dict(row)
            org_dict['creation_params'] = self._deserialize_params(row['creation_params_json'])
            return org_dict
        return None

    def get_neuron_groups(self, organoid_id=None, sim_id=None):
        """Fetches neuron group details. Returns a list of dicts."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        if organoid_id is None and sim_id is not None:
            org_details = self.get_organoid_details(sim_id)
            if not org_details: return []
            organoid_id = org_details['organoid_id']
        elif organoid_id is None and sim_id is None:
            raise ValueError("Either organoid_id or sim_id must be provided.")

        self.cursor.execute("SELECT * FROM NeuronGroups WHERE organoid_id = ?", (organoid_id,))
        rows = self.cursor.fetchall()
        ng_list = []
        for row in rows:
            ng_dict = dict(row)
            ng_dict['model_params'] = self._deserialize_params(row['model_params_json'])
            ng_dict['spatial_params'] = self._deserialize_params(row['spatial_params_json'])
            # If positions_json was added to schema:
            # ng_dict['positions'] = self._deserialize_params(row['positions_json']) # Would be list of lists
            ng_list.append(ng_dict)
        return ng_list

    def get_synapse_groups(self, organoid_id=None, sim_id=None):
        """Fetches synapse group details. Returns a list of dicts."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        if organoid_id is None and sim_id is not None:
            org_details = self.get_organoid_details(sim_id)
            if not org_details: return []
            organoid_id = org_details['organoid_id']
        elif organoid_id is None and sim_id is None:
            raise ValueError("Either organoid_id or sim_id must be provided.")
            
        self.cursor.execute("SELECT * FROM SynapseGroups WHERE organoid_id = ?", (organoid_id,))
        rows = self.cursor.fetchall()
        sg_list = []
        for row in rows:
            sg_dict = dict(row)
            sg_dict['model_params'] = self._deserialize_params(row['model_params_json'])
            sg_list.append(sg_dict)
        return sg_list

    def get_stimuli_applied(self, sim_id):
        """Fetches details of stimuli applied in a simulation. Returns a list of dicts."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        self.cursor.execute("SELECT * FROM StimuliApplied WHERE sim_id = ?", (sim_id,))
        rows = self.cursor.fetchall()
        stim_list = []
        for row in rows:
            stim_dict = dict(row)
            stim_dict['influence_radius'] = self._get_quantity_from_parts(row['influence_radius_value'], row['influence_radius_unit'])
            stim_dict['stimulus_params'] = self._deserialize_params(row['stimulus_params_json'])
            stim_list.append(stim_dict)
        return stim_list

    def get_monitors_metadata(self, sim_id):
        """Fetches metadata for all monitors in a simulation. Returns a list of dicts."""
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        self.cursor.execute("SELECT * FROM Monitors WHERE sim_id = ?", (sim_id,))
        rows = self.cursor.fetchall()
        mon_list = []
        for row in rows:
            mon_dict = dict(row)
            mon_dict['record_details'] = self._deserialize_params(row['record_details_json'])
            mon_list.append(mon_dict)
        return mon_list

    def get_spike_data(self, monitor_db_id=None, sim_id=None, monitor_name_pyneurorg=None):
        """
        Fetches spike data for a specific monitor.
        Returns a tuple (spike_indices_array, spike_times_quantity).
        """
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        if monitor_db_id is None:
            if sim_id and monitor_name_pyneurorg:
                self.cursor.execute("SELECT monitor_db_id FROM Monitors WHERE sim_id = ? AND monitor_name_pyneurorg = ?", 
                                    (sim_id, monitor_name_pyneurorg))
                row = self.cursor.fetchone()
                if not row: return np.array([]), np.array([]) * b2.second
                monitor_db_id = row['monitor_db_id']
            else:
                raise ValueError("Provide monitor_db_id, or sim_id and monitor_name_pyneurorg.")

        self.cursor.execute("SELECT neuron_index, spike_time_value, spike_time_unit FROM SpikeData WHERE monitor_db_id = ? ORDER BY spike_time_value", 
                            (monitor_db_id,))
        rows = self.cursor.fetchall()
        if not rows:
            return np.array([]), np.array([]) * b2.second # Return empty arrays with unit

        indices = np.array([r['neuron_index'] for r in rows], dtype=int)
        times_val = np.array([r['spike_time_value'] for r in rows], dtype=float)
        time_unit_str = rows[0]['spike_time_unit']
        
        time_unit_obj = b2.second # Default
        if hasattr(b2, time_unit_str): time_unit_obj = getattr(b2, time_unit_str)
        elif time_unit_str:
            try: time_unit_obj = b2.Unit.from_string(time_unit_str)
            except: print(f"Warning: Could not parse unit '{time_unit_str}' for spike times, defaulting to seconds.")

        return indices, times_val * time_unit_obj

    def get_state_data(self, monitor_db_id=None, sim_id=None, monitor_name_pyneurorg=None):
        """
        Fetches state data for a specific monitor.
        Returns a dictionary: 
        {
            't': time_quantity_array, 
            'variable_name1': data_quantity_array_var1 (neurons x time),
            'variable_name2': data_quantity_array_var2 (neurons x time),
            ...
            'recorded_neuron_indices': list_of_original_neuron_indices
        }
        """
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        
        actual_monitor_db_id = monitor_db_id
        if actual_monitor_db_id is None:
            if sim_id and monitor_name_pyneurorg:
                self.cursor.execute("SELECT monitor_db_id FROM Monitors WHERE sim_id = ? AND monitor_name_pyneurorg = ?", 
                                    (sim_id, monitor_name_pyneurorg))
                row = self.cursor.fetchone()
                if not row: return {'t': np.array([]) * b2.second} # Empty result
                actual_monitor_db_id = row['monitor_db_id']
            else:
                raise ValueError("Provide monitor_db_id, or sim_id and monitor_name_pyneurorg.")

        # Fetch all data for this monitor, ordered for easier reshaping
        sql = """
        SELECT time_step_index, time_value, time_unit, neuron_index, 
               variable_name, variable_value_real, variable_value_text, variable_unit 
        FROM StateData 
        WHERE monitor_db_id = ? 
        ORDER BY variable_name, neuron_index, time_step_index
        """
        self.cursor.execute(sql, (actual_monitor_db_id,))
        rows = self.cursor.fetchall()

        if not rows:
            return {'t': np.array([]) * b2.second} # Empty result

        # Process time array first
        time_unit_str = rows[0]['time_unit']
        time_unit_obj = b2.second
        if hasattr(b2, time_unit_str): time_unit_obj = getattr(b2, time_unit_str)
        elif time_unit_str: 
            try: time_unit_obj = b2.Unit.from_string(time_unit_str)
            except: pass # Default to s
            
        unique_times = sorted(list(set(r['time_value'] for r in rows)))
        t_array = np.array(unique_times) * time_unit_obj
        
        results = {'t': t_array}
        
        # Get unique recorded neuron indices (original indices in the group)
        recorded_neuron_indices = sorted(list(set(r['neuron_index'] for r in rows)))
        results['recorded_neuron_indices'] = recorded_neuron_indices
        
        # Map original neuron index to its index within the recorded data (0 to N_recorded-1)
        neuron_idx_map = {original_idx: i for i, original_idx in enumerate(recorded_neuron_indices)}

        current_var_name = None
        current_var_data_list = []

        for row_dict in rows:
            var_name = row_dict['variable_name']
            if var_name != current_var_name:
                # Finalize previous variable if any
                if current_var_name and current_var_data_list:
                    # Reshape: (num_recorded_neurons, num_time_steps)
                    data_array = np.array(current_var_data_list).reshape(len(recorded_neuron_indices), len(t_array))
                    var_unit_obj = self._get_quantity_from_parts(1, current_var_unit_str).unit # Get unit obj
                    results[current_var_name] = data_array * var_unit_obj
                
                current_var_name = var_name
                current_var_data_list = []
                current_var_unit_str = row_dict['variable_unit']

            # Append data point
            if row_dict['variable_value_real'] is not None:
                current_var_data_list.append(row_dict['variable_value_real'])
            elif row_dict['variable_value_text'] is not None: # For booleans etc.
                current_var_data_list.append(json.loads(row_dict['variable_value_text'].lower()) 
                                             if row_dict['variable_value_text'].lower() in ['true', 'false'] 
                                             else row_dict['variable_value_text'])
            else:
                current_var_data_list.append(np.nan) # Should not happen if schema is good

        # Finalize the last variable
        if current_var_name and current_var_data_list:
            data_array = np.array(current_var_data_list).reshape(len(recorded_neuron_indices), len(t_array))
            var_unit_obj = self._get_quantity_from_parts(1, current_var_unit_str).unit
            results[current_var_name] = data_array * var_unit_obj
            
        return results


    def get_population_rate_data(self, monitor_db_id=None, sim_id=None, monitor_name_pyneurorg=None):
        """
        Fetches population rate data.
        Returns a tuple (times_quantity_array, rates_quantity_array).
        """
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        if monitor_db_id is None:
            if sim_id and monitor_name_pyneurorg:
                self.cursor.execute("SELECT monitor_db_id FROM Monitors WHERE sim_id = ? AND monitor_name_pyneurorg = ?", 
                                    (sim_id, monitor_name_pyneurorg))
                row = self.cursor.fetchone()
                if not row: return np.array([]) * b2.second, np.array([]) * b2.Hz
                monitor_db_id = row['monitor_db_id']
            else:
                raise ValueError("Provide monitor_db_id, or sim_id and monitor_name_pyneurorg.")

        self.cursor.execute("SELECT time_value, time_unit, rate_value, rate_unit FROM PopulationRateData WHERE monitor_db_id = ? ORDER BY time_value", (monitor_db_id,))
        rows = self.cursor.fetchall()
        if not rows:
            return np.array([]) * b2.second, np.array([]) * b2.Hz

        times_val = np.array([r['time_value'] for r in rows], dtype=float)
        time_unit_str = rows[0]['time_unit']
        rates_val = np.array([r['rate_value'] for r in rows], dtype=float)
        rate_unit_str = rows[0]['rate_unit']

        time_unit_obj = b2.second
        if hasattr(b2, time_unit_str): time_unit_obj = getattr(b2, time_unit_str)
        elif time_unit_str: 
            try: time_unit_obj = b2.Unit.from_string(time_unit_str)
            except: pass
            
        rate_unit_obj = b2.Hz
        if hasattr(b2, rate_unit_str): rate_unit_obj = getattr(b2, rate_unit_str)
        elif rate_unit_str: 
            try: rate_unit_obj = b2.Unit.from_string(rate_unit_str)
            except: pass

        return times_val * time_unit_obj, rates_val * rate_unit_obj

if __name__ == '__main__':
    # Example Usage (assumes a database 'test_pyneurorg_writer.db' was created by SQLiteWriter example)
    db_file = "test_pyneurorg_writer.db" # Use the same DB file created by writer
    
    if not os.path.exists(db_file):
        print(f"Database file {db_file} not found. Run SQLiteWriter example first to create it.")
    else:
        try:
            with SQLiteReader(db_file) as reader:
                print(f"Connected to database: {db_file}")
                
                sims = reader.get_simulations()
                if sims:
                    print(f"\nFound {len(sims)} simulation(s):")
                    for sim_meta in sims:
                        print(f"  Sim ID: {sim_meta['sim_id']}, Name: {sim_meta['sim_name']}, UUID: {sim_meta['sim_uuid']}")
                        print(f"    Brian2 dt: {sim_meta['brian2_dt']}, Run duration: {sim_meta['duration_run']}")
                        
                        test_sim_id = sim_meta['sim_id'] # Use the first one found for further tests
                        
                        organoid = reader.get_organoid_details(test_sim_id)
                        if organoid:
                            print(f"\n  Organoid for Sim ID {test_sim_id}: {organoid['organoid_name']}")
                            print(f"    Creation Params: {organoid['creation_params']}")
                            
                            neuron_groups = reader.get_neuron_groups(organoid_id=organoid['organoid_id'])
                            print(f"    Neuron Groups ({len(neuron_groups)}):")
                            for ng in neuron_groups:
                                print(f"      - {ng['ng_name_pyneurorg']}: {ng['num_neurons']} neurons, Model: {ng['neuron_model_pyneurorg']}")
                                # print(f"        Params: {ng['model_params']}")


                            syn_groups = reader.get_synapse_groups(organoid_id=organoid['organoid_id'])
                            print(f"    Synapse Groups ({len(syn_groups)}):")
                            for sg in syn_groups:
                                print(f"      - {sg['sg_name_pyneurorg']}: {sg['num_synapses_created']} synapses, Model: {sg['synapse_model_pyneurorg']}")
                                # print(f"        Params: {sg['model_params']}")
                        
                        stimuli = reader.get_stimuli_applied(test_sim_id)
                        print(f"\n  Stimuli Applied ({len(stimuli)}):")
                        for stim in stimuli:
                            print(f"    - To: {stim['target_group_name_pyneurorg']}, Type: {stim['stimulus_type']}")

                        monitors = reader.get_monitors_metadata(test_sim_id)
                        print(f"\n  Monitors ({len(monitors)}):")
                        for mon in monitors:
                            print(f"    - {mon['monitor_name_pyneurorg']} (Type: {mon['monitor_type']}, Target: {mon['target_name_pyneurorg']})")
                            if mon['monitor_type'] == "SpikeMonitor":
                                indices, times = reader.get_spike_data(monitor_db_id=mon['monitor_db_id'])
                                print(f"      Spikes - Count: {len(indices)}, Example times: {times[:3] if len(times) > 0 else 'N/A'}")
                            elif mon['monitor_type'] == "StateMonitor":
                                state_data = reader.get_state_data(monitor_db_id=mon['monitor_db_id'])
                                print(f"      State Data - Time points: {len(state_data.get('t',[]))}, Vars: {list(state_data.keys() - {'t', 'recorded_neuron_indices'})}")
                                if 'v' in state_data and len(state_data['v']) > 0:
                                     print(f"        Example Vm (neuron 0): {state_data['v'][0,:3] if state_data['v'].ndim >1 and state_data['v'].shape[1]>0 else state_data['v'][:3]}")
                            elif mon['monitor_type'] == "PopulationRateMonitor":
                                times, rates = reader.get_population_rate_data(monitor_db_id=mon['monitor_db_id'])
                                print(f"      PopRate Data - Points: {len(times)}, Example rates: {rates[:3] if len(rates)>0 else 'N/A'}")
                        break # Only process the first simulation for this example
                else:
                    print("No simulations found in the database.")

        except Exception as e:
            print(f"An error occurred during SQLiteReader example usage: {e}")
            import traceback
            traceback.print_exc()
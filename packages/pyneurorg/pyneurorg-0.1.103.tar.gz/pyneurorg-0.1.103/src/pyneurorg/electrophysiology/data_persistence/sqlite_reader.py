# src/pyneurorg/electrophysiology/data_persistence/sqlite_reader.py

import sqlite3
import json
import numpy as np
import brian2 as b2
from brian2.units.fundamentalunits import DIMENSIONLESS

class SQLiteReader:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row 
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database {self.db_path}: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _reconstruct_brian2_quantity(self, value, unit_str):
        """
        Reconstructs a Brian2 Quantity from a numerical value and its unit string.
        Returns the Quantity, or the original value if unit_str is None or invalid.
        """
        if value is None or unit_str is None:
            return value # Or raise error, or return None
        try:
            if unit_str == "1" or unit_str == "" or unit_str.lower() == "dimensionless":
                return b2.Quantity(value, dim=DIMENSIONLESS)
            else:
                # Attempt to find the unit in brian2's namespace
                if hasattr(b2, unit_str):
                    return value * getattr(b2, unit_str)
                else: # Try to parse it as a string (e.g., "siemens", "uA/cm**2")
                    return value * b2.Unit.from_string(unit_str)
        except Exception as e: #pragma: no cover
            # print(f"Warning: Could not reconstruct Quantity from value '{value}' and unit '{unit_str}'. Error: {e}. Returning raw value.")
            return value # Fallback

    def _deserialize_params(self, params_json_str):
        if params_json_str is None:
            return {}
        try:
            params_dict = json.loads(params_json_str)
        except json.JSONDecodeError:
            return {"raw_json_string": params_json_str}

        deserialized_params = {}
        for key, value in params_dict.items():
            if isinstance(value, dict) and 'value' in value and 'unit' in value:
                deserialized_params[key] = self._reconstruct_brian2_quantity(value['value'], value['unit'])
            elif isinstance(value, dict) and 'value_array' in value and 'unit' in value:
                # For arrays, reconstruct the unit and then multiply the numpy array
                unit_obj = self._reconstruct_brian2_quantity(1.0, value['unit']).dimensions # Get the unit object
                deserialized_params[key] = np.array(value['value_array']) * unit_obj
            elif isinstance(value, str):
                try:
                    parsed_list = json.loads(value)
                    if isinstance(parsed_list, list): deserialized_params[key] = parsed_list
                    else: deserialized_params[key] = value
                except json.JSONDecodeError:
                    deserialized_params[key] = value
            else:
                deserialized_params[key] = value
        return deserialized_params

    def get_simulations(self, sim_id=None, sim_uuid=None):
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
            sim_dict['brian2_dt'] = self._reconstruct_brian2_quantity(row['brian2_dt_value'], row['brian2_dt_unit'])
            sim_dict['duration_run'] = self._reconstruct_brian2_quantity(row['duration_run_value'], row['duration_run_unit'])
            sim_list.append(sim_dict)
        return sim_list

    def get_organoid_details(self, sim_id):
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        self.cursor.execute("SELECT * FROM Organoids WHERE sim_id = ?", (sim_id,))
        row = self.cursor.fetchone()
        if row:
            org_dict = dict(row)
            org_dict['creation_params'] = self._deserialize_params(row['creation_params_json'])
            return org_dict
        return None

    def get_neuron_groups(self, organoid_id=None, sim_id=None):
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        # ... (lógica para obter organoid_id como antes) ...
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
            if 'positions_json' in row.keys() and row['positions_json']: # Check if column exists and has data
                 try:
                    pos_data = json.loads(row['positions_json'])
                    if 'positions_um' in pos_data and isinstance(pos_data['positions_um'], list):
                         ng_dict['positions'] = np.array(pos_data['positions_um']) * b2.um
                 except (json.JSONDecodeError, TypeError): #pragma: no cover
                     print(f"Warning: Could not deserialize positions_json for NG {row['ng_name_pyneurorg']}")
                     ng_dict['positions'] = None
            ng_list.append(ng_dict)
        return ng_list

    def get_synapse_groups(self, organoid_id=None, sim_id=None):
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        # ... (lógica para obter organoid_id como antes) ...
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
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        self.cursor.execute("SELECT * FROM StimuliApplied WHERE sim_id = ?", (sim_id,))
        rows = self.cursor.fetchall()
        stim_list = []
        for row in rows:
            stim_dict = dict(row)
            stim_dict['influence_radius'] = self._reconstruct_brian2_quantity(row['influence_radius_value'], row['influence_radius_unit'])
            stim_dict['stimulus_params'] = self._deserialize_params(row['stimulus_params_json'])
            stim_list.append(stim_dict)
        return stim_list

    def get_monitors_metadata(self, sim_id):
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
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        # ... (lógica para obter monitor_db_id como antes) ...
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
            return np.array([]), np.array([]) * b2.second

        indices = np.array([r['neuron_index'] for r in rows], dtype=int)
        times_val = np.array([r['spike_time_value'] for r in rows], dtype=float)
        time_unit_str = rows[0]['spike_time_unit']
        
        time_quantity = self._reconstruct_brian2_quantity(times_val, time_unit_str)
        if not isinstance(time_quantity, b2.Quantity): # Fallback if reconstruction failed for the array
            time_quantity = times_val * b2.second
            print(f"Warning: Could not fully reconstruct Quantity for spike times, using seconds for unit {time_unit_str}.")


        return indices, time_quantity

    def get_state_data(self, monitor_db_id=None, sim_id=None, monitor_name_pyneurorg=None):
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        actual_monitor_db_id = monitor_db_id
        if actual_monitor_db_id is None:
            # ... (lógica para obter actual_monitor_db_id como antes) ...
            if sim_id and monitor_name_pyneurorg:
                self.cursor.execute("SELECT monitor_db_id FROM Monitors WHERE sim_id = ? AND monitor_name_pyneurorg = ?", 
                                    (sim_id, monitor_name_pyneurorg))
                row = self.cursor.fetchone()
                if not row: return {'t': np.array([]) * b2.second, 'recorded_neuron_indices': []} 
                actual_monitor_db_id = row['monitor_db_id']
            else:
                raise ValueError("Provide monitor_db_id, or sim_id and monitor_name_pyneurorg.")


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
            return {'t': np.array([]) * b2.second, 'recorded_neuron_indices': []}

        time_unit_str_from_db = rows[0]['time_unit']
        time_unit_obj_for_t_array = self._reconstruct_brian2_quantity(1.0, time_unit_str_from_db) \
                                   if self._reconstruct_brian2_quantity(1.0, time_unit_str_from_db) is not None \
                                   else b2.second
        
        unique_times_numeric = sorted(list(set(r['time_value'] for r in rows)))
        t_array = np.array(unique_times_numeric) * time_unit_obj_for_t_array
        results = {'t': t_array}
        
        recorded_neuron_indices = sorted(list(set(int(r['neuron_index']) for r in rows)))
        results['recorded_neuron_indices'] = recorded_neuron_indices
        
        data_by_var_neuron_time = {}
        for row_dict in rows:
            var_name = row_dict['variable_name']
            neuron_idx = int(row_dict['neuron_index'])
            time_idx = int(row_dict['time_step_index'])
            
            if var_name not in data_by_var_neuron_time:
                data_by_var_neuron_time[var_name] = {
                    'data': np.full((len(recorded_neuron_indices), len(unique_times_numeric)), np.nan),
                    'unit_str': row_dict['variable_unit'] # Assume unit is consistent for a variable
                }

            mapped_neuron_array_idx = recorded_neuron_indices.index(neuron_idx) # Map original index to 0-based for array
            
            if row_dict['variable_value_real'] is not None:
                data_by_var_neuron_time[var_name]['data'][mapped_neuron_array_idx, time_idx] = row_dict['variable_value_real']
            elif row_dict['variable_value_text'] is not None:
                val_text = row_dict['variable_value_text']
                data_by_var_neuron_time[var_name]['data'][mapped_neuron_array_idx, time_idx] = json.loads(val_text.lower()) if val_text.lower() in ['true', 'false'] else val_text
        
        for var_name, var_info in data_by_var_neuron_time.items():
            var_unit_obj = self._reconstruct_brian2_quantity(1.0, var_info['unit_str'])
            if var_unit_obj is not None: # If unit reconstruction successful
                 results[var_name] = var_info['data'] * var_unit_obj.dimensions
            else: # Fallback if unit cannot be reconstructed
                 results[var_name] = var_info['data'] # Store as numpy array
                 print(f"Warning: Could not reconstruct unit for state variable '{var_name}'. Data stored as NumPy array.")
            
        return results

    def get_population_rate_data(self, monitor_db_id=None, sim_id=None, monitor_name_pyneurorg=None):
        if not self.cursor: raise sqlite3.Error("Database not connected.")
        # ... (lógica para obter monitor_db_id como antes) ...
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

        time_quantity = self._reconstruct_brian2_quantity(times_val, time_unit_str)
        rate_quantity = self._reconstruct_brian2_quantity(rates_val, rate_unit_str)

        if not isinstance(time_quantity, b2.Quantity): time_quantity = times_val * b2.second
        if not isinstance(rate_quantity, b2.Quantity): rate_quantity = rates_val * b2.Hz
        
        return time_quantity, rate_quantity

if __name__ == '__main__': #pragma: no cover
    # ... (bloco if __name__ == '__main__' como antes, para testar o reader) ...
    db_file = "test_pyneurorg_writer.db" 
    import os
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
                        print(f"  Sim ID: {sim_meta['sim_id']}, Name: {sim_meta['sim_name']}")
                        test_sim_id = sim_meta['sim_id']
                        organoid = reader.get_organoid_details(test_sim_id)
                        if organoid:
                            print(f"  Organoid for Sim ID {test_sim_id}: {organoid['organoid_name']}")
                            neuron_groups = reader.get_neuron_groups(organoid_id=organoid['organoid_id'])
                            for ng in neuron_groups:
                                print(f"    - NG: {ng['ng_name_pyneurorg']}, Model: {ng['neuron_model_pyneurorg']}")
                                if ng.get('positions'):
                                     print(f"      Positions (first 2): {ng['positions'][:2] if ng['positions'].shape[0]>0 else 'N/A'}")
                        monitors_metadata = reader.get_monitors_metadata(test_sim_id)
                        print(f"\n  Monitors ({len(monitors_metadata)}):")
                        for mon_meta in monitors_metadata:
                            print(f"    - {mon_meta['monitor_name_pyneurorg']} (Type: {mon_meta['monitor_type']})")
                            if mon_meta['monitor_type'] == "SpikeMonitor" and mon_meta['monitor_name_pyneurorg'] == "user_spike_monitor":
                                indices, times = reader.get_spike_data(monitor_db_id=mon_meta['monitor_db_id'])
                                print(f"      Spikes - Count: {len(indices)}, Example times: {times[:3] if len(times) > 0 else 'N/A'}")
                            elif mon_meta['monitor_type'] == "StateMonitor" and mon_meta['monitor_name_pyneurorg'] == "user_state_monitor":
                                state_data = reader.get_state_data(monitor_db_id=mon_meta['monitor_db_id'])
                                print(f"      State Data - Time points: {len(state_data.get('t',[]))}, Vars: {list(k for k in state_data.keys() if k not in ['t', 'recorded_neuron_indices'] )}")
                                if 'v' in state_data and len(state_data['v']) > 0:
                                     print(f"        Example Vm (neuron 0): {state_data['v'][0,:3] if state_data['v'].ndim >1 and state_data['v'].shape[1]>0 else state_data['v'][:3]}")
                        break 
                else:
                    print("No simulations found in the database.")
        except Exception as e:
            print(f"An error occurred during SQLiteReader example usage: {e}")
            import traceback
            traceback.print_exc()

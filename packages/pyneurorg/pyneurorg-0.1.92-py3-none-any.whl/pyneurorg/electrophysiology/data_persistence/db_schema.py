# src/pyneurorg/electrophysiology/data_persistence/db_schema.py

"""
Defines the SQLite database schema for pyneurorg simulations.
Contains SQL CREATE TABLE statements as string constants.
"""

# --- Simulation Metadata Tables ---

CREATE_SIMULATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS Simulations (
    sim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_uuid TEXT UNIQUE NOT NULL,
    sim_name TEXT,
    sim_timestamp_start DATETIME NOT NULL,
    sim_timestamp_end DATETIME,
    brian2_dt_value REAL,
    brian2_dt_unit TEXT,
    duration_run_value REAL,
    duration_run_unit TEXT,
    pyneurorg_version TEXT,
    brian2_version TEXT,
    numpy_version TEXT,
    notes TEXT
);
"""

CREATE_ORGANOIDS_TABLE = """
CREATE TABLE IF NOT EXISTS Organoids (
    organoid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER NOT NULL,
    organoid_name TEXT NOT NULL,
    creation_params_json TEXT,
    FOREIGN KEY (sim_id) REFERENCES Simulations(sim_id) ON DELETE CASCADE
);
"""

# --- Network Structure Tables ---

CREATE_NEURON_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS NeuronGroups (
    ng_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organoid_id INTEGER NOT NULL,
    ng_name_pyneurorg TEXT NOT NULL,
    ng_name_brian2 TEXT,
    num_neurons INTEGER NOT NULL,
    neuron_model_pyneurorg TEXT NOT NULL,
    model_params_json TEXT,
    spatial_distribution_func TEXT,
    spatial_params_json TEXT,
    FOREIGN KEY (organoid_id) REFERENCES Organoids(organoid_id) ON DELETE CASCADE
);
"""

# Storing all positions as a single JSON blob per NeuronGroup might be more efficient
# for SQLite than individual rows if N is large. If individual access is frequent,
# a separate table is better. Let's start with it in NeuronGroups for simplicity.
# If NeuronPositions table is desired:
# CREATE_NEURON_POSITIONS_TABLE = """
# CREATE TABLE IF NOT EXISTS NeuronPositions (
#     pos_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     ng_id INTEGER NOT NULL,
#     neuron_index_in_group INTEGER NOT NULL,
#     pos_x_um REAL,
#     pos_y_um REAL,
#     pos_z_um REAL,
#     FOREIGN KEY (ng_id) REFERENCES NeuronGroups(ng_id) ON DELETE CASCADE,
#     UNIQUE (ng_id, neuron_index_in_group)
# );
# """

CREATE_SYNAPSE_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS SynapseGroups (
    sg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organoid_id INTEGER NOT NULL,
    sg_name_pyneurorg TEXT NOT NULL,
    sg_name_brian2 TEXT,
    pre_ng_name_pyneurorg TEXT NOT NULL,
    post_ng_name_pyneurorg TEXT NOT NULL,
    synapse_model_pyneurorg TEXT NOT NULL,
    model_params_json TEXT,
    connect_rule_description TEXT,
    num_synapses_created INTEGER,
    FOREIGN KEY (organoid_id) REFERENCES Organoids(organoid_id) ON DELETE CASCADE
);
"""

# --- Stimulation Tables ---

CREATE_STIMULI_APPLIED_TABLE = """
CREATE TABLE IF NOT EXISTS StimuliApplied (
    stim_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER NOT NULL,
    mea_electrode_id INTEGER,
    target_group_name_pyneurorg TEXT NOT NULL,
    stimulus_type TEXT NOT NULL, -- e.g., 'current', 'current_density'
    waveform_name TEXT,
    cumulative_var_name TEXT,
    flag_template TEXT,
    influence_radius_value REAL,
    influence_radius_unit TEXT,
    stimulus_params_json TEXT, -- Params used for stimulus_generator
    FOREIGN KEY (sim_id) REFERENCES Simulations(sim_id) ON DELETE CASCADE
);
"""

# --- Monitoring Data Tables ---

CREATE_MONITORS_TABLE = """
CREATE TABLE IF NOT EXISTS Monitors (
    monitor_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER NOT NULL,
    monitor_name_pyneurorg TEXT NOT NULL UNIQUE, -- User-defined key for retrieval
    monitor_name_brian2 TEXT,
    monitor_type TEXT NOT NULL, -- 'SpikeMonitor', 'StateMonitor', 'PopulationRateMonitor'
    target_name_pyneurorg TEXT NOT NULL, -- Name of the NeuronGroup or SynapseGroup
    record_details_json TEXT, -- For StateMonitor: vars, indices; For SpikeMonitor: indices
    FOREIGN KEY (sim_id) REFERENCES Simulations(sim_id) ON DELETE CASCADE
);
"""

CREATE_SPIKE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS SpikeData (
    spike_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_db_id INTEGER NOT NULL,
    neuron_index INTEGER NOT NULL, -- Index within the monitored group
    spike_time_value REAL NOT NULL,
    spike_time_unit TEXT NOT NULL,
    FOREIGN KEY (monitor_db_id) REFERENCES Monitors(monitor_db_id) ON DELETE CASCADE
);
"""

CREATE_STATE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS StateData (
    state_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_db_id INTEGER NOT NULL,
    time_step_index INTEGER NOT NULL, -- Index of the time point in the monitor's t array
    time_value REAL NOT NULL,
    time_unit TEXT NOT NULL,
    neuron_index INTEGER NOT NULL, -- Index within the recorded subset of the monitored group
    variable_name TEXT NOT NULL,
    variable_value_real REAL, -- For float/int values
    variable_value_text TEXT, -- For boolean or other non-numeric if needed (though rare for state vars)
    variable_unit TEXT, -- Unit of the variable_value_real
    FOREIGN KEY (monitor_db_id) REFERENCES Monitors(monitor_db_id) ON DELETE CASCADE
);
"""
# Note on StateData: Storing each variable for each neuron at each time step in a long format
# can lead to a very large table. Consider alternatives if performance becomes an issue:
# 1. Store entire arrays (e.g., one neuron's Vm trace) as a BLOB (e.g., pickled NumPy array or JSON array).
#    - Pros: Fewer rows. Cons: Harder to query individual data points with SQL.
# 2. Create separate tables per monitored variable if schema is fixed.
# For now, the long format is chosen for query flexibility.

CREATE_POPULATION_RATE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS PopulationRateData (
    rate_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_db_id INTEGER NOT NULL,
    time_value REAL NOT NULL,
    time_unit TEXT NOT NULL,
    rate_value REAL NOT NULL,
    rate_unit TEXT NOT NULL, -- e.g., "Hz"
    FOREIGN KEY (monitor_db_id) REFERENCES Monitors(monitor_db_id) ON DELETE CASCADE
);
"""

# List of all create table statements for convenience
ALL_TABLES = [
    CREATE_SIMULATIONS_TABLE,
    CREATE_ORGANOIDS_TABLE,
    CREATE_NEURON_GROUPS_TABLE,
    # CREATE_NEURON_POSITIONS_TABLE, # If using separate table for positions
    CREATE_SYNAPSE_GROUPS_TABLE,
    CREATE_STIMULI_APPLIED_TABLE,
    CREATE_MONITORS_TABLE,
    CREATE_SPIKE_DATA_TABLE,
    CREATE_STATE_DATA_TABLE,
    CREATE_POPULATION_RATE_DATA_TABLE
]

if __name__ == '__main__':
    # Example of how to print all schemas
    for i, table_sql in enumerate(ALL_TABLES):
        print(f"-- Schema for table {i+1} --")
        print(table_sql)
        print("-" * 30)
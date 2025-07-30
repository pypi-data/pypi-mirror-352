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
    positions_json TEXT, -- JSON blob of Nx3 position array (e.g., in um)
    FOREIGN KEY (organoid_id) REFERENCES Organoids(organoid_id) ON DELETE CASCADE
);
"""

# Storing all positions as a single JSON blob per NeuronGroup in NeuronGroups table.
# If individual row-wise access to positions becomes critical for many queries,
# the NeuronPositions table below could be activated. For now, it's commented out.
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
    pre_ng_name_pyneurorg TEXT NOT NULL, -- Name of the pyneurorg NeuronGroup
    post_ng_name_pyneurorg TEXT NOT NULL, -- Name of the pyneurorg NeuronGroup
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
    stimulus_type TEXT NOT NULL, -- e.g., 'current', 'current_density', 'dimensionless'
    waveform_name TEXT,          -- Name of the TimedArray in Brian2 namespace
    cumulative_var_name TEXT,    -- Name of the variable in neuron model (e.g., I_stimulus_sum)
    flag_template TEXT,
    influence_radius_value REAL,
    influence_radius_unit TEXT,
    stimulus_params_json TEXT,   -- Parameters used for stimulus_generator
    FOREIGN KEY (sim_id) REFERENCES Simulations(sim_id) ON DELETE CASCADE
);
"""

# --- Monitoring Data Tables ---

CREATE_MONITORS_TABLE = """
CREATE TABLE IF NOT EXISTS Monitors (
    monitor_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER NOT NULL,
    monitor_name_pyneurorg TEXT NOT NULL, 
    monitor_name_brian2 TEXT,
    monitor_type TEXT NOT NULL, -- 'SpikeMonitor', 'StateMonitor', 'PopulationRateMonitor'
    target_name_pyneurorg TEXT NOT NULL, -- pyneurorg name of NeuronGroup/SynapseGroup
    record_details_json TEXT, -- For StateMonitor: vars, indices; For SpikeMonitor: indices
    FOREIGN KEY (sim_id) REFERENCES Simulations(sim_id) ON DELETE CASCADE,
    UNIQUE (sim_id, monitor_name_pyneurorg) -- Ensure user-defined name is unique per simulation
);
"""

CREATE_SPIKE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS SpikeData (
    spike_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_db_id INTEGER NOT NULL,
    neuron_index INTEGER NOT NULL, -- Index within the monitored group (original index if record=True)
    spike_time_value REAL NOT NULL,
    spike_time_unit TEXT NOT NULL,
    FOREIGN KEY (monitor_db_id) REFERENCES Monitors(monitor_db_id) ON DELETE CASCADE
);
"""

CREATE_STATE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS StateData (
    state_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_db_id INTEGER NOT NULL,
    time_step_index INTEGER NOT NULL, 
    time_value REAL NOT NULL,
    time_unit TEXT NOT NULL,
    neuron_index INTEGER NOT NULL, -- Original index in the source group
    variable_name TEXT NOT NULL,
    variable_value_real REAL, 
    variable_value_text TEXT, 
    variable_unit TEXT, 
    FOREIGN KEY (monitor_db_id) REFERENCES Monitors(monitor_db_id) ON DELETE CASCADE
);
"""

CREATE_POPULATION_RATE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS PopulationRateData (
    rate_db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_db_id INTEGER NOT NULL,
    time_value REAL NOT NULL,
    time_unit TEXT NOT NULL,
    rate_value REAL NOT NULL,
    rate_unit TEXT NOT NULL, 
    FOREIGN KEY (monitor_db_id) REFERENCES Monitors(monitor_db_id) ON DELETE CASCADE
);
"""

# List of all create table statements for convenience
ALL_TABLES = [
    CREATE_SIMULATIONS_TABLE,
    CREATE_ORGANOIDS_TABLE,
    CREATE_NEURON_GROUPS_TABLE,
    # CREATE_NEURON_POSITIONS_TABLE, # Kept commented as positions_json is in NeuronGroups
    CREATE_SYNAPSE_GROUPS_TABLE,
    CREATE_STIMULI_APPLIED_TABLE,
    CREATE_MONITORS_TABLE,
    CREATE_SPIKE_DATA_TABLE,
    CREATE_STATE_DATA_TABLE,
    CREATE_POPULATION_RATE_DATA_TABLE
]

if __name__ == '__main__': #pragma: no cover
    # Example of how to print all schemas
    for i, table_sql in enumerate(ALL_TABLES):
        table_name = table_sql.split("EXISTS ")[1].split(" ")[0]
        print(f"-- Schema for table {table_name} --")
        print(table_sql)
        print("-" * 30)
# src/pyneurorg/electrophysiology/data_persistence/__init__.py

"""
The data_persistence sub-package handles saving and loading of simulation
metadata, setup, and results, primarily using an SQLite database.
"""

from .db_schema import (
    CREATE_SIMULATIONS_TABLE,
    CREATE_ORGANOIDS_TABLE,
    CREATE_NEURON_GROUPS_TABLE,
    CREATE_SYNAPSE_GROUPS_TABLE,
    CREATE_STIMULI_APPLIED_TABLE,
    CREATE_MONITORS_TABLE,
    CREATE_SPIKE_DATA_TABLE,
    CREATE_STATE_DATA_TABLE,
    CREATE_POPULATION_RATE_DATA_TABLE,
    ALL_TABLES
)

from .sqlite_writer import SQLiteWriter
from .sqlite_reader import SQLiteReader
from .persistent_simulator import (
    PersistentSimulator,
    LOG_NOTHING,
    LOG_SIM_METADATA,
    LOG_ORGANOID_SETUP,
    LOG_MONITOR_METADATA,
    LOG_SPIKE_DATA,
    LOG_STATE_DATA,
    LOG_RATE_DATA,
    LOG_ALL_SETUP,
    LOG_ALL_RESULTS,
    LOG_EVERYTHING
)

__all__ = [
    # From db_schema (optional to expose all create statements, usually not needed by end-user)
    # "CREATE_SIMULATIONS_TABLE", 
    # "ALL_TABLES", 
    
    # Core classes
    "SQLiteWriter",
    "SQLiteReader",
    "PersistentSimulator",

    # Logging flags
    "LOG_NOTHING",
    "LOG_SIM_METADATA",
    "LOG_ORGANOID_SETUP",
    "LOG_MONITOR_METADATA",
    "LOG_SPIKE_DATA",
    "LOG_STATE_DATA",
    "LOG_RATE_DATA",
    "LOG_ALL_SETUP",
    "LOG_ALL_RESULTS",
    "LOG_EVERYTHING"
]
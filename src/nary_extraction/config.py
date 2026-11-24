from pathlib import Path

# Paths

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
SCHEMA_DIR = ROOT / "schemas"

RAW_TEXT_DIR = DATA_DIR / "raw" / "Text"
PROCESSED_DIR = DATA_DIR / "processed"
EXPERIMENT_DIR = DATA_DIR / "experiments"
OUTPUT_DIR = DATA_DIR / "output"

DATASET_FILE = PROCESSED_DIR / "dataset.json"
EXP1_FILE = EXPERIMENT_DIR / "exp1_dataset_v2.json"
OUTPUT_FILE = OUTPUT_DIR / "predictions_exp1_50.json"

SEED = 42

# LLM

MODEL_NAME = "llama3:8b"
TEMPERATURE = 0
NUM_CTX = 8192

# SBERT

SBERT_MODEL_NAME = "all-MiniLM-L6-v2"
SBERT_REFINE_MIN_SCORE = 0.50
SBERT_REFINE_MIN_MARGIN = 0.03

# Experiment settings

RUN_LIMIT = 50

INCLUDE_NEGATIVE_SAMPLES = False

# Event taxonomy

TARGET_EVENT_TYPES = [
    "Manufacturing",
    "Competition",
    "Supply",
    "Investment",
]


# Entity taxonomy

ENTITY_TYPES = (
    "ORG",
    "COMP",
    "PERSON",
    "PRODUCT",
    "TECHNOLOGY",
    "MATERIAL",
    "FACILITY",
    "LOCATION",
    "SEGMENT",
    "REGULATION",
    "AGREEMENT",
    "IMPACT_EVENT",
    "METRIC_VALUE",
    "TIME",
    "OTHER",
)


# Filing company normalization


# Filing company normalization

COMPANY_MAP = {
    # Tier 0 — OEMs (5)
    "Ford": "Ford Motor Company",
    "GM": "General Motors Company",
    "Tesla": "Tesla, Inc.",
    "Rivian": "Rivian Automotive, Inc.",
    "Lucid": "Lucid Group, Inc.",

    # Tier 1 — Major systems/component suppliers (11)
    "Aptiv": "Aptiv PLC",
    "BorgWarner": "BorgWarner Inc.",
    "Lear": "Lear Corporation",
    "Adient": "Adient plc",
    "Dana": "Dana Incorporated",
    "American_Axle": "American Axle & Manufacturing Holdings, Inc.",
    "Visteon": "Visteon Corporation",
    "Gentex": "Gentex Corporation",
    "Gentex_reannotated": "Gentex Corporation",
    "Autoliv": "Autoliv, Inc.",
    "Cooper_Standard": "Cooper-Standard Holdings Inc.",
    "Cooper-Standard": "Cooper-Standard Holdings Inc.",
    "Goodyear": "The Goodyear Tire & Rubber Company",

    # Tier 2 — Semiconductor (6)
    "NVIDIA": "NVIDIA Corporation",
    "Qualcomm": "QUALCOMM Incorporated",
    "Texas_Instruments": "Texas Instruments Incorporated",
    "Onsemi": "onsemi",
    "Analog_Devices": "Analog Devices, Inc.",
    "NXP": "NXP Semiconductors N.V.",

    # Tier 2b — Electronics (2)
    "Avnet": "Avnet, Inc.",
    "Arrow Electronics": "Arrow Electronics, Inc.",

    # Tier 3 — Raw materials (8)
    "Albemarle": "Albemarle Corporation",
    "Alcoa": "Alcoa Corporation",
    "Nucor": "Nucor Corporation",
    "U.S. Steel": "United States Steel Corporation",
    "Cleveland-Cliffs": "Cleveland-Cliffs Inc.",
    "Carpenter_Technology": "Carpenter Technology Corporation",
    "MP_Materials": "MP Materials Corp.",
    "QuantumScape": "QuantumScape Corporation",

    # Tier 4 — Mining (2)
    "Southern_Copper": "Southern Copper Corporation",
    "Freeport-McMoRan": "Freeport-McMoRan Inc.",
}


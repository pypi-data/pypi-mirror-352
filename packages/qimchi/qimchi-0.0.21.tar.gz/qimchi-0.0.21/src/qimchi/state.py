import json

import numpy as np
from pathlib import Path
from dataclasses import dataclass, field

# For SQLState
import sqlite3
import threading
from dataclasses import asdict
from typing import Any

# Local imports
from qimchi.logger import logger


# Default vars
QIMCHI_HOME = Path("~/.qimchi").expanduser()
DATA_REFRESH_INTERVAL = 1_000  # ms
SQUARIFY_SIZE = "450px"


# Plot width options
DEFAULT_PLOT_WIDTH = "33%"  # Corresponds to Bulma's column width options
PLOT_WIDTH_OPTS_DICT = {
    "33%": "is-one-third",
    "50%": "is-half",
    "66%": "is-two-thirds",
    "100%": "is-full",
}
PLOT_WIDTH_OPTS = [{"label": key, "value": key} for key in PLOT_WIDTH_OPTS_DICT.keys()]

# Default filter options
DEFAULT_SAVGOL_OPTS = {
    "window": 5,
    "polyorder": 2,
    # NOTE: -1 is default for savgol_filter AKA column-wise for 2D heatmap. "2" here means along both axes.
    # NOTE: See filters.py::Smooth.apply_2d() for more details.
    "axis": 2,
    "deriv": 0,
    "delta": 1.0,
    "mode": "interp",
    "cval": 0.0,
}

DEFAULT_SMA_WINDOW = 5

DEFAULT_NORM_AXIS = "z"

DEFAULT_GC_OPTS = {
    "gamma": 2.0,  # skimage default is 1.0
    "gain": 2.0,  # skimage default is 1.0
}

DEFAULT_LC_OPTS = {
    "gain": 1.0,
    "inv": False,
}

DEFAULT_SC_OPTS = {
    "cutoff": 0.5,
    "gain": 10.0,
}

DEFAULT_POLYFIT_OPTS = {
    "deg": 5,
    "window": [0, 1],  # TODOLATER: window
}

# TODOLATER: Can allow specifying the range to scale to.
# TODOLATER: See: https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.rescale_intensity
DEFAULT_RI_OPTS = {
    "in_range": "image",  # skimage default is "image"
}

DEFAULT_ROTA_OPTS = {
    "angle": 0,
}

DEFAULT_HMAP_COLSCALE = "viridis"
DEFAULT_LINE_MODE = "lines+markers"
DEFAULT_LINE_COLOR = "#6acc64"
DEFAULT_LINE_WIDTH = 3
DEFAULT_LINE_OPACITY = 1.0
DEFAULT_LINE_DASH = "solid"
DEFAULT_LINE_SHAPE = "linear"
DEFAULT_SPLINE_SMOOTHING = 0.0
DEFAULT_MARKER_COLOR = "#6acc64"
DEFAULT_MARKER_SIZE = 6
DEFAULT_MARKER_OPACITY = 0.5
LINE_MODE_OPTS = [
    {"label": "Lines", "value": "lines"},
    {"label": "Markers", "value": "markers"},
    {"label": "Lines + Markers", "value": "lines+markers"},
]
LINE_COLOR_OPTS = MARKER_COLOR_OPTS = GRID_COLOR_OPTS = TICK_COLOR_OPTS = [
    "#4878d0",
    "#ee854a",
    "#6acc64",
    "#d65f5f",
    "#956cb4",
    "#8c613c",
    "#dc7ec0",
    "#797979",
    "#d5bb67",
    "#82c6e2",
]
LINE_DASH_OPTS = [
    {"label": "Solid", "value": "solid"},
    {"label": "Dash", "value": "dash"},
    {"label": "Dot", "value": "dot"},
    {"label": "Long Dash", "value": "longdash"},
    {"label": "Dash Dot", "value": "dashdot"},
    {"label": "Long Dash Dot", "value": "longdashdot"},
]
LINE_SHAPE_OPTS = [
    {"label": "Linear", "value": "linear"},
    {"label": "Spline", "value": "spline"},
    {"label": "Step", "value": "hv"},
    {"label": "Step Before", "value": "hvh"},
    {"label": "Step After", "value": "vhv"},
]
DEFAULT_MARKER_SYMBOL = "circle"
MARKER_SYMBOL_OPTS = [
    {"label": "Circle", "value": "circle"},
    {"label": "Square", "value": "square"},
    {"label": "Diamond", "value": "diamond"},
    {"label": "Cross", "value": "cross"},
    {"label": "X", "value": "x"},
    {"label": "Triangle-Down", "value": "triangle-down"},
    {"label": "Triangle-Left", "value": "triangle-left"},
    {"label": "Triangle-Right", "value": "triangle-right"},
    {"label": "Triangle-Up", "value": "triangle-up"},
    {"label": "Diamond-Tall", "value": "diamond-tall"},
    {"label": "Diamond-Tall-Open", "value": "diamond-tall-open"},
    {"label": "Diamond-Wide", "value": "diamond-wide"},
    {"label": "Diamond-Wide-Open", "value": "diamond-wide-open"},
    {"label": "Hourglass", "value": "hourglass"},
    {"label": "Hourglass-Open", "value": "hourglass-open"},
]
# Grid & tick options
DEFAULT_AXIS_TYPE = "linear"
DEFAULT_GRID_COLOR = DEFAULT_TICK_COLOR = "gray"
DEFAULT_SHOWGRID = False
DEFAULT_NTICKS = 5
DEFAULT_GRID_WIDTH = 1  # px
DEFAULT_GRID_DASH = "solid"
AXIS_TYPE_OPTS = [
    {"label": "Linear", "value": "linear"},
    {"label": "Log", "value": "log"},
]
GRID_DASH_OPTS = [
    {"label": "Solid", "value": "solid"},
    {"label": "Dash", "value": "dash"},
    {"label": "Dot", "value": "dot"},
    {"label": "Long Dash", "value": "longdash"},
    {"label": "Dash Dot", "value": "dashdot"},
    {"label": "Long Dash Dot", "value": "longdashdot"},
]
DEFAULT_TICK_WIDTH = 1  # px
DEFAULT_TICK_LENGTH = 5  # px
DEFAULT_TICK_ANGLE = 0  # deg

# Default filter options
DEFAULT_SAVGOL_WINDOW_LENGTH = 5
DEFAULT_SAVGOL_POLYORDER = 2


class JSONStateEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for the JSONState dataclass.

    """

    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj.resolve())
        elif isinstance(obj, np.int64):
            return int(obj)
        return super().default(obj)


class JSONStateDecoder(json.JSONDecoder):
    """
    Custom JSON decoder for the JSONState dataclass.

    """

    def __init__(self):
        super().__init__(object_hook=self.object_hook)

    def object_hook(self, obj):
        if "state_file" in obj:
            obj["state_file"] = Path(obj["state_file"])
        if "dataset_path" in obj:
            obj["dataset_path"] = Path(obj["dataset_path"])
        return obj


@dataclass
class JSONState:
    # FS stuff
    state_session_id: str = ""
    # state_file: Path = QIMCHI_HOME / "state.json"
    # logger.warning(f"State file: {state_file}")

    # selector.py
    dataset_path: Path = Path("")
    dataset_type: str = ""
    measurement_path: Path = Path("")
    measurement_last_fmt: str = ""

    # datasets.py
    wafer_id: str = ""
    device_type: str = ""
    device_id: str = ""
    measurement_type: str = ""
    measurement: str = ""

    # NOTE: Specs for plot_states
    # 1. No data stored, only things like:
    #   1.1 deps (list) - List of dependent variables
    #   1.2 indeps (list) - List of independent variables
    #   1.3 theme (dict) - Not all keys are applicable to all plots
    # 2. `slider` config (dict)
    # 3. `filters_order` (list) - List of filters applied in order
    # 4. `filters_opts` (dict) - Dict of filters with options
    # 5. `plots_menu` (list) - Open/Close State etc. of the options in the plots-menu
    # And more stuff. Check state.json.
    plot_states: dict[str, dict] = field(default_factory=dict)
    squarify_plots: bool = False

    # metadata.py
    parameters_snapshot: dict = field(default_factory=dict)

    def __post_init__(self):
        assert self.state_session_id, "Session ID cannot be empty."
        # Create the state directory if it doesn't exist
        try:
            QIMCHI_HOME.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            err_msg = (
                f"PermissionError: Cannot create state directory at {QIMCHI_HOME}. "
                f"WORKAROUND: Please manually create this directory: {QIMCHI_HOME}"
            )
            logger.error(err_msg)
            raise PermissionError(err_msg)
        # Create the state file path
        self.state_file: Path = (
            QIMCHI_HOME / f"qimchistate_{self.state_session_id}.json"
        )
        logger.warning(f"State file: {self.state_file}")

    def load_state(self) -> dict:
        """
        Loads the state from the local JSON file if it exists.
        Otherwise, creates the state from the default values.

        """
        state_file = self.state_file
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    self.__dict__.update(json.load(f, cls=JSONStateDecoder))
                logger.debug("State loaded from disk.")
            except json.JSONDecodeError:
                logger.warning(
                    "Error decoding state. Backing up current file and creating a new state file..."
                )
                # Rename the current state file
                try:
                    state_file.rename(state_file.with_suffix(".json.bak"))
                except FileExistsError:
                    logger.error(
                        f"Backup file {state_file.with_suffix('.json.bak')} already exists and will be overwritten."
                    )
                    # Overwrite the existing backup file
                    state_file.with_suffix(".json.bak").unlink()
                    state_file.rename(state_file.with_suffix(".json.bak"))

                # Create a new state file
                self.save_state()
                logger.warning(
                    f"New state file created at {state_file}.\nOld state file backed up at {state_file}.bak."
                )

                # Load the new state file # NOTE: No recursion here
                self.load_state()

            except Exception as err:
                logger.error(f"Error loading state: {err}", exc_info=True)
                exit()
        else:
            logger.debug("State loaded anew.")
        return self.__dict__

    def save_state(self) -> None:
        """
        Saves the given state to the local JSON file.

        """
        data = self.__dict__

        state_file = self.state_file
        with open(state_file, "w") as f:
            json.dump(data, f, indent=4, cls=JSONStateEncoder)


# Load the state from disk or create a new one
# _state = JSONState()
# _state.load_state()


DB_PATH = QIMCHI_HOME / "qimchi_state.db"

# One global connection pool lock (if needed for multi-thread access)
_db_lock = threading.Lock()


@dataclass
class SQLiteState:
    state_session_id: str
    dataset_path: str = ""
    dataset_type: str = ""
    measurement_path: str = ""
    measurement_last_fmt: str = ""
    wafer_id: str = ""
    device_type: str = ""
    device_id: str = ""
    measurement_type: str = ""
    measurement: str = ""
    plot_states: dict[str, dict] = field(default_factory=dict)
    squarify_plots: bool = False
    parameters_snapshot: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        assert self.state_session_id, "Session ID cannot be empty."
        # Create the state directory if it doesn't exist
        QIMCHI_HOME.mkdir(parents=True, exist_ok=True)

    def save_state(self):
        with _db_lock, sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                """
                INSERT INTO session_state (session_id, state_json, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id)
                DO UPDATE SET state_json = excluded.state_json,
                              last_updated = CURRENT_TIMESTAMP;
                """,
                (self.state_session_id, json.dumps(asdict(self), cls=JSONStateEncoder)),
            )
            conn.commit()

    @classmethod
    def load_state(cls, session_id: str) -> "SQLiteState":
        with _db_lock, sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.execute(
                "SELECT state_json FROM session_state WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()

        if row:
            data = json.loads(row[0], cls=JSONStateDecoder)
            return cls(**data)
        else:
            # Create a new default state
            state = cls(state_session_id=session_id)
            state.save_to_db()
            return state

    def __str__(self):
        return json.dumps(asdict(self), indent=4, cls=JSONStateEncoder)

    __repr__ = __str__


def load_state_from_disk(session_id: str) -> SQLiteState:
    """
    Loads the state from disk or creates a new one.

    Args:
        session_id (str): Session ID to load the state for

    Returns:
        SQLiteState: Loaded or newly created state

    """
    assert session_id, "Session ID cannot be empty"

    with _db_lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        # Ensure table exists (runs only if needed — harmless otherwise)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_state (
                session_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cursor = conn.execute(
            "SELECT state_json FROM session_state WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()

    if row:
        data = json.loads(row[0], cls=JSONStateDecoder)
        return SQLiteState(**data)
    else:
        state = SQLiteState(state_session_id=session_id)
        state.save_state()
        return state

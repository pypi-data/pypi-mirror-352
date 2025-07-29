from pathlib import Path

from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

# Local imports
import qimchi.components.data as data
from qimchi.components.data import (
    __all__ as DATASET_TYPES,
)  # NOTE: __all__ is a list of all the public names in the module
from qimchi.components.utils import read_data
from qimchi.state import load_state_from_disk, DATA_REFRESH_INTERVAL
from qimchi.logger import logger


def data_selector() -> html.Div:
    """
    Generator for the data selector component.

    Returns:
        dash.html.Div: The data selector component
    """
    DROPDOWN_HEIGHT = "4rem"  # consistent height for inputs & dropdowns

    return html.Div(
        [
            # Data input + dropdowns + button (first row)
            html.Div(
                [
                    dcc.Interval(
                        id="upload-ticker",
                        interval=DATA_REFRESH_INTERVAL,
                        n_intervals=0,
                    ),
                    dcc.Store(
                        id="is-data-selector-set",
                        data=False,
                        storage_type="memory",
                    ),
                    # Dataset Path Input
                    html.Div(
                        dcc.Input(
                            className="input",
                            type="text",
                            placeholder="Dataset Path",
                            id="dataset-path",
                            persistence=True,
                            persistence_type="local",
                            style={"width": "100%"},
                        ),
                        className="column is-5 pt-0 pb-0",
                        style={
                            "height": DROPDOWN_HEIGHT,
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                    # Dataset Type Dropdown
                    html.Div(
                        dcc.Dropdown(
                            options=DATASET_TYPES,
                            placeholder="Dataset type",
                            id="dataset-type",
                            persistence=True,
                            persistence_type="local",
                            style={"width": "100%"},
                        ),
                        className="column is-5 pt-0 pb-0",
                        style={
                            "height": DROPDOWN_HEIGHT,
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                    # Submit Button
                    html.Div(
                        html.Button(
                            html.I(className="fa-solid fa-dice-d20"),
                            id="submit",
                            n_clicks=0,
                            className="button is-warning",
                            style={"height": "2.5rem"},
                        ),
                        className="column is-2 pt-0 pb-0",
                        style={
                            "height": DROPDOWN_HEIGHT,
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                ],
                className="columns is-multiline ml-1 mr-1 mb-0 is-vcentered",
                id="selector",
            ),
            # Separate row for sample info / data options
            html.Div(
                [
                    html.Div(
                        className="column is-12",
                        id="data-options",
                    )
                ],
                className="columns ml-1 mr-1 mt-1 mb-1",
            ),
            # Background signal
            dcc.Store("load-signal", data=0),
        ]
    )


@callback(
    Output("data-options", "children"),
    State("session-id", "data"),
    State("data-options", "children"),
    Input("dataset-type", "value"),
    Input("dataset-path", "value"),
    Input("submit", "n_clicks"),
    prevent_initial_call=True,
)
def update_options(
    sess_id: str, sel_contents: None | html.Div, dataset_type: str, dataset_path: str, _
) -> html.Div:
    """
    Updates the options for the data selector.

    Args:
        sess_id (str): Session ID to load the state for
        sel_contents (None | html.Div): The current contents of the data selector
        dataset_type (str): The type of the dataset
        dataset_path (str): The path to the dataset

    Returns:
        dash.html.Div: The updated data selector component

    """
    _state = load_state_from_disk(sess_id)

    if dataset_type is not None and dataset_path is not None:
        try:
            dataset_path = Path(dataset_path)
            logger.debug(f"Dataset Type: {dataset_type}")
            logger.debug(f"Dataset Path: {dataset_path}")

            # Import `dataset_type` class from data module and instantiate it
            data_cls = getattr(data, dataset_type)(path=dataset_path)
            logger.debug(f"Dataset Class: {data_cls}")

            # Update the state
            _state.dataset_path = dataset_path
            _state.dataset_type = dataset_type
            _state.save_state()

            return data_cls.selector()
        except AttributeError:
            # CONCERN: API: XarrayData is being handled differently from XarrayDataFolder
            logger.error("AttributeError from update_options()")
            return sel_contents
    return sel_contents


@callback(
    Output("submit", "n_clicks"),
    State("submit", "n_clicks"),
    State("dataset-path", "value"),
    State("dataset-type", "value"),
    State("is-data-selector-set", "data"),
    State("session-id", "data"),
    Input("upload-ticker", "n_intervals"),
)
def refresh(
    n_clicks: int,
    dataset_path: str,
    dataset_type: str,
    is_ds_set: bool,
    sess_id: str,
    _,
) -> int:
    """
    Conditionally refreshes the submit button, auto-submitting the data path
    and options to refresh the data selector dropdowns.

    Args:
        n_clicks (int): The current number of clicks
        dataset_path (str): The path to the dataset
        dataset_type (str): The type of the dataset
        is_ds_set (bool): Whether the data selector is set
        sess_id (str): Session ID to load the state for

    Returns:
        int: The number of clicks

    Raises:
        PreventUpdate: If `dataset_path` or `dataset_type` is not set, or if `is_ds_set` is True

    """
    logger.debug(f"Refresh | sess_id: {sess_id}")
    logger.debug(
        f"Refresh | n_clicks: {n_clicks} | dataset_path: {dataset_path} | data_type: {dataset_type} | is_ds_set: {is_ds_set}"
    )
    if not dataset_path or not dataset_type or is_ds_set:
        logger.debug(
            "Refresh | No data path or type set; or data_selector is set. Not refreshing."
        )
        raise PreventUpdate
    logger.debug("Refresh | Refreshing data selector.")
    return n_clicks


@callback(
    Output("dependent-dropdown", "options"),
    State("session-id", "data"),
    Input("load-signal", "data"),
)
def update_dependents(sess_id: str, sig: int | None) -> list:
    """
    Updates the dependent dropdown options.

    Args:
        sess_id (str): Session ID to load the state for
        sig (int | None): Signal to indicate that data has been updated

    Returns:
        list: The dependent dropdown options generated from the data

    Raises:
        PreventUpdate: If `sig` is None or 0

    """
    if sig in [None, 0]:
        raise PreventUpdate
    data = read_data(sess_id, src="update_dependents")
    return list(data.data_vars.keys())


@callback(
    Output("independent-dropdown", "options"),
    State("session-id", "data"),
    Input("load-signal", "data"),
    Input("dependent-dropdown", "value"),
)
def update_independents(sess_id: str, sig: int | None, dependents: list):
    """
    Updates the independent dropdown options.

    Args:
        sess_id (str): Session ID to load the state for
        sig (int): Signal to indicate that data has been updated
        dependents (list): List of dependent variables

    Returns:
        list: The independent dropdown options generated from the data

    Raises:
        PreventUpdate: If `sig` is None or 0, or `dependents` is None

    """
    if sig in [None, 0] or dependents is None:
        raise PreventUpdate
    data = read_data(sess_id, src="update_independents")
    return list(data[dependents].coords)

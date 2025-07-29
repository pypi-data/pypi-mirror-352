import json
import shutil
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Any, Tuple

import plotly.io as pio
import dash_daq as daq

from plotly import graph_objects as go
from dash import ALL, MATCH, Input, Output, State, callback, html, dcc
from dash import callback_context as ctx
from dash.exceptions import PreventUpdate
from xarray import Dataset

# Local imports
from qimchi.components.appearance import apply_appearance_by_key, apply_appearance_axes
from qimchi.components.plot_elements import (
    appearance_line_options,
    appearance_marker_options,
)
from qimchi.components.utils import read_data, format_number
from qimchi.components.plots import Plot

from qimchi.state import load_state_from_disk, PLOT_WIDTH_OPTS_DICT, SQUARIFY_SIZE
from qimchi.logger import logger


pio.templates.default = "none"


def plot_selector() -> html.Div:
    """
    Generator for the plot selector, defining the dropdowns for the dependent and independent variables.

    Returns:
        dash.html.Div: Dash div component containing the dropdowns for the dependent and independent variables.

    """
    return html.Div(
        [
            html.Div(
                [
                    html.P("Dependents"),
                    dcc.Dropdown(
                        className="dropdown",
                        id="dependent-dropdown",
                        persistence=True,
                        persistence_type="local",
                    ),
                ],
                className="column is-one-third",
            ),
            html.Div(
                [
                    html.P("Independents"),
                    dcc.Dropdown(
                        className="dropdown",
                        id="independent-dropdown",
                        multi=True,
                        persistence=True,
                        persistence_type="local",
                    ),
                ],
                className="column is-one-third",
            ),
            html.Div(
                html.Button("Add Plot", className="button is-3", id="add-plot"),
                className="column mt-auto",
            ),
            html.Div(
                daq.ToggleSwitch(
                    id="squarify-all-plots",
                    label="Squarify Plots",
                    labelPosition="top",
                    persistence=True,
                    persistence_type="local",
                ),
                className="column mt-auto",
            ),
            html.Div(
                html.Button(
                    "Clear All Plots",
                    id="clear-all-plots",
                    className="button is-danger",
                ),
                className="column mt-auto",
            ),
        ],
        className="columns is-full",
        id="plot-selector",
    )


def plots_container() -> html.Div:
    """
    Plots container

    Returns:
        dash.html.Div: Empty div to hold the plots, to be filled with callbacks

    """
    return html.Div(
        [
            html.Div([], className="columns is-multiline is-full", id="plots"),
        ]
    )


@callback(
    State("session-id", "data"),
    Input("measurement", "value"),
    Input("measurement-type", "value"),
    Input("device-id", "value"),
    Input("device-type", "value"),
    Input("wafer-id", "value"),
)
def update_state_wafer_id(
    sess_id: str,
    measurement: str,
    measurement_type: str,
    device_id: str,
    device_type: str,
    wafer_id: str,
) -> None:
    """
    Update the state with the wafer id, device type, device id, measurement type, and measurement.

    """
    _state = load_state_from_disk(sess_id)
    _state.wafer_id = wafer_id if wafer_id else _state.wafer_id
    _state.device_type = device_type if device_type else _state.device_type
    _state.device_id = device_id if device_id else _state.device_id
    _state.measurement_type = (
        measurement_type if measurement_type else _state.measurement_type
    )
    _state.measurement = measurement if measurement else _state.measurement
    _state.save_state()


def _update_plots_list(
    sess_id: str,
    new_plots: list[html.Div],
    plots_list_tmp: list,
) -> list:
    """
    Utility function to update the plots list with new plots in Div.

    Args:
        sess_id (str): Session ID to load the state for
        new_plots (list): List of new plots in Div
        plots_list_tmp (list): List of existing plots in Div

    Returns:
        list: Updated list of plots in Div

    """
    _state = load_state_from_disk(sess_id)

    for new_plot in new_plots:
        fig_id = new_plot.children[0].children[0].id["index"]
        fig = _state.plot_states[fig_id]
        width = PLOT_WIDTH_OPTS_DICT[fig["width_class"]]

        plots_list_tmp.extend(
            [
                html.Div(
                    new_plot,
                    id={"type": "plot", "index": fig_id},
                    className=f"column {width}",
                )
            ]
        )

    return plots_list_tmp


def _add_default_plots(sess_id: str, data: Dataset) -> list:
    """
    Utility function to add default plots based on the data.

    Args:
        sess_id (str): Session ID to load the state for
        data (dict): Dict representation of xarray.Dataset

    Returns:
        list: List of default plots

    """
    deps = list(data.data_vars.keys())  # [0] # TODOLATER: remove
    indeps = list(
        data[deps[0]].coords
    )  # TODOLATER: remove - # CONCERN: complication if deps becomes a list

    fig_divs = []
    # Line Plot
    try:
        fig_divs = [
            Plot(
                sess_id=sess_id,
                data=data,
                deps=deps,
                indeps=[indeps[0]],
                fig_id=None,
                # NOTE: These must be new objects; don't use defaults
                slider={},
                filters_order=[],
                filters_opts={},
                relayout_data={},
            ).plot()
        ]
    except Exception as err:
        logger.error(f"Error in adding default LINE plot.\nError: {err}", exc_info=True)

    # If the data is multidimensional, add a HeatMap
    if len(indeps) > 1:
        try:
            fig_divs.extend(
                [
                    Plot(
                        sess_id=sess_id,
                        data=data,
                        deps=deps,
                        indeps=indeps[:2],
                        fig_id=None,
                        # NOTE: These must be new objects; don't use defaults
                        slider={},
                        filters_order=[],
                        filters_opts={},
                        relayout_data={},
                    ).plot()
                ]
            )
        except Exception as err:
            logger.error(
                f"Error in adding default HEATMAP plot.\nError: {err}", exc_info=True
            )

    return _update_plots_list(sess_id, fig_divs, [])


@callback(
    Output({"type": "plot", "index": MATCH}, "className"),
    State("session-id", "data"),
    Input({"type": "plot-width", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def update_plot_width(sess_id: str, width: str) -> str:
    """
    Callback to update the plot width based on the input value.

    Args:
        sess_id (str): Session ID to load the state for.
        width (str): Width of the plot.

    Returns:
        str: Bulma className for the plot width.

    """
    _state = load_state_from_disk(sess_id)

    # NOTE: Other plots won't be responsive when the width is changed
    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    fig_id = input_id["index"]
    logger.debug(f"update_plot_width || Width: {width}")

    if width not in PLOT_WIDTH_OPTS_DICT.keys():
        logger.error(f"update_plot_width || Invalid width: {width}")
        raise ValueError(f"Invalid width: {width}")

    fig_width_cls = PLOT_WIDTH_OPTS_DICT[width]
    className = f"column {fig_width_cls}"

    _state.plot_states[fig_id]["width_class"] = width
    _state.save_state()

    return className


@callback(
    Output("plots", "children"),
    State("session-id", "data"),
    State("dependent-dropdown", "value"),
    State("independent-dropdown", "value"),
    State("plots", "children"),
    Input("load-signal", "data"),
    Input("add-plot", "n_clicks"),
    Input("clear-all-plots", "n_clicks"),
    Input({"type": "button-plot-delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def update_plot_list(
    sess_id: str,
    dependents: str,  # TODOLATER: type, when deps is a list
    independents: list,
    plots_list: list,
    sig: int,
    *_,
) -> Tuple[list]:
    """
    Callback to add a plot to the plots container, or to update existing plots in the container.

    The container is updated under the following conditions:

    1. If the data is selected for the first time, it generates default plots based on the data.
    2. If the user adds a new plot, it generates a new plot based on the selected dependent and independent variables.
    3. If the user clears all plots, it removes all the plots from the container.
    4. If the user deletes a specific plot, it removes the plot from the container.
    5. If the user uploads new data, it updates the plots based on the new data. Filters, ranges, and appearance settings are retained.

    Args:
        sess_id (str): Session ID to load the state for
        dependents (str): Selected dependent variables. # TODOLATER: type, when deps is a list
        independents (list): Selected independent variables.
        plots_list (list): List of plots in the plots container.
        sig (int): Signal to indicate that data has been updated

    Returns:
        tuple: Updated plots list.

    """
    _state = load_state_from_disk(sess_id)

    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    data = read_data(sess_id, src="update_plot_list")
    plots_list = plots_list or []

    if "index" in input_id:
        # TODOLATER: any better way to do this? Include in match?
        # To delete a specific plot when the delete button is clicked
        delete_chart = json.loads(input_id)["index"]
        plots_list = [
            chart
            for chart in plots_list
            if f"'index': '{delete_chart}'" not in str(chart)
        ]

        _state.plot_states.pop(delete_chart, None)
        _state.save_state()
        # logger.debug(f"Deleted plot {delete_chart}.")

    match input_id:
        case "clear-all-plots":
            _state.plot_states = {}
            _state.save_state()
            plots_list = []
            logger.debug("Cleared all plots.")

        case "load-signal":
            logger.warning("case 'load-signal': New data selected. UPDATING PLOTS...")
            # NOTE: Plot() adds fig info to `_state` internally
            if _state.plot_states != {}:
                # If there are plots already present, try plotting with new data
                try:
                    fig_divs = [
                        Plot(
                            sess_id=sess_id,
                            data=data,
                            deps=fig_info["deps"],
                            indeps=fig_info["indeps"],
                            fig_id=fig_id,
                            slider=fig_info["slider"],
                            theme=fig_info["theme"],
                            filters_order=fig_info["filters_order"],
                            filters_opts=fig_info["filters_opts"],
                            plots_menu=fig_info["plots_menu"],
                            width_class=fig_info["width_class"],
                            relayout_data=fig_info["relayout_data"],
                        ).plot()
                        for fig_id, fig_info in _state.plot_states.items()
                    ]

                    plots_list = []  # NOTE: This makes _state the source of truth
                    plots_list = _update_plots_list(sess_id, fig_divs, plots_list)
                    # logger.debug("Updated plots based on EXISTING data.")
                # If KeyError is raised, e.g., "ch# does not exist", clear all plots and start fresh with default plots
                except (KeyError, ValueError) as err:
                    # logger.error(f"Error: {err}")
                    _state.plot_states = {}
                    _state.save_state()
                    # logger.warning(
                    #     "Existing data mismatch. Cleared all plots. Adding default plots."
                    # )
                    plots_list = _add_default_plots(sess_id, data)

            else:
                # If there are no plots present, add default plots
                plots_list = _add_default_plots(sess_id, data)
                # logger.debug("No EXISTING data found. Created new plots.")

        case "add-plot":
            if all([dependents, independents]):
                fig_div = Plot(
                    sess_id=sess_id,
                    data=data,
                    deps=[
                        dependents
                    ],  # TODOLATER: remove [] when deps is a proper list
                    indeps=independents,
                    fig_id=None,
                    # NOTE: These must be new objects; don't use defaults
                    slider={},
                    filters_order=[],
                    filters_opts={},
                    relayout_data={},
                ).plot()

                plots_list = _update_plots_list(sess_id, [fig_div], plots_list)
                # logger.debug("Added new plot.")
            # TODOLATER: add toast for error

    return plots_list


@callback(
    Output({"type": "plots-menu-dropdown", "index": MATCH}, "style"),
    Output({"type": "content-ranges", "index": MATCH}, "style"),
    Output({"type": "content-appearance", "index": MATCH}, "style"),
    Output({"type": "content-filters", "index": MATCH}, "style"),
    Output({"type": "button-plot-ranges", "index": MATCH}, "className"),
    Output({"type": "button-plot-appearance", "index": MATCH}, "className"),
    Output({"type": "button-plot-filters", "index": MATCH}, "className"),
    State("session-id", "data"),
    State({"type": "button-plot-ranges", "index": MATCH}, "className"),
    State({"type": "button-plot-appearance", "index": MATCH}, "className"),
    State({"type": "button-plot-filters", "index": MATCH}, "className"),
    Input({"type": "button-plot-ranges", "index": MATCH}, "n_clicks"),
    Input({"type": "button-plot-appearance", "index": MATCH}, "n_clicks"),
    Input({"type": "button-plot-filters", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def toggle_dropdown(
    sess_id: str,
    r_state: str,
    a_state: str,
    s_state: str,
    r_n_clicks: int,
    a_n_clicks: int,
    s_n_clicks: int,
) -> tuple:
    """
    Callback to toggle the dropdowns for the plot options.
    Toggles the dropdowns for the plot options when the corresponding button is clicked.
    Changes the color to `warning` when the button is active, and changes it back, when the button is clicked again.

    Args:
        sess_id (str): Session ID to load the state for
        r_state (str): State of the ranges dropdown from the class name.
        a_state (str): State of the appearance dropdown from the class name.
        s_state (str): State of the filters dropdown from the class name.

    Returns:
        tuple: Tuple of display styles and class names for the dropdowns and buttons.

    """
    _state = load_state_from_disk(sess_id)

    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button = json.loads(input_id)["type"]
    fig_id = json.loads(input_id)["index"]
    fig_plot_menu = _state.plot_states[fig_id]["plots_menu"]

    ret_styles = None

    def reset_plot_buttons():
        fig_plot_menu.update(
            {
                "ranges_n_clicks": 0,
                "ranges_cname": "button mb-2",
                "appearance_n_clicks": 0,
                "appearance_cname": "button mb-2",
                "filters_n_clicks": 0,
                "filters_cname": "button mb-2",
                "plots_menu_dropdown_disp": "none",
                "content_ranges_disp": "none",
                "content_appearance_disp": "none",
                "content_filters_disp": "none",
            }
        )
        _state.plot_states[fig_id]["plots_menu"] = fig_plot_menu
        _state.save_state()
        # logger.debug(f"Reset plot buttons. || fig_plot_menu (AFTER): {fig_plot_menu}")

        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            "button mb-2",
            "button mb-2",
            "button mb-2",
        )

    match button:
        case "button-plot-ranges":
            # logger.debug(
            #     f"Ranges button clicked. || Fig ID: {fig_id} || r_state: {r_state}"
            # )
            # Toggle off
            if r_state == "button is-warning mb-2":
                return reset_plot_buttons()

            # Toggle on
            fig_plot_menu.update(
                {
                    "ranges_n_clicks": r_n_clicks,
                    "ranges_cname": "button is-warning mb-2",
                    "appearance_n_clicks": 0,
                    "appearance_cname": "button mb-2",
                    "filters_n_clicks": 0,
                    "filters_cname": "button mb-2",
                    "plots_menu_dropdown_disp": "unset",
                    "content_ranges_disp": "unset",
                    "content_appearance_disp": "none",
                    "content_filters_disp": "none",
                }
            )
            ret_styles = (
                {"display": "unset"},
                {"display": "unset"},
                {"display": "none"},
                {"display": "none"},
                "button is-warning mb-2",
                "button mb-2",
                "button mb-2",
            )

        case "button-plot-appearance":
            # logger.debug(
            #     f"Appearance button clicked. || Fig ID: {fig_id} || a_state: {a_state}"
            # )
            # Toggle off
            if a_state == "button is-warning mb-2":
                return reset_plot_buttons()

            # Toggle on
            fig_plot_menu.update(
                {
                    "ranges_n_clicks": 0,
                    "ranges_cname": "button mb-2",
                    "appearance_n_clicks": a_n_clicks,
                    "appearance_cname": "button is-warning mb-2",
                    "filters_n_clicks": 0,
                    "filters_cname": "button mb-2",
                    "plots_menu_dropdown_disp": "unset",
                    "content_ranges_disp": "none",
                    "content_appearance_disp": "unset",
                    "content_filters_disp": "none",
                }
            )
            ret_styles = (
                {"display": "unset"},
                {"display": "none"},
                {"display": "unset"},
                {"display": "none"},
                "button mb-2",
                "button is-warning mb-2",
                "button mb-2",
            )

        case "button-plot-filters":
            # logger.debug(
            #     f"Filters button clicked. || Fig ID: {fig_id} || s_state: {s_state}"
            # )
            # Toggle off
            if s_state == "button is-warning mb-2":
                return reset_plot_buttons()

            # Toggle on
            fig_plot_menu.update(
                {
                    "ranges_n_clicks": 0,
                    "ranges_cname": "button mb-2",
                    "appearance_n_clicks": 0,
                    "appearance_cname": "button mb-2",
                    "filters_n_clicks": s_n_clicks,
                    "filters_cname": "button is-warning mb-2",
                    "plots_menu_dropdown_disp": "unset",
                    "content_ranges_disp": "none",
                    "content_appearance_disp": "none",
                    "content_filters_disp": "unset",
                }
            )
            ret_styles = (
                {"display": "unset"},
                {"display": "none"},
                {"display": "none"},
                {"display": "unset"},
                "button mb-2",
                "button mb-2",
                "button is-warning mb-2",
            )
        case _:
            reset_plot_buttons()

    _state.plot_states[fig_id]["plots_menu"] = fig_plot_menu
    _state.save_state()
    # logger.debug(f"Plot Menu (AFTER): {fig_plot_menu}")

    return ret_styles


@callback(
    Output({"index": MATCH, "type": "line-options"}, "children"),
    State("session-id", "data"),
    Input({"index": MATCH, "key": "line", "setting": "mode"}, "value"),
    prevent_initial_call=True,
)
def update_settings(sess_id: str, line_mode: list[str]) -> tuple:
    """
    Callback to update the settings based on the line mode dropdown.

    Args:
        sess_id (str): Session ID to load the state for
        line_mode (list): Selected line mode.

    Returns:
        tuple: Updated class names for the settings.

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    fig_id = input_id["index"]
    logger.debug(f"Line mode: {line_mode}")
    fig_plot_menu = _state.plot_states[fig_id]["plots_menu"]
    logger.debug(f"Line mode | fig_plot_menu (BEFORE): {fig_plot_menu}")

    ret_con = None
    match line_mode:
        case "markers":
            # Show markers only
            fig_plot_menu["appearance_line_options_disp"] = False
            fig_plot_menu["appearance_marker_options_disp"] = True
            ret_con = (appearance_marker_options(fig_id),)
        case "lines":
            # Show lines only
            fig_plot_menu["appearance_line_options_disp"] = True
            fig_plot_menu["appearance_marker_options_disp"] = False
            ret_con = (appearance_line_options(fig_id),)
        case "lines+markers":
            # Show both
            fig_plot_menu["appearance_line_options_disp"] = True
            fig_plot_menu["appearance_marker_options_disp"] = True
            ret_con = (
                appearance_line_options(fig_id),
                appearance_marker_options(fig_id),
            )
    logger.debug(f"Line mode | fig_plot_menu (AFTER): {fig_plot_menu}")
    _state.plot_states[fig_id]["plots_menu"] = fig_plot_menu
    _state.save_state()

    return ret_con


@callback(
    Output({"index": MATCH, "type": "relayout-data"}, "data"),
    State("session-id", "data"),
    Input({"index": MATCH, "type": "figure"}, "relayoutData"),
    prevent_initial_call=True,
)
def store_relayout_data(sess_id: str, relayout_data: dict) -> dict:
    """
    Callback to store the relayout data in dcc.Store to be used while exporting the plot.

    Args:
        sess_id (str): Session ID to load the state for.
        relayout_data (dict): Relayout data from the plot.

    Returns:
        dict: Relayout data.

    """
    _state = load_state_from_disk(sess_id)

    try:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        input_id = json.loads(prop_id) if prop_id else {}
    except json.JSONDecodeError:
        logger.error(
            f"JSONDecodeError: Invalid prop_id format: {ctx.triggered[0]['prop_id']}"
        )
        input_id = {}

    fig_id = input_id["index"]
    logger.debug(f"store_relayout_data | fig_id: {fig_id}")

    if relayout_data:
        logger.debug(f"store_relayout_data | relayout_data: {relayout_data}")

        # Store the relayout data in the plot state
        _state.plot_states[fig_id]["relayout_data"] = relayout_data
        _state.save_state()
        logger.debug(f"store_relayout_data | Stored relayout data for fig_id: {fig_id}")

        return relayout_data

    logger.debug(
        f"store_relayout_data | No relayout data to store for fig_id: {fig_id}"
    )
    _state.plot_states[fig_id]["relayout_data"] = {}
    _state.save_state()
    return {}


# TODOLATER: BUG: See notes.py::update_notes()
# @callback(
#     Output({"index": MATCH, "type": "notes-store"}, "data", allow_duplicate=True),
#     State({"index": MATCH, "type": "relayout-data"}, "data"),
#     State({"index": MATCH, "type": "figure"}, "figure"),
#     Input({"index": MATCH, "type": "button-plot-send-to-md"}, "n_clicks"),
#     prevent_initial_call=True,
# )
# def send_img_to_notes(
#     relayout_data: dict,
#     orig_fig: go.Figure,
#     n_clicks: int,
# ) -> str:
#     """
#     # TODO: Docs

#     """
#     # TODO: Remove some debug logs
#     logger.debug(f"Attempting image addition...")

#     logger.debug(f"relayout_data : {type(relayout_data)}")
#     logger.debug(f"orig_fig : {type(orig_fig)}")
#     logger.debug(f"n_clicks : {type(n_clicks)}")
#     logger.debug(f"n_clicks val : {n_clicks}")

#     input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
#     fig_id = input_id["index"]
#     logger.debug(f"{fig_id}: Attempting image addition...")
#     meas_path = Path(_state.measurement_path)

#     # Get current notes from disk
#     notes = _get_notes()

#     # Save to file
#     # Output directory # NOTE: Different from the one in `export_images`
#     exports_dir = meas_path.parent / meas_path.stem / "exports/notes"
#     exports_dir.mkdir(exist_ok=True)

#     # Filename
#     # NOTE: The first 8 characters of the measurement ID
#     meas_id_short = meas_path.stem[:8]
#     fig_cls = _state.plot_states[fig_id]["plot_type"]
#     filename = (
#         exports_dir
#         / f"{meas_id_short}__{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}__{fig_cls}.png"
#     )

#     if n_clicks > 0:
#         logger.debug(f"{fig_id}: Exporting images...")
#         logger.debug(f"{fig_id}: Export path: {exports_dir}")

#         try:
#             # Reload the original figure as a valid Plotly figure
#             fig = go.Figure(orig_fig)
#             # Apply the relayout changes (zoom, pan, grid/tick settings etc.)
#             if relayout_data:
#                 logger.debug(f"{fig_id}: Relayout data: {relayout_data}")
#                 fig.plotly_relayout(relayout_data)
#                 logger.debug(f"{fig_id}: Applied relayout data.")

#             # Ensure transparent background
#             fig.update_layout(
#                 paper_bgcolor="rgba(0,0,0,0)",
#                 plot_bgcolor="rgba(0,0,0,0)",
#             )

#             # TODO: @s.anupam Customize the look of the exported figures

#             # Save
#             pio.write_image(fig, f"{filename}")

#             logger.debug(
#                 f"{fig_id}: Image added to markdown. Exported to {exports_dir} as {filename}"
#             )

#             # Append centered image (using <center> tag)
#             notes += f"""
# <center>

# <img src="./exports/notes/{filename.name}" alt="{filename.name}" width="400"/>

# </center>

# """

#         except Exception as err:
#             logger.error(
#                 f"{fig_id}: Error adding to markdown.\nError: {err}", exc_info=True
#             )

#         return notes


@callback(
    Output("download-dataset", "data"),
    Input("download-dataset-btn", "n_clicks"),
    State("session-id", "data"),
    prevent_initial_call=True,
)
def download_dataset(_ddb_n_clicks: int, sess_id: str) -> dict:
    """
    Callback to download the dataset.

    Args:
        _ddb_n_clicks (int): Number of clicks on the download button.
        sess_id (str): Session ID to load the state for.

    Returns:
        dict: Data to download the dataset.

    Raises:
        PreventUpdate: If the session ID is not found or the measurement path is not set.

    """
    _state = load_state_from_disk(sess_id)
    meas_path = Path(_state.measurement_path)

    exports_dir = meas_path.parent / meas_path.stem / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    zip_dest = exports_dir.parent / f"{meas_path.stem}.zarr.zip"

    # If the zip already exists, return it
    if zip_dest.exists():
        logger.debug(
            f"download_dataset | Zipped dataset exists at {zip_dest}. Sending for download."
        )
        return dcc.send_file(zip_dest)

    # Create zip in current working directory (CWD)
    zip_name = meas_path.stem + ".zarr"
    shutil.make_archive(zip_name, "zip", root_dir=meas_path, base_dir=".")

    # Move the zip to the exports directory
    zip_src = Path.cwd() / (zip_name + ".zip")
    shutil.move(zip_src, zip_dest)

    logger.debug(f"download_dataset | Zipped folder created at {zip_dest}")

    return dcc.send_file(zip_dest)


@callback(
    # NOTE: Styled using Bulma, not Bootstrap
    Output({"index": MATCH, "type": "export-toast"}, "className"),
    Output({"index": MATCH, "type": "export-toast"}, "children"),
    Output({"index": MATCH, "type": "export-toast"}, "is_open"),
    Output({"index": MATCH, "type": "export-download"}, "data"),
    Input({"index": MATCH, "type": "button-plot-export"}, "n_clicks"),
    State({"index": MATCH, "type": "relayout-data"}, "data"),
    State({"index": MATCH, "type": "figure"}, "figure"),
    State("session-id", "data"),
    prevent_initial_call=True,
)
def export_images(
    n_clicks: int,
    relayout_data: dict,
    orig_fig: go.Figure,
    sess_id: str,
) -> Tuple[str, str, bool]:
    """
    Callback to export the figure in .svg, .png. .pdf formats in light and dark mode with relayout.
    Shows a toast notification with the export status.

    Args:
        n_clicks (int): Number of clicks on the export button.
        relayout_data (dict): Relayout data from the plot.
        orig_fig (go.Figure): Original figure.
        sess_id (str): Session ID to load the state for.

    Returns:
        Tuple[str, str, bool, dict]: Toast color, message, is_open status and download link.

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    fig_id = input_id["index"]
    logger.debug(f"export_images | {fig_id}: Attempting image export...")
    meas_path = Path(_state.measurement_path)

    # Output directory
    exports_dir = meas_path.parent / meas_path.stem / "exports"
    exports_dir.mkdir(exist_ok=True, parents=True)

    # Filenames
    # NOTE: The first 8 characters of the measurement ID
    meas_id_short = meas_path.stem[:8]
    fig_cls = _state.plot_states[fig_id]["plot_type"]
    base_filename = (
        exports_dir
        / f"{meas_id_short}__{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}__{fig_cls}"
    )
    formats = ["png", "svg"]  # , "pdf"]

    if n_clicks > 0:
        logger.debug(f"export_images | {fig_id}: Exporting images...")
        logger.debug(f"export_images | {fig_id}: Export path: {exports_dir}")

        try:
            # Reload the original figure as a valid Plotly figure
            fig = go.Figure(orig_fig)
            # Apply the relayout changes (zoom, pan, grid/tick settings etc.)
            if relayout_data:
                logger.debug(
                    f"export_images | {fig_id}: Relayout data: {relayout_data}"
                )
                fig.plotly_relayout(relayout_data)
                logger.debug(f"export_images | {fig_id}: Applied relayout data.")

            # Ensure transparent background
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )

            # TODO: @s.anupam Customize the look of the exported figures

            # NOTE: To avoid https://github.com/plotly/plotly.py/issues/3469
            # 1. Write an arbitrary .pdf plot to file first.
            # 2. Sleep for 0.2 seconds.
            # 3. Save the actual plot in each format.
            # logger.debug(f"export_images | {fig_id}: Saving arbitrary plot...")
            # arb_fig = go.Figure(data=go.Scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16]))
            # pio.write_image(arb_fig, f"{base_filename}_arbitrary.pdf")
            # sleep(2)

            # Save in each format
            for fmt in formats:
                pio.write_image(fig, f"{base_filename}.{fmt}")

            # In dark mode
            # NOTE: `plotly_dark` has some undesirable features, like missing colorbar ticks.
            # fig.update_layout(template="plotly_dark")

            # Manually set title color, border color and tick color to white
            axis_style_dark = {
                "title": {"font": {"color": "white"}},
                "linecolor": "white",
                "tickfont": {"color": "white"},
                "tickcolor": "white",
                "minor": {
                    "tickcolor": "white",
                },
            }
            fig.update_layout(
                title_font_color="white",
                xaxis=axis_style_dark,
                yaxis=axis_style_dark,
                coloraxis={
                    "colorbar": {
                        "title": {"font": {"color": "white"}},
                        "tickcolor": "white",
                        "tickfont": {"color": "white"},
                        "ticklen": 5,
                    },
                },
            )
            for fmt in formats:
                pio.write_image(fig, f"{base_filename}_dark.{fmt}")

            # Delete the arbitrary .pdf plot
            # Path(f"{base_filename}_arbitrary.pdf").unlink()
            # logger.debug(f"export_images | {fig_id}: Deleted arbitrary .pdf plot.")

            logger.debug(
                f"export_images | {fig_id}: Images exported to {exports_dir} as {', '.join(formats)}"
            )

            # Create a zipped folder
            zip_dest = exports_dir.parent / Path(meas_path.stem + "_exports.zip")
            zip_src = Path(meas_path.stem + "_exports.zip")
            if zip_dest.exists():
                logger.debug(
                    f"export_images | {fig_id}: Removing existing zipped folder at {zip_dest}"
                )
                zip_dest.unlink(missing_ok=True)

            shutil.make_archive(
                meas_path.stem + "_exports",
                format="zip",
                root_dir=exports_dir,
            )
            logger.debug(f"export_images | {fig_id}: Zipped folder created.")

            # Move the zipped folder to the measurement directory
            shutil.move(zip_src, zip_dest)
            logger.debug(f"export_images | {fig_id}: Zipped folder moved to {zip_dest}")

            return (
                "notification p-4 is-success",
                "Export successful",
                True,
                dcc.send_file(zip_dest),
            )

        except Exception as err:
            logger.error(
                f"export_images | {fig_id}: Error exporting images.\nError: {err}",
                exc_info=True,
            )

            return ("notification p-4 is-danger", "Export failed", True, None)

    return ("", "", False, None)


@callback(
    Output({"type": "figure", "index": MATCH}, "style"),
    State("session-id", "data"),
    Input("squarify-all-plots", "value"),
)
def squarify_plots(sess_id: str, squarify: bool) -> dict:
    """
    Callback to squarify the plots.

    Args:
        sess_id (str): Session ID to load the state for
        squarify (bool): Squarify all plots.

    Returns:
        dict: Style for the plots.

    """
    _state = load_state_from_disk(sess_id)

    logger.debug(f"squarify_plots() || squarify: {squarify}")

    # Update _state
    _state.squarify_plots = squarify
    _state.save_state()

    # Set the width and height of the plots
    if squarify:
        return {"width": SQUARIFY_SIZE, "height": SQUARIFY_SIZE}

    return {"width": "auto", "height": "auto"}


@callback(
    Output({"type": "figure", "index": MATCH}, "figure", allow_duplicate=True),
    State("session-id", "data"),
    State({"type": "figure", "index": MATCH}, "figure"),
    Input({"index": MATCH, "key": ALL, "setting": ALL}, "value"),
    prevent_initial_call=True,
)
def update_plot_by_type(
    sess_id: str,
    figure: dict,
    _: list,
) -> go.Figure:
    """
    Callback to update the plot appearance settings by plot type.

    Args:
        sess_id (str): Session ID to load the state for
        figure (dict): Dict representation of a go.Figure object.
        _: List of values from the dropdowns. Unused.

    Returns:
        go.Figure: Updated figure.

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    app_val = ctx.triggered[0]["value"]
    fig_id = input_id["index"]
    fig = _state.plot_states[fig_id]

    app_setting = input_id["setting"]
    key = input_id["key"]

    # Update _state
    fig["theme"][key][app_setting] = app_val
    _state.save_state()
    # logger.debug(f"Updated _state for plot {fig_id} with new appearance settings.")

    return apply_appearance_by_key(
        input_id, figure, app_val=app_val, key=key, app_setting=app_setting
    )


@callback(
    Output({"type": "figure", "index": MATCH}, "figure", allow_duplicate=True),
    State("session-id", "data"),
    State({"type": "figure", "index": MATCH}, "figure"),
    Input({"index": MATCH, "axis": ALL, "ticks": ALL, "setting": ALL}, "value"),
    prevent_initial_call=True,
)
def update_plot_axes(
    sess_id: str,
    figure: dict,
    _: list,
) -> go.Figure:
    """
    Callback to update the plot appearance settings for the axes.

    Args:
        sess_id (str): Session ID to load the state for
        figure (dict): Dict representation of a go.Figure object.
        _: List of values from the dropdowns. Unused.

    Returns:
        go.Figure: Updated figure.

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    app_val = ctx.triggered[0]["value"]
    fig_id = input_id["index"]
    fig = _state.plot_states[fig_id]

    app_setting = input_id["setting"]
    axis = input_id["axis"]
    ticks = input_id["ticks"]

    # Update _state
    fig["theme"][axis][ticks][app_setting] = app_val
    _state.save_state()
    # logger.debug(
    #     f"Updated _state for the axes of plot {fig_id} with new appearance settings."
    # )
    # logger.debug(f"theme: {fig['theme']}")

    return apply_appearance_axes(
        input_id,
        figure,
        app_val=app_val,
        axis=axis,
        ticks=ticks,
        app_setting=app_setting,
    )


@callback(
    Output({"type": "figure", "index": MATCH}, "figure", allow_duplicate=True),
    State("session-id", "data"),
    Input({"type": ALL, "index": MATCH, "menu": "ranges", "extra": ALL}, "value"),
    prevent_initial_call=True,
)
def update_plot_range(
    sess_id: str,
    range_val: float,
) -> go.Figure:
    """
    Updates the plot based on the range slider values and filter button clicks.

    Args:
        sess_id (str): Session ID to load the state for
        range_val (float): Value of the range slider

    Returns:
        go.Figure: Updated figure

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    fig_id = input_id["index"]
    fig = _state.plot_states[fig_id]
    data = read_data(sess_id, src="update_plot_range")

    slider_id = json.loads(input_id["extra"])["dim"]
    slider = fig["slider"]
    slider[slider_id]["value"] = range_val[list(slider.keys()).index(slider_id)]
    _state.save_state()

    # NOTE: Filters are applied in the Plot class
    fig_div = Plot(
        sess_id=sess_id,
        data=data,
        deps=fig["deps"],
        indeps=fig["indeps"],
        fig_id=fig_id,
        slider=slider,
        theme=fig["theme"],
        filters_order=fig["filters_order"],
        filters_opts=fig["filters_opts"],
        plots_menu=fig["plots_menu"],
        width_class=fig["width_class"],
        relayout_data=fig["relayout_data"],
    ).plot(return_div=False)

    logger.debug(f"Updated plot {fig_id} with new ranges.")
    return fig_div


@callback(
    Output({"index": MATCH, "type": "figure"}, "figure", allow_duplicate=True),
    State("session-id", "data"),
    Input({"index": MATCH, "type": ALL, "menu": "filter-opts"}, "value"),
    prevent_initial_call=True,
)
def update_filter_opts(
    sess_id: str,
    _: Any,
) -> go.Figure:
    """
    Updates the filter opts and the plot.

    Args:
        sess_id (str): Session ID to load the state for

    Returns:
        go.Figure: Updated figure.

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    app_val = ctx.triggered[0]["value"]
    fig_id = input_id["index"]
    fil_type = input_id["type"]
    data = read_data(sess_id, src="update_filter_opts")

    # Update "filters_opts" dict in _state
    fil, fil_opt = fil_type.split("-")
    fig = _state.plot_states[fig_id]
    fil_opts = fig["filters_opts"]

    # Check if corresponding filter_opts exists
    if fil not in fil_opts:
        fil_opts.update({fil: {}})
    fil_opts[fil][fil_opt] = app_val
    _state.save_state()

    logger.debug(
        f"update_filter_opts | {input_id=}, {fig_id=}, {fil_type=} {fil=} {fil_opt=} {app_val=}"
    )

    # Redo the plot with the new filter options applied,...
    # NOTE: ...depending on whether the filter is toggled on.
    # NOTE: Filters are applied in the Plot class
    fig_div = Plot(
        sess_id=sess_id,
        data=data,
        deps=fig["deps"],
        indeps=fig["indeps"],
        fig_id=fig_id,
        slider=fig["slider"],
        theme=fig["theme"],
        filters_order=fig["filters_order"],
        filters_opts=fil_opts,
        plots_menu=fig["plots_menu"],
        width_class=fig["width_class"],
        relayout_data=fig["relayout_data"],
    ).plot(return_div=False)

    logger.debug(
        f"update_filter_opts | Updated plot {fig_id} with new filters_opts: {fil_opts}."
    )
    return fig_div


@callback(
    Output({"index": MATCH, "key": "hmap", "setting": "rangecolor"}, "min"),
    Output({"index": MATCH, "key": "hmap", "setting": "rangecolor"}, "max"),
    Output({"index": MATCH, "key": "hmap", "setting": "rangecolor"}, "marks"),
    Output({"index": MATCH, "key": "hmap", "setting": "rangecolor"}, "value"),
    State("session-id", "data"),
    Input({"index": MATCH, "type": "figure"}, "figure"),
    prevent_initial_call=True,
)
def update_hmap_rangecolor_slider(
    sess_id: str,
    figure: go.Figure,
) -> Tuple[float, float, dict, list]:
    """
    Callback to update the rangecolor RangeSlider based on the HeatMap's data.

    Args:
        sess_id (str): Session ID to load the state for
        figure (go.Figure): 2D HeatMap.

    Returns:
        Tuple[float, float, dict, list]: Min, max, marks, and value of the rangecolor RangeSlider.

    """
    _state = load_state_from_disk(sess_id)
    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    fig_id = input_id["index"]
    fig_state = _state.plot_states[fig_id]

    # Get the min, max, marks, and value of the rangecolor RangeSlider from the HeatMap's data
    z = figure["data"][0]["z"]
    z = np.where(z is None, np.nan, z).astype(
        float
    )  # To avoid TypeError in case of `None` when rotating the plot
    rcol_min = np.nanmin(z)
    rcol_max = np.nanmax(z)
    rcol_marks = {
        rcol_min: f"{rcol_min:.3f}",
        rcol_max: f"{rcol_max:.3f}",
    }

    # Cross-check with the saved _state & update _state
    # NOTE: Reading from _state is needed to prevent infinite circular callback | Can't make this a proper circular callback
    # BUG: But this also leads to sliders being set to extremes on figure update.
    rcol_val = fig_state["theme"]["hmap"]["rangecolor"]
    if rcol_val is not None:
        if rcol_val[0] not in ["", None] and rcol_val[1] not in ["", None]:
            rcol_val[0] = max(float(rcol_val[0]), rcol_min)
            rcol_val[1] = min(float(rcol_val[1]), rcol_max)
    else:
        rcol_val = [rcol_min, rcol_max]
    fig_state["theme"]["hmap"]["rangecolor"] = rcol_val
    _state.save_state()

    return (
        rcol_min,
        rcol_max,
        rcol_marks,
        rcol_val,
    )


@callback(
    Output({"index": MATCH, "type": "figure"}, "figure", allow_duplicate=True),
    State("session-id", "data"),
    Input({"index": MATCH, "type": ALL, "menu": "filter-apply"}, "value"),
    prevent_initial_call=True,
)
def update_filter_apply(
    sess_id: str,
    _: Any,
) -> go.Figure:
    """
    Updates the plot based on the applied filters.

    Args:
        sess_id (str): Session ID to load the state for

    Returns:
        go.Figure: Updated figure.

    """
    _state = load_state_from_disk(sess_id)

    input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    app_val = ctx.triggered[0]["value"]
    fig_id = input_id["index"]
    fil_type = input_id["type"]
    data = read_data(sess_id, src="update_filter_apply")

    # Update "filters_order" list in _state
    # NOTE: Get the filter name (same as in filters.py::apply_filters() cases)
    fil = fil_type.split("-")[1]
    fig = _state.plot_states[fig_id]
    fil_order = fig["filters_order"]
    if fil in fil_order:
        fil_order.remove(fil)
    else:
        fil_order.extend([fil])

    # Ensures that the filters are unique & preserve order
    fil_order = [*dict.fromkeys(fil_order)]

    # Checking if corresponding filter_opts exists
    if fil not in fig["filters_opts"]:
        fig["filters_opts"].update({fil: {}})

    # Save the updated state
    _state.save_state()

    logger.debug(
        f"update_filter_apply | {input_id=}, {fig_id=}, {fil_type=} {fil=} {app_val=} {fil_order=}"
    )

    # Redo the plot with the new filters applied
    # NOTE: Filters are applied in the Plot class
    fig_div = Plot(
        sess_id=sess_id,
        data=data,
        deps=fig["deps"],
        indeps=fig["indeps"],
        fig_id=fig_id,
        slider=fig["slider"],
        theme=fig["theme"],
        filters_order=fil_order,
        filters_opts=fig["filters_opts"],
        plots_menu=fig["plots_menu"],
        width_class=fig["width_class"],
        relayout_data=fig["relayout_data"],
    ).plot(return_div=False)

    logger.debug(
        f"update_filter_apply | Updated plot {fig_id} with new filters_order: {fil_order}."
    )
    return fig_div


@callback(
    Output({"index": MATCH, "type": "figure"}, "figure", allow_duplicate=True),
    State({"index": MATCH, "key": "hmap", "setting": "textrcolmin"}, "value"),
    State({"index": MATCH, "key": "hmap", "setting": "textrcolmax"}, "value"),
    State({"index": MATCH, "type": "figure"}, "figure"),
    State("session-id", "data"),
    Input({"index": MATCH, "key": "hmap", "setting": "textrcolapply"}, "n_clicks"),
    prevent_initial_call=True,
)
def apply_hmap_rcol_textbox(
    rcol_min: float,
    rcol_max: float,
    figure: dict,
    sess_id: str,
    n_clicks: int,
    *_: Any,
) -> go.Figure:
    """
    Updates the plot based on the applied rangecolor values from the textboxes.

    Args:
        rcol_min (float): Minimum value of the rangecolor.
        rcol_max (float): Maximum value of the rangecolor.
        figure (dict): Dict representation of a go.Figure object.
        sess_id (str): Session ID to load the state for
        n_clicks (int): Number of clicks on the apply button.
        *_: Unused.

    Returns:
        go.Figure: Updated figure.

    """
    logger.debug(f"apply_hmap_rcol_textbox | {n_clicks=} | {rcol_min=} | {rcol_max=}")

    if n_clicks >= 1:
        rcol_min_empty = rcol_min in ["", None]
        rcol_max_empty = rcol_max in ["", None]

        _state = load_state_from_disk(sess_id)

        input_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        fig_id = input_id["index"]
        fig = _state.plot_states[fig_id]

        # Update _state
        fig["theme"]["hmap"]["rangecolor"] = [rcol_min, rcol_max]
        _state.save_state()
        # logger.debug(f"apply_hmap_rcol_textbox | Updated _state for HeatMap {fig_id} with new rangecolor settings.")

        logger.debug(
            f"apply_hmap_rcol_textbox | Applying rangecolor values from the textboxes to figure {fig_id}..."
        )
        fig_caxis = figure["layout"]["coloraxis"]

        # Get the min, max, marks, and value of the rangecolor RangeSlider from the HeatMap's data
        z = np.array(figure["data"][0]["z"])
        z = np.where(z is None, np.nan, z).astype(
            float
        )  # To avoid TypeError in case of `None` when rotating the plot
        z_rcol_min = np.nanmin(z)
        z_rcol_max = np.nanmax(z)

        if rcol_min_empty and rcol_max_empty:
            logger.debug(
                f"apply_hmap_rcol_textbox | {rcol_min=} and {rcol_max=} are both empty. Resetting figure..."
            )
            fig_caxis["cmin"] = z_rcol_min
            fig_caxis["cmax"] = z_rcol_max

        elif rcol_min_empty:
            logger.debug(
                f"apply_hmap_rcol_textbox | {rcol_min=} is empty. Setting rcol_max and resetting rcol_min..."
            )
            fig_caxis["cmin"] = z_rcol_min
            fig_caxis["cmax"] = rcol_max

        elif rcol_max_empty:
            logger.debug(
                f"apply_hmap_rcol_textbox | {rcol_max=} is empty. Setting rcol_min and resetting rcol_max..."
            )
            fig_caxis["cmin"] = rcol_min
            fig_caxis["cmax"] = z_rcol_max

        else:
            if rcol_min > rcol_max:
                logger.debug(
                    "apply_hmap_rcol_textbox | rcol_min is greater than rcol_max. Not updating."
                )
                raise PreventUpdate

            logger.debug(
                f"apply_hmap_rcol_textbox | {rcol_min=} and {rcol_max=} are both set. Updating figure..."
            )

            fig_caxis["cmin"] = rcol_min
            fig_caxis["cmax"] = rcol_max

        return figure

    raise PreventUpdate


@callback(
    Output({"index": MATCH, "type": "custom-hover"}, "children"),
    State({"index": MATCH, "type": "figure"}, "figure"),
    Input({"index": MATCH, "type": "figure"}, "hoverData"),
)
def show_custom_hover(figure: dict, hoverData: dict) -> str:
    """
    Callback to display the hover data in a custom format.

    Args:
        figure (dict): Dict representation of a go.Figure object.
        hoverData (dict): Hover data from the plot.

    Returns:
        str: Formatted hover data string.

    """
    if hoverData is None:
        return ""

    # logger.debug(f"show_custom_hover | Hover data: {hoverData}")

    point = hoverData["points"][0]
    x: float = point["x"]
    y: float = point["y"]

    x_label: str = figure["layout"]["xaxis"]["title"]["text"]
    y_label: str = figure["layout"]["yaxis"]["title"]["text"]

    try:
        z: float = point["z"]
        z_label: str = figure["layout"]["coloraxis"]["colorbar"]["title"]["text"]

        if z is None:
            return ""

        string = f"{x_label} = {format_number(x)} | {y_label} = {format_number(y)} | {z_label} = {format_number(z)}"
    except KeyError:
        if y is None:
            return ""

        # Expected for LinePlots
        string = f"{x_label} = {format_number(x)} | {y_label} = {format_number(y)}"

    # BUG: FIXME: Rotate filter changes labels significantly by adding LaTeX. Will look weird.
    # BUG: FIXME: Will also keep flickering with live-plots as the entire figure is replaced.
    # logger.debug(f"show_custom_hover | Updating with {string}")
    return string

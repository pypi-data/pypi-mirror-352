import json
import numpy as np
from uuid import uuid4
from datetime import datetime

import dash_daq as daq
import dash_bootstrap_components as dbc
from dash import dcc, html
from xarray import Dataset
from plotly import graph_objects as go

# Local imports
from qimchi.components.figures import QimchiFigure, HeatMap, Line
from qimchi.components.filters import apply_filters
from qimchi.components.plot_elements import (
    appearance_plot_width_dropdown,
    # appearance_axes_ranges,  # TODOLATER:
    appearance_line_dropdown,
    appearance_line_options,
    appearance_marker_options,
)
from qimchi.components.plot_filters import content_filters

from qimchi.logger import logger
from qimchi.state import (
    load_state_from_disk,
    # Plot size options
    DEFAULT_PLOT_WIDTH,
    SQUARIFY_SIZE,
    # Hmap options
    DEFAULT_HMAP_COLSCALE,
    # Line & marker options
    DEFAULT_LINE_MODE,
    DEFAULT_LINE_COLOR,
    DEFAULT_LINE_WIDTH,
    DEFAULT_LINE_OPACITY,
    DEFAULT_LINE_DASH,
    DEFAULT_LINE_SHAPE,
    DEFAULT_SPLINE_SMOOTHING,
    DEFAULT_MARKER_COLOR,
    DEFAULT_MARKER_SIZE,
    DEFAULT_MARKER_SYMBOL,
    DEFAULT_MARKER_OPACITY,
    # Grid & tick options
    DEFAULT_AXIS_TYPE,
    DEFAULT_GRID_COLOR,
    DEFAULT_TICK_COLOR,
    DEFAULT_SHOWGRID,
    DEFAULT_NTICKS,
    DEFAULT_GRID_WIDTH,
    DEFAULT_GRID_DASH,
    DEFAULT_TICK_LENGTH,
    DEFAULT_TICK_ANGLE,
    DEFAULT_TICK_WIDTH,
    AXIS_TYPE_OPTS,
    GRID_COLOR_OPTS,
    GRID_DASH_OPTS,
    TICK_COLOR_OPTS,
)


DEFAULT_THEME = {
    # NOTE: Nesting structure is NOT indicative of the actual data structure in Plotly figures
    "hmap": {
        "colorscale": DEFAULT_HMAP_COLSCALE,
        "rangecolor": None,  # NOTE: Dynamically set via callback
    },
    "line": {
        "mode": DEFAULT_LINE_MODE,
        "color": DEFAULT_LINE_COLOR,
        "width": DEFAULT_LINE_WIDTH,
        "opacity": DEFAULT_LINE_OPACITY,
        "dash": DEFAULT_LINE_DASH,
        "shape": DEFAULT_LINE_SHAPE,
        "smoothing": DEFAULT_SPLINE_SMOOTHING,
    },
    "marker": {
        "color": DEFAULT_MARKER_COLOR,
        "size": DEFAULT_MARKER_SIZE,
        "symbol": DEFAULT_MARKER_SYMBOL,
        "opacity": DEFAULT_MARKER_OPACITY,
    },
    "x": {
        "maj": {
            "showgrid": DEFAULT_SHOWGRID,
            "type": DEFAULT_AXIS_TYPE,
            "nticks": DEFAULT_NTICKS,
            "gridcolor": DEFAULT_GRID_COLOR,
            "griddash": DEFAULT_GRID_DASH,
            "gridwidth": DEFAULT_GRID_WIDTH,
            "tickcolor": DEFAULT_TICK_COLOR,
            "tickwidth": DEFAULT_TICK_WIDTH,
            "ticklen": DEFAULT_TICK_LENGTH,
            "tickangle": DEFAULT_TICK_ANGLE,
        },
        "min": {
            "showgrid": DEFAULT_SHOWGRID,
            "nticks": DEFAULT_NTICKS,
            "gridcolor": DEFAULT_GRID_COLOR,
            "griddash": DEFAULT_GRID_DASH,
            "gridwidth": DEFAULT_GRID_WIDTH,
            "tickcolor": DEFAULT_TICK_COLOR,
            "tickwidth": DEFAULT_TICK_WIDTH,
            "ticklen": DEFAULT_TICK_LENGTH,
        },
    },
    "y": {
        "maj": {
            "showgrid": DEFAULT_SHOWGRID,
            "type": DEFAULT_AXIS_TYPE,
            "nticks": DEFAULT_NTICKS,
            "gridcolor": DEFAULT_GRID_COLOR,
            "griddash": DEFAULT_GRID_DASH,
            "gridwidth": DEFAULT_GRID_WIDTH,
            "tickcolor": DEFAULT_TICK_COLOR,
            "tickwidth": DEFAULT_TICK_WIDTH,
            "ticklen": DEFAULT_TICK_LENGTH,
            "tickangle": DEFAULT_TICK_ANGLE,
        },
        "min": {
            "showgrid": DEFAULT_SHOWGRID,
            "nticks": DEFAULT_NTICKS,
            "gridcolor": DEFAULT_GRID_COLOR,
            "griddash": DEFAULT_GRID_DASH,
            "gridwidth": DEFAULT_GRID_WIDTH,
            "tickcolor": DEFAULT_TICK_COLOR,
            "tickwidth": DEFAULT_TICK_WIDTH,
            "ticklen": DEFAULT_TICK_LENGTH,
        },
    },
}


DEFAULT_PLOTS_MENU = {
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
    "appearance_line_options_disp": True,
    "appearance_marker_options_disp": True,
}


def content_ranges(
    sess_id: str, slider: dict, fig: QimchiFigure, fig_id: str
) -> html.Div:
    """
    Generates the range sliders for the plot.

    Args:
        sess_id (str): Session ID to load the state for
        slider (dict): Slider configuration
        fig (QimchiFigure): QimchiFigure object.
        fig_id (str): Unique identifier for the figure in the plot

    Returns:
        dash.html.Div: Range sliders container.

    """
    _state = load_state_from_disk(sess_id)

    if fig.num_axes == 2:
        rcol_min = float(np.nanmin(fig.data))
        rcol_max = float(np.nanmax(fig.data))
        fig_state = _state.plot_states[fig_id]
        rangecolor = fig_state["theme"]["hmap"]["rangecolor"]
        # logger.debug(f"Initial rangecolor: {rangecolor}")

        if rangecolor is not None:
            # Convert values to float safely, falling back to data min/max if conversion fails
            try:
                min_range = (
                    float(rangecolor[0]) if rangecolor[0] is not None else rcol_min
                )
                max_range = (
                    float(rangecolor[1]) if rangecolor[1] is not None else rcol_max
                )
                rangecolor[0] = max(min_range, rcol_min)
                rangecolor[1] = min(max_range, rcol_max)
            except (TypeError, ValueError):
                rangecolor = [rcol_min, rcol_max]
        else:
            rangecolor = [rcol_min, rcol_max]
        fig_state["theme"]["hmap"]["rangecolor"] = rangecolor
        _state.save_state()
        # logger.debug(f"Updated rangecolor: {rangecolor}")
        rcol_marks = {
            rcol_min: f"{rcol_min:.3f}",
            rcol_max: f"{rcol_max:.3f}",
        }

    fig_plot_menu = _state.plot_states[fig_id]["plots_menu"]
    dim_sliders = []
    for dim in slider:
        dim_sliders.append(
            html.Div(
                [
                    # 0 padding and negative margin to align the label with the slider
                    html.Div(
                        f"{dim} : ",
                        className="column is-1 p-0",
                        style={"fontWeight": "bold", "margin-top": "-0.3225rem"},
                    ),
                    dcc.Slider(
                        min=slider[dim]["min"],
                        max=slider[dim]["max"],
                        value=slider[dim]["value"],
                        marks=None,
                        updatemode="drag",
                        tooltip={
                            "placement": "bottom",
                            "always_visible": True,
                        },
                        className="column is-11",
                        id={
                            "type": "slider",
                            "index": fig_id,
                            "menu": "ranges",
                            "extra": json.dumps(
                                {
                                    "dim": dim,
                                }
                            ),
                        },
                    ),
                ],
                className="columns is-full",
            )
        )

    dim_sliders.append(
        html.Div(
            [
                dcc.Input(
                    id={
                        "index": fig_id,
                        "key": "hmap",
                        "setting": "textrcolmin",
                    },
                    type="number",
                    placeholder="Min",
                    inputMode="numeric",
                    className="input",
                    style={
                        "width": "45%",
                        "margin": "0.3rem 0.2rem 0 0",
                    },
                    persistence=True,
                    persistence_type="local",
                )
                if fig.num_axes == 2
                else None,
                dcc.Input(
                    id={
                        "index": fig_id,
                        "key": "hmap",
                        "setting": "textrcolmax",
                    },
                    type="number",
                    placeholder="Max",
                    inputMode="numeric",
                    className="input",
                    style={
                        "width": "45%",
                        "margin": "0.3rem 0 0 0.2rem",
                    },
                    persistence=True,
                    persistence_type="local",
                )
                if fig.num_axes == 2
                else None,
                html.Button(
                    html.I(className="fa-solid fa-paper-plane"),
                    id={
                        "index": fig_id,
                        "key": "hmap",
                        "setting": "textrcolapply",
                    },
                    className="button is-pulled-right",
                    style={
                        "width": "7.5%",
                        "padding": "0.65rem 1rem",
                    },
                )
                if fig.num_axes == 2
                else None,
                dcc.RangeSlider(
                    min=rcol_min,
                    max=rcol_max,
                    marks=rcol_marks,
                    value=rangecolor,
                    updatemode="drag",
                    id={
                        "index": fig_id,
                        "key": "hmap",
                        "setting": "rangecolor",
                    },
                    tooltip={"placement": "bottom"},
                    persistence=True,
                    persistence_type="local",
                    className="mx-0 my-3 px-0",
                )
                if fig.num_axes == 2
                else None,
            ],
            className="p-1",
        )
    )

    return html.Div(
        dim_sliders,
        className="column is-full",
        style={"display": fig_plot_menu["content_ranges_disp"]},
        id={"type": "content-ranges", "index": fig_id},
    )


def _grid_options(fig: QimchiFigure, fig_id: str, axis: str, ticks: str) -> html.Div:
    """
    Generates the grid options for the plot.

    Args:
        fig (QimchiFigure): QimchiFigure object.
        fig_id (str): Unique identifier for the figure in the plot.
        axis (str): Axis to apply the grid options to. Either "x" or "y".
        ticks (str): Major or minor ticks. Either "maj" or "min".

    Returns:
        dash.html.Div: Grid options container.

    """
    # Flag to disable certain options for HeatMap
    is_hmap = fig.__class__.__name__ == "HeatMap"
    # Flag to disable certain options for minor ticks
    is_min = ticks == "min"

    return html.Div(
        [
            # Tick Options
            html.Div(
                [
                    html.Label(
                        "Tick Options",
                        className="column is-full",
                        style={"fontWeight": "bold"},
                    ),
                    dcc.Dropdown(
                        id={
                            "index": fig_id,
                            "axis": axis,
                            "ticks": ticks,
                            "setting": "tickcolor",
                        },
                        options=TICK_COLOR_OPTS,
                        value=DEFAULT_TICK_COLOR,
                        placeholder="Tick Color",
                        searchable=True,
                        persistence=True,
                        persistence_type="local",
                        className="column is-full",
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Tick Length: ",
                                className="column is-one-fifth",
                                style={"fontWeight": "bold"},
                            ),
                            dcc.Slider(
                                min=0.0,
                                max=50.0,
                                step=0.5,
                                marks={0: "0", 50: "50"},
                                updatemode="drag",
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                value=DEFAULT_TICK_LENGTH,
                                id={
                                    "index": fig_id,
                                    "axis": axis,
                                    "ticks": ticks,
                                    "setting": "ticklen",
                                },
                                persistence=True,
                                persistence_type="local",
                                className="column is-four-fifths mx-0 my-2",
                            ),
                        ],
                        className="column is-flex is-one-half",
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Tick Width: ",
                                className="column is-one-fifth",
                                style={"fontWeight": "bold"},
                            ),
                            dcc.Slider(
                                min=0.0,
                                max=15.0,
                                step=0.5,
                                marks={0: "0", 15: "15"},
                                value=DEFAULT_TICK_WIDTH,
                                updatemode="drag",
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                id={
                                    "index": fig_id,
                                    "axis": axis,
                                    "ticks": ticks,
                                    "setting": "tickwidth",
                                },
                                persistence=True,
                                persistence_type="local",
                                className="column is-four-fifths mx-0 my-2",
                            ),
                        ],
                        className="column is-flex is-one-half",
                    ),
                    (
                        html.Div(
                            [
                                html.Label(
                                    "Tick Angle: ",
                                    className="column is-one-fifth",
                                    style={"fontWeight": "bold"},
                                ),
                                dcc.Slider(
                                    min=-90.0,
                                    max=90.0,
                                    step=5.0,
                                    marks={
                                        -90: "-90",
                                        -45: "-45",
                                        0: "0",
                                        45: "45",
                                        90: "90",
                                    },
                                    value=DEFAULT_TICK_ANGLE,
                                    id={
                                        "index": fig_id,
                                        "axis": axis,
                                        "ticks": ticks,
                                        "setting": "tickangle",
                                    },
                                    updatemode="drag",
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    persistence=True,
                                    persistence_type="local",
                                    className="column is-four-fifths mx-0 my-2",
                                ),
                            ],
                            className="column is-flex is-one-half",
                        )
                        if not is_min
                        else None
                    ),
                ],
                className="column is-half px-0",
            ),
            # Grid Options
            (
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    "Grid Options",
                                    className="column is-four-fifths",
                                    style={"fontWeight": "bold"},
                                ),
                                daq.ToggleSwitch(
                                    id={
                                        "index": fig_id,
                                        "axis": axis,
                                        "ticks": ticks,
                                        "setting": "showgrid",
                                    },
                                    value=DEFAULT_SHOWGRID,
                                    labelPosition="top",
                                    persistence=True,
                                    persistence_type="local",
                                    className="column is-one-fifth",
                                ),
                            ],
                            className="column is-full is-flex p-0",
                        ),
                        (
                            dcc.Dropdown(
                                id={
                                    "index": fig_id,
                                    "axis": axis,
                                    "ticks": ticks,
                                    "setting": "type",
                                },
                                options=AXIS_TYPE_OPTS,
                                value=DEFAULT_AXIS_TYPE,
                                placeholder="Axis Type",
                                searchable=True,
                                persistence=True,
                                persistence_type="local",
                                className="column is-full",
                            )
                            if not is_min
                            else None
                        ),
                        dcc.Dropdown(
                            id={
                                "index": fig_id,
                                "axis": axis,
                                "ticks": ticks,
                                "setting": "gridcolor",
                            },
                            options=GRID_COLOR_OPTS,
                            value=DEFAULT_GRID_COLOR,
                            placeholder="Grid Color",
                            searchable=True,
                            persistence=True,
                            persistence_type="local",
                            className="column is-full",
                        ),
                        dcc.Dropdown(
                            id={
                                "index": fig_id,
                                "axis": axis,
                                "ticks": ticks,
                                "setting": "griddash",
                            },
                            options=GRID_DASH_OPTS,
                            value=DEFAULT_GRID_DASH,
                            placeholder="Grid Dash",
                            clearable=False,
                            persistence=True,
                            persistence_type="local",
                            className="column is-full",
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Num Ticks: ",
                                    className="column is-one-fifth",
                                    style={"fontWeight": "bold"},
                                ),
                                dcc.Slider(
                                    min=0,
                                    max=100,
                                    step=1,
                                    marks={0: "0", 100: "100"},
                                    value=DEFAULT_NTICKS,
                                    id={
                                        "index": fig_id,
                                        "axis": axis,
                                        "ticks": ticks,
                                        "setting": "nticks",
                                    },
                                    updatemode="drag",
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    persistence=True,
                                    persistence_type="local",
                                    className="column is-four-fifths mx-0 my-2",
                                ),
                            ],
                            className="column is-flex is-one-half",
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Grid Width: ",
                                    className="column is-one-fifth",
                                    style={"fontWeight": "bold"},
                                ),
                                dcc.Slider(
                                    min=0.0,
                                    max=10.0,
                                    step=0.5,
                                    marks={0: "0", 10: "10"},
                                    value=DEFAULT_GRID_WIDTH,
                                    id={
                                        "index": fig_id,
                                        "axis": axis,
                                        "ticks": ticks,
                                        "setting": "gridwidth",
                                    },
                                    updatemode="drag",
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    persistence=True,
                                    persistence_type="local",
                                    className="column is-four-fifths mx-0 my-2",
                                ),
                            ],
                            className="column is-flex is-one-half",
                        ),
                    ],
                    className="column is-half px-0",
                )
                if not is_hmap
                else None
            ),
        ],
        className="column is-full is-flex",
    )


def content_appearance(sess_id: str, fig: QimchiFigure, fig_id: str) -> html.Div:
    """
    Generates the appearance menu for the plot.

    Args:
        sess_id (str): Session ID to load the state for
        fig (QimchiFigure): QimchiFigure object
        fig_id (str): Unique identifier for the figure in the plot

    Returns:
        dash.html.Div: Appearance menu container.

    """
    _state = load_state_from_disk(sess_id)

    logger.debug(
        f"content_appearance() | fig_id: {fig_id} | fig.num_axes: {fig.num_axes}"
    )

    fig_plot_menu = _state.plot_states[fig_id]["plots_menu"]
    general_options = dcc.Tabs(
        [
            dcc.Tab(
                label="X-Axis Major Ticks & Grids",
                className="p-1",
                children=[_grid_options(fig, fig_id, "x", "maj")],
            ),
            dcc.Tab(
                label="X-Axis Minor Ticks & Grids",
                className="p-1",
                children=[_grid_options(fig, fig_id, "x", "min")],
            ),
            dcc.Tab(
                label="Y-Axis Major Ticks & Grids",
                className="p-1",
                children=[_grid_options(fig, fig_id, "y", "maj")],
            ),
            dcc.Tab(
                label="Y-Axis Minor Ticks & Grids",
                className="p-1",
                children=[_grid_options(fig, fig_id, "y", "min")],
            ),
        ],
        id={"type": "appearance-tabs-general", "index": fig_id},
        persistence=True,
        persistence_type="local",
    )

    # For Heat Maps
    hmap_options = None
    if fig.num_axes == 2:
        colors = fig.colors

        hmap_options = html.Div(
            [
                appearance_plot_width_dropdown(fig_id),
                dcc.Dropdown(
                    options=colors,
                    id={
                        "index": fig_id,
                        "key": "hmap",
                        "setting": "colorscale",
                    },
                    value=DEFAULT_HMAP_COLSCALE,
                    placeholder="Color Scale",
                    searchable=True,
                    persistence=True,
                    persistence_type="local",
                ),
            ]
        )

    # For Line/Scatter plots
    line_options = None
    if fig.num_axes == 1:
        line_options = html.Div(
            children=[
                appearance_plot_width_dropdown(fig_id),
                # appearance_axes_ranges(fig_id), # TODOLATER:
                appearance_line_dropdown(fig_id),
                html.Div(
                    id={
                        "index": fig_id,
                        "type": "line-options",
                    },
                    children=[
                        (
                            appearance_line_options(fig_id)
                            if fig_plot_menu["appearance_line_options_disp"]
                            else None
                        ),
                        (
                            appearance_marker_options(fig_id)
                            if fig_plot_menu["appearance_marker_options_disp"]
                            else None
                        ),
                    ],
                ),
            ],
        )

    fig_cname = fig.__class__.__name__
    plot_options = dcc.Tab(
        label=f"{fig_cname} Settings",
        className="p-1",
        children=[hmap_options if fig_cname == "HeatMap" else line_options],
    )

    return html.Div(
        [
            dcc.Tabs(
                [
                    plot_options,
                    dcc.Tab(
                        label="General Settings",
                        className="p-1",
                        children=[general_options],
                    ),
                ],
                id={"type": "appearance-tabs", "index": fig_id},
                persistence=True,
                persistence_type="local",
                className="column is-full px-0 py-2",
            )
        ],
        style={"display": fig_plot_menu["content_appearance_disp"]},
        id={"type": "content-appearance", "index": fig_id},
    )


def plots_menu(sess_id: str, fig_id: str) -> list[html.Button]:
    """
    Generator for the plots menu, defining the buttons for the plot options.

    Args:
        sess_id (str): Session ID to load the state for
        fig_id (str): Unique value for associating buttons to their parent graphs

    Returns:
        list: List of buttons for the plot menu

    """
    _state = load_state_from_disk(sess_id)

    fig_plot_menu = _state.plot_states[fig_id]["plots_menu"]

    send_to_md = html.Button(
        html.I(className="fa-solid fa-clipboard-list"),
        id={"index": fig_id, "type": "button-plot-send-to-md"},
        className="button",
        disabled=True,  # TODOLATER: Enable when bug is fixed. See notes.py::update_notes()
        title="Send to Markdown",
    )

    export = html.Button(
        html.I(className="fa-solid fa-save"),
        id={"index": fig_id, "type": "button-plot-export"},
        className="button",
        title="Export Plot",
    )

    ranges = html.Button(
        html.I(className="fa-solid fa-arrow-right-arrow-left"),
        id={"index": fig_id, "type": "button-plot-ranges"},
        n_clicks=fig_plot_menu["ranges_n_clicks"],
        className=fig_plot_menu["ranges_cname"],
        title="Edit Plot Range",
    )

    appearance = html.Button(
        html.I(className="fa-solid fa-palette"),
        id={"index": fig_id, "type": "button-plot-appearance"},
        n_clicks=fig_plot_menu["appearance_n_clicks"],
        className=fig_plot_menu["appearance_cname"],
        title="Edit Plot Appearance",
    )

    filters = html.Button(
        html.I(className="fa-solid fa-meteor"),
        id={"index": fig_id, "type": "button-plot-filters"},
        n_clicks=fig_plot_menu["filters_n_clicks"],
        className=fig_plot_menu["filters_cname"],
        title="Apply Filters",
    )

    delete = html.Button(
        html.I(className="fa-solid fa-xmark"),
        id={"index": fig_id, "type": "button-plot-delete"},
        n_clicks=0,
        className="button is-danger mb-2",
        title="Delete Plot",
    )

    return [
        send_to_md,
        export,
        ranges,
        appearance,
        filters,
        delete,
    ]


def plots_menu_dropdown(sess_id: str, dropdown_options: list, fig_id: str) -> html.Div:
    """
    Dropdown container for each of the plot menu options.
    Normally hidden until the corresponding button is clicked.

    Args:
        sess_id (str): Session ID to load the state for
        dropdown_options (list): List of Buttons inside the dropdown
        fig_id (str): Unique value for associating dropdowns to their parent graphs

    Returns:
        dash.html.Div: Dropdown container

    """
    _state = load_state_from_disk(sess_id)

    fig_plot_menu = _state.plot_states[fig_id]["plots_menu"]

    return html.Div(
        html.Div(
            dropdown_options,
            className="column is-10",
            style={"display": fig_plot_menu["plots_menu_dropdown_disp"]},
            id={"type": "plots-menu-dropdown", "index": fig_id},
        ),
        className="is-flex is-justify-content-center is-align-items-center",
        style={"width": "100%"},
    )


class Plot:
    def __init__(
        self,
        sess_id: str,
        data: Dataset,
        deps: list,
        indeps: list,
        fig_id: str = None,
        slider: dict = {},
        theme: dict = DEFAULT_THEME,
        filters_order: list = [],
        filters_opts: dict = {},
        plots_menu: dict = DEFAULT_PLOTS_MENU,
        width_class: str = DEFAULT_PLOT_WIDTH,
        relayout_data: dict = {},
    ):
        """
        Main plot class; generates the plot based on the data, dependent and independent variables.

        Args:
            sess_id (str): Session ID to load the state for.
            data (xarray.Dataset): Xarray data loaded from the selected file.
            deps (list): Main dependent variable(s) to plot.
            indeps (list): Independent variables to plot.
            fig_id (str): Unique identifier for the figure in the plot.
            slider (dict, optional): Slider configuration. Defaults to {}.
            theme (dict, optional): Plot theme dictionary. Defaults to `DEFAULT_THEME`.
            filters_order (list, optional): Filters in order. Defaults to [].
            filters_opts (dict, optional): Filters options. Defaults to {}. If a filter has no options, it is {}.
            plots_menu (dict, optional): Plot menu configuration. Defaults to `DEFAULT_PLOTS_MENU`.
            width_class (str, optional): Plot width Bulma className. Defaults to `DEFAULT_PLOT_WIDTH`.
            relayout_data (dict, optional): Data to store for relayout events (Zoom, Pan, etc.). Defaults to {}.

        Raises:
            ValueError: If `indeps` or `deps` are not lists.

        """
        if not isinstance(indeps, list):
            err = "Independents must be a list"
            # logger.error(err)
            raise ValueError(err)
        if not isinstance(deps, list):
            err = "Dependents must be a list"
            # logger.error(err)
            raise ValueError(err)

        # TODOLATER: When deps is a proper list with more than 1 item, remove this hardcoding
        deps = deps[0]
        self.data_array = data[deps]

        # NOTE: These are stored in _state
        self.id = str(uuid4()) if not fig_id else fig_id
        self.indeps = indeps
        self.deps = deps
        self.theme = theme
        self.slider = slider
        self.filters_order = filters_order
        self.filters_opts = filters_opts
        self.plots_menu = plots_menu
        self.width_class = width_class
        self.relayout_data = relayout_data

        # State
        self.sess_id = sess_id
        self._state = load_state_from_disk(sess_id)

        # logger.debug(f"Plotting {self.deps} against {self.indeps} with id {self.id}")

    def _base(self) -> QimchiFigure:
        """
        Base Plotly graph generator

        Returns:
            QimchiFigure: Base Figure object of type Line or HeatMap

        Raises:
            ValueError: If the number of independent variables is greater than the number of axes.

        """

        def _update_slider():
            for dim in self.data_array.dims:
                # logger.debug(f"self.indeps | {self.indeps}")
                if dim not in self.indeps:
                    if self.slider == {} or dim not in self.slider.keys():
                        # logger.debug("Slider is empty")
                        vals = self.data_array.coords[dim].values
                        self.slider[dim] = {
                            "min": min(vals),
                            "max": max(vals),
                            "step": vals[1] - vals[0],
                            "value": min(vals),
                        }

        # Line Plot
        if len(self.indeps) == 1:
            # logger.debug(f"self.data_array.dims | {self.data_array.dims}")
            if len(self.data_array.dims) > 1:
                _update_slider()
            slider_vals = {dim: self.slider[dim]["value"] for dim in self.slider}
            data_array_subset = self.data_array.sel(**slider_vals, method="nearest")
            fig = Line(
                self.sess_id, data_array_subset, self.indeps, self.deps, self.theme
            )

        # Heat Map
        elif len(self.indeps) == 2:
            if len(self.data_array.dims) > 2:
                _update_slider()
            slider_vals = {dim: self.slider[dim]["value"] for dim in self.slider}
            data_array_subset = self.data_array.sel(**slider_vals, method="nearest")
            fig = HeatMap(
                self.sess_id, data_array_subset, self.indeps, self.deps, self.theme
            )

        else:
            err = f"Invalid number of independent variables: {len(self.indeps)}"
            # logger.error(err)
            raise ValueError(err)

        return fig

    def plot(self, return_div: bool = True) -> html.Div | go.Figure:
        """
        Creates the plot container with the plot & dropdowns, if `return_div` is True.
        Only the plot is returned, if `return_div` is False.

        Args:
            return_div (bool, optional): Whether to return the plot container or just the plot (go.Figure). Defaults to True.

        Returns:
            go.Figure | dash.html.Div: Either the plot or the plot container, depending on `return_div`.

        """
        fig: QimchiFigure = self._base()
        fig_plot: go.Figure = fig.plot()
        ID = self.id
        sess_id = self.sess_id
        _state = self._state

        _state.plot_states.update(
            {
                ID: {
                    "plot_type": fig.__class__.__name__,
                    "deps": [self.deps],  # TODOLATER: when deps is a list
                    "indeps": self.indeps,
                    # NOTE: Deep copy of theme
                    "theme": json.loads(json.dumps(self.theme)),
                    "slider": self.slider,
                    "filters_order": self.filters_order,
                    "filters_opts": self.filters_opts,
                    # NOTE: Deep copy of plots_menu
                    "plots_menu": json.loads(json.dumps(self.plots_menu)),
                    "width_class": self.width_class,
                    # NOTE: Deep copy of relayout_data
                    "relayout_data": json.loads(json.dumps(self.relayout_data)),
                }
            }
        )
        _state.save_state()

        # Filters
        logger.debug(
            f"Plot.plot() | Applying filters with new filter_opts: {self.filters_opts}"
        )
        if self.filters_order:
            fig_plot = apply_filters(
                filters_order=self.filters_order,
                filters_opts=self.filters_opts,
                fig=fig_plot,
                fig_num_axes=fig.num_axes,
            )

        if fig.__class__.__name__ == "HeatMap":
            fig.data = fig_plot.data[0]["z"]
            logger.debug(
                "Plot.plot() | Updated HeatMap data for rangecolor RangeSlider."
            )

        # Relayout
        if self.relayout_data:
            fig_plot.plotly_relayout(self.relayout_data)
            logger.debug("Plot.plot() | Applied relayout data to the figure.")
        else:
            logger.debug("Plot.plot() | No relayout data to apply.")

        if not return_div:
            logger.debug(
                f"Plot.plot() | As {return_div=}, returning only the plot (go.Figure)."
            )
            return fig_plot

        fig_cls = fig.__class__.__name__
        # is_line = fig_cls == "Line"
        style = {
            "width": SQUARIFY_SIZE if _state.squarify_plots else "auto",
            "height": SQUARIFY_SIZE if _state.squarify_plots else "auto",
        }
        fig_graph = dcc.Graph(
            figure=fig_plot,
            id={"index": ID, "type": "figure"},
            style=style,
            mathjax=True,
            # To unset the last hover label to hide the custom-hover Div when exiting hover
            clear_on_unhover=True,
            # NOTE: Animation is only for Line plots
            # BUG: Does not animate axis ranges, meaning charts can drop off the plot
            # BUG: See: https://github.com/plotly/plotly.js/issues/1687 (Probably #wontfix)
            # animate=is_line,
            # animation_options={
            #     "frame": {"redraw": False},
            #     "transition": {"duration": 500, "easing": "cubic-in-out"},
            # }
            # if is_line
            # else {},
            config={
                "editable": True,
                "edits": {
                    # TODOLATER: if needed
                    # "legendPosition": True,
                    # "legendText": True,
                    # "shapePosition": True,
                    "annotationTail": True,
                    "annotationText": False,
                    "annotationPosition": True,
                    "axisTitleText": True,
                    "colorbarTitleText": True,
                    "colorbarPosition": True,
                    "titleText": False,
                },
                "displaylogo": False,  # Hides the Plotly logo
                "toImageButtonOptions": {
                    "format": "svg",  # One of png, svg, jpeg, webp
                    "filename": f"{self.id[:8]}__{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}__{fig_cls}",
                    # TODOLATER: if needed
                    # "width": None,
                    # "height": None,
                    # "scale": 1,
                },
                # TODOLATER: if needed
                # "modeBarButtonsToAdd": [],
                # "modeBarButtonsToRemove": [],
            },
        )
        return html.Div(
            [
                html.Div(
                    [
                        # Custom hover label
                        html.Div(
                            id={"index": ID, "type": "custom-hover"},
                            style={
                                "fontFamily": "monospace",
                                "textAlign": "center",
                                "marginBottom": "4px",
                                "fontWeight": "bold",
                                "fontSize": "10px",
                                "height": "12px",
                            },
                        ),
                        fig_graph,
                        # Export download
                        dcc.Download(id={"index": ID, "type": "export-download"}),
                        # Store to save relayout information
                        dcc.Store(
                            id={
                                "index": ID,
                                "type": "relayout-data",
                            },
                            storage_type="local",
                            data=self.relayout_data if self.relayout_data else {},
                        ),
                        # Store to save notes
                        dcc.Store(
                            id={
                                "index": ID,
                                "type": "notes-store",
                            },
                            storage_type="local",
                        ),
                        # Toast to show export status
                        dbc.Toast(
                            "",
                            id={"index": ID, "type": "export-toast"},
                            header=None,
                            header_style={"display": "none"},
                            is_open=False,
                            dismissable=True,
                            duration=3000,
                            # NOTE: Styled using Bulma, not Bootstrap
                            style={
                                "position": "fixed",
                                "top": 50,
                                "right": 10,
                                "width": 350,
                            },
                        ),
                    ],
                    className="column is-11",
                ),
                html.Div(
                    plots_menu(sess_id, fig_id=ID),
                    className="column is-1 mt-auto",
                ),
                plots_menu_dropdown(
                    sess_id=sess_id,
                    dropdown_options=[
                        content_ranges(sess_id, self.slider, fig, fig_id=ID),
                        content_appearance(sess_id, fig, fig_id=ID),
                        content_filters(sess_id, fig, fig_id=ID),
                    ],
                    fig_id=ID,
                ),
            ],
            className="columns is-multiline is-full",
        )

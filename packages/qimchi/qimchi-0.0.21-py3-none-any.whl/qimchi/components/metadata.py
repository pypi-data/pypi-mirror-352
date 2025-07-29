import json
from datetime import datetime
from pathlib import Path

from dash import Input, Output, State, callback, html, dcc

# Local imports
from qimchi.components.utils import read_data
from qimchi.state import load_state_from_disk
from qimchi.logger import logger


def metadata_viewer() -> html.Div:
    """
    Metadata viewer

    Returns:
        dash.html.Div: Div element, displaying all the metadata relevant to the data

    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(id="display-session-id2"),
                    html.H5(
                        html.B("Metadata"), className="is-size-5 is-4 is-pulled-left"
                    ),
                    # Toggle button to show/hide metadata
                    html.Button(
                        html.I(className="fa-solid fa-eye-slash"),
                        id="hide-metadata",
                        className="button is-info is-pulled-right",
                    ),
                ],
                className="column is-full mt-0",
                style={
                    "minHeight": "4rem",
                },
            ),
            # Metadata viewer
            html.P(
                "",
                className="column is-full mt-0",
                id="metadata-viewer",
            ),
        ],
        className="has-background-light",
    )


def _render_tree(data: dict) -> html.Ul | html.Span:
    """
    Recursive function to render collapsible items

    """
    if isinstance(data, dict):
        return html.Ul(
            [
                html.Li(
                    # If the value is an empty list, empty string, empty dict, or None, render as "key: value" without a collapsible arrow
                    (
                        html.Span(
                            [
                                html.Strong(f"{key}", style={"color": "black"}),
                                f": {value}",
                            ]
                        )
                        if value in [None, [], "", {}]
                        else (
                            html.Span(
                                [
                                    html.Strong(f"{key}", style={"color": "black"}),
                                    f": {value}",
                                ]
                            )
                            if not isinstance(value, dict)
                            # Otherwise, make it collapsible, if it's a dictionary
                            else html.Details(
                                [
                                    html.Summary(
                                        html.Strong(key, style={"color": "black"}),
                                        style={"cursor": "pointer"},
                                    ),
                                    _render_tree(
                                        value
                                    ),  # NOTE: Recursively render nested dicts
                                ]
                            )
                        )
                    ),
                    style={
                        "listStyleType": "none",
                        "marginLeft": "20px",
                    },  # No bullets, indented
                )
                for key, value in data.items()
            ],
            style={"paddingLeft": "0px"},
        )
    else:
        # Render non-dict values directly as strings in a span
        return html.Span(str(data))


@callback(
    Output("metadata-viewer", "children"),
    State("session-id", "data"),
    Input("load-signal", "data"),
)
def update_metadata_viewer(sess_id: str, sig: int) -> list:
    """
    Callback to update metadata viewer

    Args:
        sess_id (str): Session ID to load the state for
        sig (int): Signal to indicate that data has been updated

    Returns:
        list: Metadata list to be displayed in the metadata viewer

    """
    _state = load_state_from_disk(sess_id)

    if sig in [None, 0]:
        logger.warning("update_metadata_viewer | No data selected")
        return f"Session ID: {sess_id} | No Data Selected"

    data = read_data(sess_id, src="update_metadata_viewer")
    metadata = data.attrs

    try:
        dt = datetime.fromisoformat(metadata["Timestamp"])
        meta = []
        meta.append(html.B(f"Session ID: {sess_id}"))
        meta.append(html.Br())
        meta_expandable = []

        keys_order = [
            "Timestamp",
            "Cryostat",
            "Wafer ID",
            "Device Type",
            "Sample Name",
            "Experiment Name",
            "Measurement ID",
            "Sweeps",
            "Extra Metadata",
            "Instruments Snapshot",
            "Parameters Snapshot",
        ]
        # Sort keys in the order defined above
        metadata = {k: metadata[k] for k in keys_order if k in metadata}

        json_keys = [
            "Sweeps",
            "Extra Metadata",
            "Instruments Snapshot",
            "Parameters Snapshot",
        ]

        # Store "Parameters Snapshot" in _state
        if "Parameters Snapshot" in metadata:
            _state.parameters_snapshot = metadata["Parameters Snapshot"]
            _state.save_state()

        for key in metadata:
            if key == "Timestamp":
                meta.append(html.B(f"{key}: "))
                meta.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
                meta.append(html.Br())

            elif key == "Cryostat":
                meta.append(html.B(f"{key}: "))
                data = metadata[key].capitalize()
                meta.append(data)
                meta.append(html.Br())

            elif key in json_keys:
                try:
                    data: str = metadata[key]
                    data: dict = json.loads(data)
                except Exception as err:
                    logger.error(
                        f"update_metadata_viewer | Error: {err}", exc_info=True
                    )
                    raise err

                # If dict is empty, skip the key
                if not data:
                    logger.debug(
                        f"update_metadata_viewer | Key: '{key}' is empty; skipping rendering."
                    )
                    continue

                meta_expandable.append(html.B(f"{key}: "))
                for k, v in data.items():  # key: str | val: dict
                    meta_expandable.append(
                        html.Details(
                            [
                                html.Summary(
                                    html.Strong(
                                        f"{k.upper()}", style={"color": "black"}
                                    ),
                                    style={"cursor": "pointer"},
                                ),
                                # BUG: Instruments Snapshot rendering too slow because it's too big
                                # FIXME: This is a workaround to render the Instruments Snapshot as a string
                                _render_tree(
                                    str(v) if key == "Instruments Snapshot" else v
                                ),
                            ],
                            className="ml-4",
                        ),
                    )

            else:
                meta.append(html.B(f"{key}: "))
                meta.append(metadata[key])
                meta.append(html.Br())

        # Full path to the current dataset with a download button
        meta.extend(
            [
                dcc.Clipboard(
                    content=str(Path(_state.measurement_path).resolve()),
                    title="Copy Path",
                    className="button is-info is-small",
                    style={
                        "height": "2rem",
                        "width": "2.5rem",
                    },
                ),
                dcc.Download(id="download-dataset"),
                html.Button(
                    html.I(className="fa-solid fa-download"),
                    id="download-dataset-btn",
                    title="Download Dataset",
                    className="button is-info is-small",
                    style={
                        "height": "2rem",
                        "width": "2.5rem",
                    },
                ),
                html.Br(),
            ]
        )

        # Non-collapsible stuff to the left & collapsible stuff to the right
        meta = html.Div(
            [
                html.Div(meta, style={"float": "left", "width": "50%"}),
                html.Div(meta_expandable, style={"float": "right", "width": "50%"}),
            ]
        )

        return meta

    except Exception as err:
        logger.error(f"update_metadata_viewer | Error: {err}", exc_info=True)
        return f"Session ID: {sess_id} | No readable metadata found!"


@callback(
    Output("metadata-viewer", "className"),
    Output("hide-metadata", "children"),
    Input("hide-metadata", "n_clicks"),
)
def show_hide_metadata(n_clicks: int) -> tuple:
    """
    Callback to show or hide the metadata viewer

    Args:
        n_clicks (int): Number of times the button has been clicked

    Returns:
        tuple: className to display the metadata viewer and the updated button icon

    """
    if n_clicks is None or n_clicks % 2 == 0:
        return "column is-full mt-0", html.I(className="fa-solid fa-eye-slash")
    else:
        return "column is-hidden mt-0", html.I(className="fa-solid fa-eye")

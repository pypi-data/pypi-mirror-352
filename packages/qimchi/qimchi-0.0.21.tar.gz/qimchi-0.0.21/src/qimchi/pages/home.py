import dash
from dash import html, dcc

from qimchi.components.notes import notes_viewer
from qimchi.components.metadata import metadata_viewer
from qimchi.components.navbar import navbar
from qimchi.components.plot_callbacks import plot_selector, plots_container
from qimchi.components.selector import data_selector

dash.register_page(__name__, path="/")
content = html.Div([plot_selector(), plots_container()], className="content p-5")


layout = html.Div(
    [
        # Store to keep track of sessions
        dcc.Store(id="session-id", storage_type="session"),
        html.Div(id="display-session-id"),
        # Main layout of the app
        navbar(),
        data_selector(),
        html.Div(
            [
                metadata_viewer(),
                notes_viewer(),
            ]
        ),
        content,
    ],
    **{"data-theme": "light"},
)

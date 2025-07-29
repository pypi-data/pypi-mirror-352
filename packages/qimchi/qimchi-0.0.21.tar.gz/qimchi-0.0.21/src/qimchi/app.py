"""
Author: Spandan Anupam
Affiliation: Forschungszentrum Jülich GmbH

"""

from dash import Dash, Input, Output
from starlette.applications import Starlette
from starlette.middleware.wsgi import WSGIMiddleware


external_scripts = []
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css",
]

app = Dash(
    __name__,
    assets_folder="./assets",
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
    use_pages=True,
    title="Qimchi",
    update_title=None,
    suppress_callback_exceptions=True,
)

# Inject a script to set a unique session ID in sessionStorage (runs instantly)
app.index_string = """
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>Qimchi</title>
            {%favicon%}
            {%css%}
            <script>
                // Only generate once per tab
                if (!sessionStorage.getItem('tabSessionID')) {
                    sessionStorage.setItem('tabSessionID', Math.random().toString(36).substr(2, 9));
                }
            </script>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    """

# Clientside callback to retrieve that ID from sessionStorage into Dash
app.clientside_callback(
    """
    function(n) {
        return sessionStorage.getItem('tabSessionID');
    }
    """,
    Output("session-id", "data"),
    Input("display-session-id", "n_clicks"),  # dummy input to trigger once
)


"""
Entry point for running the Starlette app with Dash.

"""
server = app.server

asgi_app = Starlette()
asgi_app.mount("/", WSGIMiddleware(server))

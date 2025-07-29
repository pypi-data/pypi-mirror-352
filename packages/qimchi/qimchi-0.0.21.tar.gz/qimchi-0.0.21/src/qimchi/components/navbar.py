from dash import html


def navbar():
    """
    Navbar component

    Returns:
        dash.html.Nav: Navbar component
    """
    return html.Nav(
        html.Div(
            [
                # Left: SQUAD logo
                html.A(
                    html.Img(
                        src="../assets/logos/SQUAD Logo.webp",
                        alt="SQUAD Lab Logo",
                        id="squad-logo",
                        style={
                            "height": "2.5rem",
                            "width": "auto",
                            "paddingLeft": "0.2rem",
                            "flexShrink": "0",
                        },
                    ),
                    href="https://squad-lab.org",
                    className="navbar-item",
                ),
                # Right: Qimchi text and logo (vertically aligned)
                html.A(
                    html.Div(
                        [
                            html.Span("Qimchi."),
                            html.Img(
                                src="../assets/logos/qimchi-logo.png",
                                alt="Qimchi Logo",
                                id="qimchi-logo",
                                style={
                                    "height": "2.5rem",
                                    "width": "auto",
                                    "paddingLeft": "0.5rem",
                                    "flexShrink": "0",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                    href="./",
                    className="navbar-item",
                    style={
                        "whiteSpace": "nowrap",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "paddingRight": "0.5rem",
                    },
                ),
            ],
            className="navbar-container is-flex is-justify-content-space-between is-align-items-center",
            style={
                "width": "100%",
                # "padding": "0.5rem 1rem",
            },
        ),
        className="navbar is-transparent",
        id="navbar",
        **{"data-theme": "light"},
    )

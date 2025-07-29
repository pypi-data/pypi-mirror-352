import json
import numpy as np
from abc import ABC, abstractmethod
from xarray import Dataset

from plotly.express import colors, imshow, line
from plotly.express.colors import named_colorscales
from plotly import graph_objects as go

# Local imports
from qimchi.logger import logger
from qimchi.state import load_state_from_disk


class QimchiFigure(ABC):
    def __init__(
        self,
        sess_id: str,
        data: Dataset | np.ndarray,
        independents: list,
        dependents: list,
        num_axes: int,
        colors=None,
        theme: dict = None,
    ) -> None:
        """
        Qimchi Figure Base Class

        Args:
            sess_id (str): Session ID to load the state for
            data (Dataset | np.ndarray): Data to be plotted
            independents (list): Independent variables
            dependents (list): Dependent variables
            num_axes (int): Number of axes in the figure
            colors (list, optional): Colors for the plot. Defaults to None.
            theme (dict, optional): Theme dict for the plot. Defaults to None.

        Raises:
            ValueError: If the number of independent variables is greater than the number of axes.

        """
        self._state = _state = load_state_from_disk(sess_id)

        self.data = data
        self.metadata = (
            _state.parameters_snapshot
            if isinstance(_state.parameters_snapshot, dict)
            else json.loads(_state.parameters_snapshot)
        )

        # logger.debug(f"QimchiFigure || {self.metadata=}")
        # logger.debug(f"QimchiFigure || {self.metadata.keys()=}")
        self.ind = independents
        self.deps = dependents
        self.colors = colors
        self.theme = theme
        self.num_axes = num_axes

        if len(self.ind) > self.num_axes:
            raise ValueError(
                f"Line plot can only have {self.num_axes} independent variable"
            )
        if type(self.deps) is list and len(self.deps) > 1:
            err = "Plots can only have one dependent variable."
            logger.error(err)
            raise ValueError(err)

    @abstractmethod
    def plot(self) -> go.Figure:
        """
        Abstract method to plot the figure.

        Returns:
            go.Figure: Plotly Figure object

        """


class Line(QimchiFigure):
    """
    Qimchi Line Plot Class

    """

    def __init__(
        self,
        sess_id: str,
        data: Dataset,
        independents: list,
        dependents: list,
        theme: dict,
    ) -> None:
        super().__init__(
            sess_id, data, independents, dependents, theme=theme, num_axes=1
        )
        self.traces = {
            "mode": theme["line"]["mode"],
            "line": {
                "color": theme["line"]["color"],
                "width": theme["line"]["width"],
                "dash": theme["line"]["dash"],
                "shape": theme["line"]["shape"],
                "smoothing": theme["line"]["smoothing"],
            },
            "marker": {
                "symbol": theme["marker"]["symbol"],
                "size": theme["marker"]["size"],
                "color": theme["marker"]["color"],
                "opacity": theme["marker"]["opacity"],
            },
            "opacity": theme["line"]["opacity"],
            # Update hover template to match the axis labels
            "hovertemplate": f"{self.metadata[self.ind[0]]['label']} ({self.metadata[self.ind[0]]['unit']}): %{{x}}<br>"
            f"{self.metadata[self.deps]['label']} ({self.metadata[self.deps]['unit']}): %{{y}}<extra></extra>",
            # NOTE: "<extra></extra>" is required to remove the trace index from the hover info
        }

        logger.debug(
            f"Line || independents: {independents} | dependent: {dependents}"  # | theme: {theme}"
        )
        # logger.debug(
        #     f"Line || self.data.coords : {self.data.coords}"  # | self.data.data : {self.data.data}"
        # )

    def plot(self) -> go.Figure:
        _state = self._state
        theme = self.theme
        layout = {
            "title": {
                "text": f"{_state.device_type} {_state.wafer_id} {_state.device_id} {_state.measurement}",
                "font": dict(
                    family="Roboto, sans-serif",
                    size=10,
                    color="rgba(0,0,0,0.6)",
                ),
                "x": 0.5,
                "y": 0.97,
            },
            "xaxis": {
                # TODOLATER: Dynamic unit - scientific notation - change only on plot, not state
                "title": f"{self.metadata[self.ind[0]]['label']} ({self.metadata[self.ind[0]]['unit']})",
                "ticks": "outside",
                "showline": True,
                "mirror": True,
                "automargin": True,
                "zeroline": False,
                "linewidth": 2,
                # Customizable
                "showgrid": theme["x"]["maj"]["showgrid"],
                "type": theme["x"]["maj"]["type"],
                "nticks": theme["x"]["maj"]["nticks"],
                "griddash": theme["x"]["maj"]["griddash"],
                "gridcolor": theme["x"]["maj"]["gridcolor"],
                "gridwidth": theme["x"]["maj"]["gridwidth"],
                "tickcolor": theme["x"]["maj"]["tickcolor"],
                "tickwidth": theme["x"]["maj"]["tickwidth"],
                "ticklen": theme["x"]["maj"]["ticklen"],
                "tickangle": theme["x"]["maj"]["tickangle"],
                "minor": {
                    "showgrid": theme["x"]["min"]["showgrid"],
                    "nticks": theme["x"]["min"]["nticks"],
                    "griddash": theme["x"]["min"]["griddash"],
                    "gridcolor": theme["x"]["min"]["gridcolor"],
                    "gridwidth": theme["x"]["min"]["gridwidth"],
                    "tickcolor": theme["x"]["min"]["tickcolor"],
                    "tickwidth": theme["x"]["min"]["tickwidth"],
                    "ticklen": theme["x"]["min"]["ticklen"],
                },
            },
            "yaxis": {
                # TODOLATER: Dynamic unit - scientific notation - change only on plot, not state
                "title": f"{self.metadata[self.deps]['label']} ({self.metadata[self.deps]['unit']})",
                "ticks": "outside",
                "showline": True,
                "mirror": True,
                "exponentformat": "e",
                "automargin": True,
                "zeroline": False,
                "linewidth": 2,
                # Customizable
                "showgrid": theme["y"]["maj"]["showgrid"],
                "type": theme["y"]["maj"]["type"],
                "nticks": theme["y"]["maj"]["nticks"],
                "griddash": theme["y"]["maj"]["griddash"],
                "gridcolor": theme["y"]["maj"]["gridcolor"],
                "gridwidth": theme["y"]["maj"]["gridwidth"],
                "tickcolor": theme["y"]["maj"]["tickcolor"],
                "tickwidth": theme["y"]["maj"]["tickwidth"],
                "ticklen": theme["y"]["maj"]["ticklen"],
                "tickangle": theme["y"]["maj"]["tickangle"],
                "minor": {
                    "showgrid": theme["y"]["min"]["showgrid"],
                    "nticks": theme["y"]["min"]["nticks"],
                    "griddash": theme["y"]["min"]["griddash"],
                    "gridcolor": theme["y"]["min"]["gridcolor"],
                    "gridwidth": theme["y"]["min"]["gridwidth"],
                    "tickcolor": theme["y"]["min"]["tickcolor"],
                    "tickwidth": theme["y"]["min"]["tickwidth"],
                    "ticklen": theme["y"]["min"]["ticklen"],
                },
            },
            "font": {
                "size": 12,
            },
            "margin": {"l": 50, "r": 10, "t": 40, "b": 50},
        }

        dat = self.data
        fig = line(
            dat.data,
            x=dat.coords[self.ind[0]],
            y=dat,
        )
        fig.update_layout(layout)
        fig.update_traces(
            self.traces,
            # NOTE: Hide default hover box
            # NOTE: Comment these out and uncomment hovertemplate to show default hover box
            hoverinfo="none",
            hovertemplate=None,  # No native hover box
        )
        logger.debug("Line || PLOTTED")

        return fig


class HeatMap(QimchiFigure):
    """
    Qimchi HeatMap Plot Class

    """

    def __init__(
        self,
        sess_id: str,
        data: Dataset,
        independents: list,
        dependents: list,
        theme: dict,
    ) -> None:
        super().__init__(
            sess_id, data, independents, dependents, theme=theme, num_axes=2
        )
        self.colors = named_colorscales()
        self.colorscale = theme["hmap"]["colorscale"]
        self.rangecolor = theme["hmap"]["rangecolor"]
        data_min = float(data.min(skipna=True).values)
        data_max = float(data.max(skipna=True).values)

        if self.rangecolor is not None:
            # Convert values to float safely, falling back to data min/max if conversion fails
            try:
                min_range = (
                    float(self.rangecolor[0])
                    if self.rangecolor[0] is not None
                    else data_min
                )
                max_range = (
                    float(self.rangecolor[1])
                    if self.rangecolor[1] is not None
                    else data_max
                )
                self.rangecolor[0] = max(min_range, data_min)
                self.rangecolor[1] = min(max_range, data_max)
            except (TypeError, ValueError):
                self.rangecolor = [data_min, data_max]
        else:
            self.rangecolor = [data_min, data_max]
        self.theme["hmap"]["rangecolor"] = self.rangecolor

        logger.debug(
            f"HeatMap || independents: {independents} | dependent: {dependents}"  # | theme: {theme}"
        )
        # logger.debug(
        #     f"HeatMap || self.data.coords : {self.data.coords}"  # | self.data.data : {self.data.data}"
        # )

    def plot(self) -> go.Figure:
        _state = self._state
        theme = self.theme
        layout = {
            "title": {
                "text": f"{_state.device_type} {_state.wafer_id} {_state.device_id} {_state.measurement}",
                "font": dict(
                    family="Roboto, sans-serif",
                    size=10,
                    color="rgba(0,0,0,0.6)",
                ),
                "x": 0.5,
                "y": 0.97,
            },
            "xaxis": {
                # TODOLATER: Dynamic unit - scientific notation - change only on plot, not state
                "title": f"{self.metadata[self.ind[1]]['label']} ({self.metadata[self.ind[1]]['unit']})",
                "ticks": "outside",
                "showline": True,
                "mirror": True,
                "automargin": True,
                "zeroline": False,
                "linewidth": 2,
                "showgrid": False,
                # Customizable
                "nticks": theme["x"]["maj"]["nticks"],
                "tickcolor": theme["x"]["maj"]["tickcolor"],
                "tickwidth": theme["x"]["maj"]["tickwidth"],
                "ticklen": theme["x"]["maj"]["ticklen"],
                "tickangle": theme["x"]["maj"]["tickangle"],
                "minor": {
                    "nticks": theme["x"]["min"]["nticks"],
                    "tickcolor": theme["x"]["min"]["tickcolor"],
                    "tickwidth": theme["x"]["min"]["tickwidth"],
                    "ticklen": theme["x"]["min"]["ticklen"],
                },
            },
            "yaxis": {
                # TODOLATER: Dynamic unit - scientific notation - change only on plot, not state
                "title": f"{self.metadata[self.ind[0]]['label']} ({self.metadata[self.ind[0]]['unit']})",
                "ticks": "outside",
                "showline": True,
                "mirror": True,
                "automargin": True,
                "zeroline": False,
                "linewidth": 2,
                "showgrid": False,
                # Customizable
                "nticks": theme["y"]["maj"]["nticks"],
                "tickcolor": theme["y"]["maj"]["tickcolor"],
                "tickwidth": theme["y"]["maj"]["tickwidth"],
                "ticklen": theme["y"]["maj"]["ticklen"],
                "tickangle": theme["y"]["maj"]["tickangle"],
                "minor": {
                    "nticks": theme["y"]["min"]["nticks"],
                    "tickcolor": theme["y"]["min"]["tickcolor"],
                    "tickwidth": theme["y"]["min"]["tickwidth"],
                    "ticklen": theme["y"]["min"]["ticklen"],
                },
            },
            "font": {
                "size": 12,
            },
            "coloraxis": {
                "colorbar_title": f"{self.metadata[self.deps]['label']} ({self.metadata[self.deps]['unit']})",
                "colorscale": colors.get_colorscale(self.colorscale),
                "cmin": self.rangecolor[0],
                "cmax": self.rangecolor[1],
                "colorbar": {
                    "exponentformat": "e",  # TODOLATER: Autoscaling Units # CONCERN: Why not "SI"?
                    "ticklen": 5,
                    "outlinewidth": 2,
                    # Colorbar height settings
                    "lenmode": "fraction",
                    "len": 0.9,
                    "y": 0.5,
                    "yanchor": "middle",
                },
            },
            "margin": {"l": 50, "r": 10, "t": 40, "b": 50},
        }

        if _state.squarify_plots:
            # NOTE: See: https://github.com/plotly/plotly.py/issues/70. They recommend setting height and width.
            # NOTE: Preset height-width pairs for squarify. Not responsive.
            layout["xaxis"]["constrain"] = "domain"
            layout["xaxis"]["scaleanchor"] = "y"
            layout["xaxis"]["scaleratio"] = 1
            layout["yaxis"]["constrain"] = "domain"
            layout["yaxis"]["scaleanchor"] = "x"
            layout["yaxis"]["scaleratio"] = 1
            # logger.debug("HeatMap || Squarified!")

        if self.data.data.shape[0] != self.data.coords[self.ind[0]].shape[0]:
            self.data = self.data.T

        fig = imshow(
            self.data.transpose(self.ind[0], self.ind[1]),
            x=self.data.coords[self.ind[1]],
            y=self.data.coords[self.ind[0]],
            origin="lower",  # Moves origin to lower left
        )
        fig.update_layout(layout)
        # Update hover template to match the axis labels
        fig.update_traces(
            # NOTE: Hide default hover box
            # NOTE: Comment these out and uncomment hovertemplate to show default hover box
            hoverinfo="none",
            hovertemplate=None,  # No native hover box
            # hovertemplate=f"{self.metadata[self.ind[1]]['label']} ({self.metadata[self.ind[1]]['unit']}): %{{x}}<br>"
            # f"{self.metadata[self.ind[0]]['label']} ({self.metadata[self.ind[0]]['unit']}): %{{y}}<br>"
            # f"{self.metadata[self.deps]['label']} ({self.metadata[self.deps]['unit']}): %{{z}}<extra></extra>",
            # # NOTE: "<extra></extra>" is required to remove the trace index from the hover info
        )
        logger.debug("HeatMap || PLOTTED")

        return fig

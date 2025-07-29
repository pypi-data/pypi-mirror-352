# =======================================================================
#
#  This file is part of WebWidgets, a Python package for designing web
#  UIs.
#
#  You should have received a copy of the MIT License along with
#  WebWidgets. If not, see <https://opensource.org/license/mit>.
#
#  Copyright(C) 2025, mlaasri
#
# =======================================================================

from .container import Container
from enum import auto, Enum
from webwidgets.compilation.html.html_tags import Div


class Direction(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


class Box(Container):
    """A widget that lays out its child widgets inside a row or a column.
    """

    def __init__(self, direction: Direction):
        """Creates a new Box with the given direction.

        :param direction: The direction in which the child widgets should be
            laid out. Can be either `Direction.HORIZONTAL` or
            `Direction.VERTICAL`.
        :type direction: Direction
        """
        super().__init__()
        self.direction = direction

    def build(self):
        """Builds the HTML representation of the Box.

        The box is constructed as a `<div>` element with a flexbox layout. Its
        `flex-direction` property is set to either "row" or "column" based on
        the direction parameter, and it has a `data-role` attribute of "box".

        Each child widget is wrapped inside its own `<div>` element with a
        `data-role` attribute of "box-item". The items are centered within
        their own `<div>`.
        """
        # Building child nodes
        nodes = [w.build() for w in self.widgets]

        # Building box items that wrap around child nodes
        items = [Div(
            children=[node],
            attributes={"data-role": "box-item"},
            style={
                "display": "flex",
                "flex-direction": "row",
                "align-items": "center",
                "justify-content": "center",
                "flex-grow": "1"
            }) for node in nodes]

        # Assembling the box
        flex_dir = "row" if self.direction == Direction.HORIZONTAL else "column"
        box = Div(children=items, attributes={"data-role": "box"}, style={
            "display": "flex",
            "flex-direction": flex_dir
        })
        return box

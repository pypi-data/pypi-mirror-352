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

import numpy as np
import pytest
from typing import Tuple
import webwidgets as ww
from webwidgets.compilation.html import Div


class TestBox:

    # A simple color widget
    class Color(ww.Widget):
        def __init__(self, color: Tuple[int, int, int]):
            super().__init__()
            self.color = color

        def build(self):
            hex_color = "#%02x%02x%02x" % self.color
            return Div(style={"background-color": hex_color,
                              "height": "100%",
                              "width": "100%"})

    # A Box that fills the entire viewport
    class FullSizedBox(ww.Box):
        def build(self, *args, **kwargs):
            node = super().build(*args, **kwargs)
            node.style["width"] = "100vw"
            node.style["height"] = "100vh"
            return node

    @pytest.mark.parametrize("colors", [
        [(255, 0, 0)],
        [(255, 0, 0), (0, 255, 0)],
        [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    ])
    def test_horizontal_box(self, colors, render_page, web_drivers):
        """Tests the even distribution of multiple colored widgets by a Box."""
        # Creating a page with one box containing widgets with the given colors
        box = TestBox.FullSizedBox(direction=ww.Direction.HORIZONTAL)
        for color in colors:
            box.add(TestBox.Color(color=color))
        page = ww.Page([box])

        for web_driver in web_drivers:

            # Rendering the page with the box
            array = render_page(page, web_driver)

            # Computing the regions where to search for each color. If the
            # colors cannot spread evenly (which happens when the image size is
            # not divisible by the number of colors), we exclude all edges
            # where one color stops and another starts.
            all_indices = np.arange(array.shape[1])
            edges = np.linspace(0, array.shape[1], len(colors) + 1)[1:-1]
            edges = np.floor(edges).astype(np.int32)
            regions = np.split(all_indices, edges)
            if array.shape[1] % len(colors) != 0:
                regions = [r[~np.isin(r, edges)] for r in regions]

            assert len(regions) == len(colors)  # One region per color
            for color, region in zip(colors, regions):
                assert np.all(array[:, region, 0] == color[0])
                assert np.all(array[:, region, 1] == color[1])
                assert np.all(array[:, region, 2] == color[2])

    @pytest.mark.parametrize("colors", [
        [(255, 0, 0)],
        [(255, 0, 0), (0, 255, 0)],
        [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    ])
    def test_vertical_box(self, colors, render_page, web_drivers):
        """Tests the even distribution of multiple colored widgets by a Box."""
        # Creating a page with one box containing widgets with the given colors
        box = TestBox.FullSizedBox(direction=ww.Direction.VERTICAL)
        for color in colors:
            box.add(TestBox.Color(color=color))
        page = ww.Page([box])

        for web_driver in web_drivers:

            # Rendering the page with the box
            array = render_page(page, web_driver)

            # Computing the regions where to search for each color. If the
            # colors cannot spread evenly (which happens when the image size is
            # not divisible by the number of colors), we exclude all edges
            # where one color stops and another starts.
            all_indices = np.arange(array.shape[0])
            edges = np.linspace(0, array.shape[0], len(colors) + 1)[1:-1]
            edges = np.floor(edges).astype(np.int32)
            regions = np.split(all_indices, edges)
            if array.shape[0] % len(colors) != 0:
                regions = [r[~np.isin(r, edges)] for r in regions]

            assert len(regions) == len(colors)  # One region per color
            for color, region in zip(colors, regions):
                assert np.all(array[region, :, 0] == color[0])
                assert np.all(array[region, :, 1] == color[1])
                assert np.all(array[region, :, 2] == color[2])

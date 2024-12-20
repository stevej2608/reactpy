from __future__ import annotations
import logging
from os import environ

from reactpy import html
from reactpy.core.component import component
from reactpy.core.types import VdomDict

logger = logging.getLogger(__name__)

@component
def SubComponent(url):
    return html.a(
        {"href": url, "target": "_blank"},
        "here",
    )

@component
def SampleApp() -> VdomDict:
    logger.info('SampleApp REACTPY_DEBUG_MODE=%s', environ.get("REACTPY_DEBUG_MODE"))
    return html.div(
        {"id": "sample", "style": {"padding": "15px"}},
        html.h1("Sample Application"),
        html.p(
            "This is a basic application made with ReactPy. Click ",
            SubComponent("https://pypi.org/project/reactpy/"),
            " to learn more.",
        ),
    )

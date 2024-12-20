from reactpy import html, use_state, component, event, run
from logging import getLogger, INFO

logger = getLogger(__name__)

@component
def ButtonWithChangingColor():

    color_toggle, set_color_toggle = use_state(True)
    color = "red" if color_toggle else "blue"

    @event
    def on_click(evt):
        logger.info("event")
        set_color_toggle(not color_toggle)

    return html.button(
        {
            "id": "my-button",
            "on_click": on_click,
            "style": {"background_color": color, "color": "white"},
        },
        f"color: {color}",
    )


# hatch shell
# cd src/py
# python -m stj.simple_button

if __name__ == "__main__":
    logger.setLevel(INFO)
    logger.info("starting...")
    run(ButtonWithChangingColor)

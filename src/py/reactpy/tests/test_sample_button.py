from reactpy.sample_button import ButtonWithChangingColor
from reactpy.testing import DisplayFixture, poll

# src/py/reactpy/tests/test_client.py

async def _get_style(element):
    items = (await element.get_attribute("style")).split(";")
    pairs = [item.split(":", 1) for item in map(str.strip, items) if item]
    return {key.strip(): value.strip() for key, value in pairs}


async def test_sample_app(display: DisplayFixture):
    await display.show(ButtonWithChangingColor)


    button = await display.page.wait_for_selector("#my-button")

    await poll(_get_style, button).until(
        lambda style: style["background-color"] == "red"
    )

    for color in ["blue", "red"] * 2:
        await button.click()
        await poll(_get_style, button).until(
            lambda style, c=color: style["background-color"] == c
        )

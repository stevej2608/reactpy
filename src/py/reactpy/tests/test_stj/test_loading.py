import asyncio
from typing import Any

import pytest
from playwright.async_api import Browser
from utils.logger import log

from reactpy import component, event, html, use_location, use_state
from reactpy.testing import BackendFixture

from .tooling import page_stable


async def test_stress(server: BackendFixture, browser: Browser):
    _browser_log: dict[str, list[str]] = {}

    def browser_log(id:str, msg:str):
        if id not in _browser_log:
            _browser_log[id] = []
        _browser_log[id].append(msg)

    @component
    def TestApp():
        count, set_count = use_state(100)
        _id = use_location().pathname[1:]

        @event
        def on_click(event: Any):
            browser_log(_id, "on_click")
            log.info("%s on_click()", _id)
            set_count(count+1)

        log.info("%s render()", _id)
        browser_log(_id, "render")
        return html.div(
            html.button({"on_click": on_click}, "UP"),
            html.h2(f"{_id} count={count}")
        )

    # https://github.com/microsoft/playwright-python/issues/886#issuecomment-911469049

    async def worker(browser: Browser, i: int):

        browser_log(f"browser-{i}", "worker started")

        context = await browser.new_context()
        page = await context.new_page()

        url = server.url(f"/browser-{i}")
        await page.goto(url)

        await page_stable(page)
        text = await page.locator("h2").inner_text()
        assert text == f"browser-{i} count=100"

        await page.locator("button").click()

        await page_stable(page)
        text = await page.locator("h2").inner_text()
        assert text == f"browser-{i} count=101"

        await context.close()

    log.info("test_stress")

    server.mount(TestApp)

    await asyncio.wait(
        [asyncio.create_task(worker(browser, i)) for i in range(6)],
        return_when=asyncio.ALL_COMPLETED,
    )

    for blog in _browser_log:
        assert blog == ["worker started", "render", "on_click", "render"]

    assert True

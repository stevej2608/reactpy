from reactpy import component, Layout, Ref, vdom, use_state

from tests.tooling.common import update_message

# src/py/reactpy/tests/test_core/test_layout.py#L81

async def test_simple_layout():
    set_state_hook = Ref()

    @component
    def SimpleComponent():
        tag, set_state_hook.current = use_state("div")
        return vdom(tag)

    async with Layout(SimpleComponent()) as layout:
        update_1 = await layout.render()
        assert update_1 == update_message(
            path="",
            model={"tagName": "", "children": [{"tagName": "div"}]},
        )

        set_state_hook.current("table")

        update_2 = await layout.render()
        assert update_2 == update_message(
            path="",
            model={"tagName": "", "children": [{"tagName": "table"}]},
        )

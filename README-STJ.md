# Building reactpy

To create a hatch shell and run tests, see [contributor-guide]

    hatch shell
    invoke env      !! This takes a while


    hatch run test-py
    hatch run test-js

## Helpers

    hatch env show

## Running examples

    hatch shell
    cd src/py/reactpy

    python -m reactpy.stj.sample_button

## Testing

    hatch run test-py

    pytest src/py/reactpy/tests/test_stj/test_loading.py

## VSCODE debugging

In order launch the examples in the VSCODE debugger the python interpreter
environment created by hatch needs to be resolved

In VSCODE, in the a terminal window:

    hatch shell
    whereis python
    python: .venv/scripts/bin/python

Using the above example, open the command input (Ctrl+Shift+P): Select Python Interpreter, and add:

    .venv/scripts/bin/python

In VSCODE, launch *1a. (stj.simple_button)*. The example should start with a Chrome Browser
window opening automatically.


# Notes on code

## Module load

* The decorator [@component](src/py/reactpy/reactpy/core/component.py#L10) is called, returning a wrapped initialiser function.
        * When the component is referenced, the function returns a *Component* class instance for the component

## Backend

### Server Start up

Calling [reactpy/backend/util.run()] kicks the server off.

The code supports the following backends:

    default.py
    fastapi.py
    flask.py
    hooks.py
    sanic.py
    starlette.py
    tornado.py

A common interface [class BackendType](src/py/reactpy/reactpy/backend/types.py#L14) is defined as follows:

```
class BackendType(Protocol[_App]):
    Options: Callable[..., Any]

    def configure(): ...
    def create_development_app(self): ...
    async def serve_development_app(): ...
```

The code in [reactpy/backend/util.run()] identifies the required backend and then 
calls:

        implementation.create_development_app()
        implementation.configure()

The implementation specific *configure()* function applies any server
**Options** and configures the underlying server with CORS and routes for 
index.html, static assests, etc.

In addition *configure()* also calls [_setup_single_view_dispatcher_route()], this
call adds the additional websocket routes and associated dispatcher that manages
the reactpy layout rendering and event dispatch.

And finally, with an **asyncio.run()** loop, off we go:

        asyncio.run(implementation.serve_development_app(app, host, port))

Concrete implementations of *serve_development_app()* are defined in:

* [flask.py]
* [sanic.py]
* [starlette.py]
* [tornado.py]

Code exists for the creation & configuration of [fastapi.py]. The definition 
of *serve_development_app()* maps directly onto starlette.

At this point, on the console, we see:

    Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

The server is now dormant, waiting for an incoming connection.


### Normal Running

The [sanic.py] and [starlette.py] backends are both [ASGI] complient 
applications. Both call [serve_with_uvicorn()] on start up.

[serve_with_uvicorn()] passes the [ASGI] application 
to [Uvicorn] for execution. All this proceeds within the **asyncio.run()** 
involcation created during startup, see [reactpy/backend/util.run()].

The server setup has been primed with routes for serving static pages and 
assets. Additionally websockets and an associated disparcher are waiting
for incomming layout requests, see [_setup_single_view_dispatcher_route()]

[serve_layout()] connects the current page's [Layout] update & events to
the websocket.

[Layout] is an asyncio context manager. It is used in a *with* context
in [serve_layout()] 

```
"""Run a dispatch loop for a single view instance"""
async with layout:
    try:
        async with create_task_group() as task_group:
            logger.info(f"Start serving {layout}")
            task_group.start_soon(_single_outgoing_loop, layout, send)
            task_group.start_soon(_single_incoming_loop, task_group, layout, recv)
    except Stop:
        logger.info(f"Stopped serving {layout}")
```


### Server Shutdown


## Pytest Tests

The tests are a great way to understand how the the codebase is intended to be 
used. The following tests give significant understanding of how the core 
code hangs together.

### [test_component.py](src/py/reactpy/tests/test_core/test_component.py)

The user facing view of ReactPy is the declaration of custom components
that are a syntheses of child components, html markup, parameters, logic
and events:

```
    @component
    def Counter(start:int):
        count, set_count = use_state(start)

        @event
        def on_click(event: Any):
            set_count(count+1)

        return html.div(
            html.button({"on_click": on_click}, "UP"),
            html.h2(f"{_id} count={count}")
        )
```



* [test_simple_layout](src/py/reactpy/tests/test_core/test_layout.py#L82)
* [test_nested_component_layout](src/py/reactpy/tests/test_core/test_layout.py#L114)
* [test_components_are_garbage_collected](src/py/reactpy/tests/test_core/test_layout.py#L321)




## TODO

- [ ] Undestand layout lifcycle hooks


# Code organisation

    core/ LOC=1656
        component.py - Instatiated on startup
            class Component

            def component

        events.py
            class EventHandler
    
            def event  
            def merge_event_handler_funcs  
            def merge_event_handlers  
            def to_event_handler_function 

        hooks.py

            class _ContextProvider  
            class _CurrentState  
            class _LambdaCaller  
            class _Memo  

            def _create_dispatcher  
            def _try_to_infer_closure_values  
            def _use_const  
            def create_context  
            def strictly_equal  
            def use_callback  
            def use_context  
            def use_debug_value  
            def use_effect  
            def use_memo  
            def use_reducer  
            def use_ref  
            def use_state 

        layout.py
            class _LifeCycleState  
            class _ModelState:
            class _ThreadSafeQueue  
            class Layout:
            class Stop  

            def _copy_component_model_state  
            def _make_component_model_state  
            def _make_element_model_state  
            def _make_life_cycle_state  
            def _new_root_model_state  
            def _process_child_type_and_key  
            def _update_component_model_state  
            def _update_element_model_state  
            def _update_life_cycle_state 

        vdom.py
            class _CustomVdomDictConstructor  
            class _EllipsisRepr

            def _is_attributes  
            def _is_single_child  
            def _validate_child_key_integrity  
            def custom_vdom_constructor  
            def is_vdom  
            def make_vdom_constructor  
            def separate_attributes_and_children  
            def separate_attributes_and_event_handlers  
            def validate_vdom_json  
            def vdom  


    backend/ LOC=961
        default.py
        fastapi.py
        flask.py
        hooks.py
        sanic.py
        starlette.py
        tornado.py
        types.py
        utils.py
            def run

    web/ LOC=368

# Links

* [ReactPy]
    * [Discord Server]


[ReactPy]: https://github.com/reactive-python/reactpy
[Discord Server]: https://github.com/reactive-python/reactpy/discussions?discussions_q=

[reactpy/backend/util.run()]: src/py/reactpy/reactpy/backend/utils.py#L26
[fastapi.py]: src/py/reactpy/reactpy/backend/fastapi.py
[flask.py]: src/py/reactpy/reactpy/backend/flask.py#L93
[sanic.py]: src/py/reactpy/reactpy/backend/sanic.py#L76
[starlette.py]: src/py/reactpy/reactpy/backend/starlette.py#L77
[_setup_single_view_dispatcher_route()]: src/py/reactpy/reactpy/backend/starlette.py#L144
[tornado.py]: src/py/reactpy/reactpy/backend/tornado.py#L70
[serve_with_uvicorn()]: src/py/reactpy/reactpy/backend/_common.py
[ASGI]: https://www.infoworld.com/article/3658336/asgi-explained-the-future-of-python-web-development.html
[Uvicorn]: https://www.uvicorn.org/
[serve_layout()]: src/py/reactpy/reactpy/core/serve.py
[Layout]: src/py/reactpy/reactpy/core/layout.py#L52
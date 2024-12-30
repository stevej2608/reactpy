Understanding ReactPy
=====================

.. toctree::
    :hidden:

    representing-html
    what-are-components
    the-rendering-pipeline
    why-reactpy-needs-keys
    the-rendering-process
    layout-render-servers
    writing-tests

.. note::

    Under construction 🚧

#  Overview

The user facing view of ReactPy is the declaration of custom components
that are a syntheses of child components, html markup, parameters, logic
and events:

```
    @component
    def MyCounter(start:int):
        count, set_count = use_state(start)

        @event
        def on_click(event: Any):
            set_count(count+1)

        return html.div(
            html.button({"on_click": on_click}, "UP"),
            html.h2(f"{_id} count={count}")
        )
```

The decorators *@component* and *@event* together with the *use_state()* hook are 
the main routes into the ReactPy underworld.

## @component

The *@component* decorator, like all python decorators, returns a function 
reference that when called constructs and returns an instance of the ReactPy 
*Component* class. The body of the wrapped component is not considered at
this stage. The returned Component instance holds a reference to the wrapped
function and the signature of the functions parameters.


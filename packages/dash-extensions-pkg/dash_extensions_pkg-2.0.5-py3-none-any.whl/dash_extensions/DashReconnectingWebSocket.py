# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DashReconnectingWebSocket(Component):
    """A DashReconnectingWebSocket component.
A Dash component wrapping ReconnectingWebSocket for auto-reconnect websocket support.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- error (boolean | number | string | dict | list; optional):
    This property is set with the content of the onerror event.

- message (boolean | number | string | dict | list; optional):
    When messages are received, this property is updated with the
    message content.

- protocols (list of strings; optional):
    Supported websocket protocols (optional).

- reconnectOptions (dict; optional):
    Reconnect options (optional).

    `reconnectOptions` is a dict with keys:

    - debug (boolean; optional)

    - automaticOpen (boolean; optional)

    - reconnectInterval (number; optional)

    - maxReconnectInterval (number; optional)

    - reconnectDecay (number; optional)

    - timeoutInterval (number; optional)

    - maxReconnectAttempts (number; optional)

    - binaryType (a value equal to: 'blob', 'arraybuffer'; optional)

- send (boolean | number | string | dict | list; optional):
    When this property is set, a message is sent with its content.

- state (boolean | number | string | dict | list; optional):
    This websocket state (in the readyState prop) and associated
    information.

- url (string; optional):
    The websocket endpoint (e.g. wss://echo.websocket.org)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'DashReconnectingWebSocket'
    ReconnectOptions = TypedDict(
        "ReconnectOptions",
            {
            "debug": NotRequired[bool],
            "automaticOpen": NotRequired[bool],
            "reconnectInterval": NotRequired[NumberType],
            "maxReconnectInterval": NotRequired[NumberType],
            "reconnectDecay": NotRequired[NumberType],
            "timeoutInterval": NotRequired[NumberType],
            "maxReconnectAttempts": NotRequired[NumberType],
            "binaryType": NotRequired[Literal["blob", "arraybuffer"]]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        state: typing.Optional[typing.Any] = None,
        message: typing.Optional[typing.Any] = None,
        error: typing.Optional[typing.Any] = None,
        send: typing.Optional[typing.Any] = None,
        url: typing.Optional[str] = None,
        protocols: typing.Optional[typing.Sequence[str]] = None,
        reconnectOptions: typing.Optional["ReconnectOptions"] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'error', 'message', 'protocols', 'reconnectOptions', 'send', 'state', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'error', 'message', 'protocols', 'reconnectOptions', 'send', 'state', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashReconnectingWebSocket, self).__init__(**args)

setattr(DashReconnectingWebSocket, "__init__", _explicitize_args(DashReconnectingWebSocket.__init__))

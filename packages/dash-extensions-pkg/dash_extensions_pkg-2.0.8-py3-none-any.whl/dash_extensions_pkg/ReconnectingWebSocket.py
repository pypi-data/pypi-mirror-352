# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class ReconnectingWebSocket(Component):
    """A ReconnectingWebSocket component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- connecting (boolean | number | string | dict | list; optional):
    This property is set with the content of connecting events.

- error (boolean | number | string | dict | list; optional):
    This property is set with the content of the onerror event.

- message (boolean | number | string | dict | list; optional):
    When messages are received, this property is updated with the
    message content.

- protocols (list of strings; optional):
    Supported websocket protocols (optional).

- reconnectOptions (dict; optional):
    Reconnection options to configure auto-reconnect behavior.

    `reconnectOptions` is a dict with keys:

    - debug (boolean; optional):
        Whether this instance should log debug messages.

    - automaticOpen (boolean; optional):
        Whether or not the websocket should attempt to connect
        immediately upon instantiation.

    - reconnectInterval (number; optional):
        The number of milliseconds to delay before attempting to
        reconnect.

    - maxReconnectInterval (number; optional):
        The maximum number of milliseconds to delay a reconnection
        attempt.

    - reconnectDecay (number; optional):
        The rate of increase of the reconnect delay. Allows reconnect
        attempts to back off when problems persist.

    - timeoutInterval (number; optional):
        The maximum time in milliseconds to wait for a connection to
        succeed before closing and retrying.

    - maxReconnectAttempts (number; optional):
        The maximum number of reconnection attempts to make. Unlimited
        if None.

    - binaryType (a value equal to: 'blob', 'arraybuffer'; optional):
        The binary type, possible values 'blob' or 'arraybuffer'.

- send (boolean | number | string | dict | list; optional):
    When this property is set, a message is sent with its content.

- state (boolean | number | string | dict | list; optional):
    This websocket state (in the readyState prop) and associated
    information.

- timeout (number; optional):
    How many ms to wait for websocket to be ready when sending a
    message (optional).

- url (string; optional):
    The websocket endpoint (e.g. wss://echo.websocket.org)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions_pkg'
    _type = 'ReconnectingWebSocket'
    ReconnectOptions = TypedDict(
        "ReconnectOptions",
            {
            "debug": NotRequired[bool],
            "automaticOpen": NotRequired[bool],
            "reconnectInterval": NotRequired[typing.Union[int, float, numbers.Number]],
            "maxReconnectInterval": NotRequired[typing.Union[int, float, numbers.Number]],
            "reconnectDecay": NotRequired[typing.Union[int, float, numbers.Number]],
            "timeoutInterval": NotRequired[typing.Union[int, float, numbers.Number]],
            "maxReconnectAttempts": NotRequired[typing.Union[int, float, numbers.Number]],
            "binaryType": NotRequired[Literal["blob", "arraybuffer"]]
        }
    )

    @_explicitize_args
    def __init__(
        self,
        children: typing.Optional[typing.Union[str, int, float, ComponentType, typing.Sequence[typing.Union[str, int, float, ComponentType]]]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        state: typing.Optional[typing.Any] = None,
        message: typing.Optional[typing.Any] = None,
        error: typing.Optional[typing.Any] = None,
        connecting: typing.Optional[typing.Any] = None,
        send: typing.Optional[typing.Any] = None,
        url: typing.Optional[str] = None,
        protocols: typing.Optional[typing.Sequence[str]] = None,
        timeout: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        reconnectOptions: typing.Optional["ReconnectOptions"] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'connecting', 'error', 'message', 'protocols', 'reconnectOptions', 'send', 'state', 'timeout', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'connecting', 'error', 'message', 'protocols', 'reconnectOptions', 'send', 'state', 'timeout', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(ReconnectingWebSocket, self).__init__(children=children, **args)

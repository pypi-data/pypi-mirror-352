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


class ReconnectingWebSocket(Component):
    """A ReconnectingWebSocket component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- options (dict; optional)

    `options` is a dict with keys:

    - debug (boolean; optional)

    - automaticOpen (boolean; optional)

    - reconnectInterval (number; optional)

    - maxReconnectInterval (number; optional)

    - reconnectDecay (number; optional)

    - timeoutInterval (number; optional)

    - maxReconnectAttempts (number; optional)

    - binaryType (a value equal to: 'blob', 'arraybuffer'; optional)

- protocols (string | list of strings; optional)

- url (string; required)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'ReconnectingWebSocket'
    Options = TypedDict(
        "Options",
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
        children: typing.Optional[ComponentType] = None,
        url: typing.Optional[str] = None,
        protocols: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        options: typing.Optional["Options"] = None,
        onOpen: typing.Optional[typing.Any] = None,
        onClose: typing.Optional[typing.Any] = None,
        onConnecting: typing.Optional[typing.Any] = None,
        onMessage: typing.Optional[typing.Any] = None,
        onError: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'options', 'protocols', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'options', 'protocols', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['url']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(ReconnectingWebSocket, self).__init__(children=children, **args)

setattr(ReconnectingWebSocket, "__init__", _explicitize_args(ReconnectingWebSocket.__init__))

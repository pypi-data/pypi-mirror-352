import dash
from dash.development.base_component import Component, _explicitize_args

class DashReconnectingWebSocket(Component):
    def __init__(self, url=None, protocols=None, reconnectOptions=None, id=None, **kwargs):
        self._prop_names = ["url", "protocols", "reconnectOptions", "id"]
        self._type = "DashReconnectingWebSocket"
        self._namespace = "dash_extensions"
        self._valid_wildcard_attributes = []
        super().__init__(url=url, protocols=protocols, reconnectOptions=reconnectOptions, id=id, **kwargs)

__all__ = ["DashReconnectingWebSocket"]

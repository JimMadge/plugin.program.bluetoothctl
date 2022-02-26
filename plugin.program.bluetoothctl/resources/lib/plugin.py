import sys
from typing import Any, Callable, Optional
import urllib.parse
import xbmcaddon  # type: ignore
from .logging import logdebug


class PluginException(Exception):
    pass


class Plugin:
    def __init__(self) -> None:
        self._base_url = sys.argv[0]
        self._handle = int(sys.argv[1])
        self._params = urllib.parse.parse_qs(sys.argv[2][1:])
        self._addon = xbmcaddon.Addon()
        self._actions: dict[str, Callable[[dict[str, str]], None]] = {}

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def params(self) -> dict[str, str]:
        return {key: value[0] for key, value in self._params.items()}

    @property
    def name(self) -> str:
        return str(self._addon.getAddonInfo('name'))

    def action(self, func: Callable[[Any], None]) -> Callable[[Any], None]:
        if not callable(func):
            raise PluginException(f'{func} is not callable')

        name = func.__name__
        if name in self._actions.keys():
            raise PluginException(f'action {name} already registered')

        logdebug(f'registering action: {name}')
        self._actions[name] = func

        return func

    def build_url(self, action: Optional[str] = None, **kwargs: Any) -> str:
        if action:
            params = urllib.parse.urlencode({'action': action} | kwargs)
        else:
            params = urllib.parse.urlencode(kwargs)
        url = ''.join([self._base_url, '?', params])
        return url

    def run(self) -> None:
        logdebug(f'entering with parameters {self.params}')
        logdebug(f'actions registered: {self._actions.keys()}')
        action = self.params.get('action', 'root')

        self._actions[action](self.params)

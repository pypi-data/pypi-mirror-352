import json
from enum import Enum

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse



class Layout(Enum):
    MODERN = "modern"
    CLASSIC = "classic"


class SearchHotKey(Enum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    J = "j"
    K = "k"
    L = "l"
    M = "m"
    N = "n"
    O = "o"
    P = "p"
    Q = "q"
    R = "r"
    S = "s"
    T = "t"
    U = "u"
    V = "v"
    W = "w"
    X = "x"
    Y = "y"
    Z = "z"


scalar_theme = """
/* basic theme */
.light-mode {
  --scalar-color-1: #2a2f45;
  --scalar-color-2: #757575;
  --scalar-color-3: #8e8e8e;
  --scalar-color-accent: #009485;

  --scalar-background-1: #fff;
  --scalar-background-2: #fcfcfc;
  --scalar-background-3: #f8f8f8;
  --scalar-background-accent: #ecf8f6;

  --scalar-border-color: rgba(0, 0, 0, 0.1);
}
.dark-mode {
  --scalar-color-1: rgba(255, 255, 255, 0.9);
  --scalar-color-2: rgba(255, 255, 255, 0.62);
  --scalar-color-3: rgba(255, 255, 255, 0.44);
  --scalar-color-accent: #00ccb8;

  --scalar-background-1: #1f2129;
  --scalar-background-2: #282a35;
  --scalar-background-3: #30323d;
  --scalar-background-accent: #223136;

  --scalar-border-color: rgba(255, 255, 255, 0.1);
}
/* Document Sidebar */
.light-mode .t-doc__sidebar {
  --sidebar-background-1: var(--scalar-background-1);
  --sidebar-item-hover-color: currentColor;
  --sidebar-item-hover-background: var(--scalar-background-2);
  --sidebar-item-active-background: var(--scalar-background-accent);
  --sidebar-border-color: var(--scalar-border-color);
  --sidebar-color-1: var(--scalar-color-1);
  --sidebar-color-2: var(--scalar-color-2);
  --sidebar-color-active: var(--scalar-color-accent);
  --sidebar-search-background: transparent;
  --sidebar-search-border-color: var(--scalar-border-color);
  --sidebar-search--color: var(--scalar-color-3);
}

.dark-mode .sidebar {
  --sidebar-background-1: var(--scalar-background-1);
  --sidebar-item-hover-color: currentColor;
  --sidebar-item-hover-background: var(--scalar-background-2);
  --sidebar-item-active-background: var(--scalar-background-accent);
  --sidebar-border-color: var(--scalar-border-color);
  --sidebar-color-1: var(--scalar-color-1);
  --sidebar-color-2: var(--scalar-color-2);
  --sidebar-color-active: var(--scalar-color-accent);
  --sidebar-search-background: transparent;
  --sidebar-search-border-color: var(--scalar-border-color);
  --sidebar-search--color: var(--scalar-color-3);
}

/* advanced */
.light-mode {
  --scalar-button-1: rgb(49 53 56);
  --scalar-button-1-color: #fff;
  --scalar-button-1-hover: rgb(28 31 33);

  --scalar-color-green: #009485;
  --scalar-color-red: #d52b2a;
  --scalar-color-yellow: #ffaa01;
  --scalar-color-blue: #0a52af;
  --scalar-color-orange: #953800;
  --scalar-color-purple: #8251df;

  --scalar-scrollbar-color: rgba(0, 0, 0, 0.18);
  --scalar-scrollbar-color-active: rgba(0, 0, 0, 0.36);
}
.dark-mode {
  --scalar-button-1: #f6f6f6;
  --scalar-button-1-color: #000;
  --scalar-button-1-hover: #e7e7e7;

  --scalar-color-green: #00ccb8;
  --scalar-color-red: #e5695b;
  --scalar-color-yellow: #ffaa01;
  --scalar-color-blue: #78bffd;
  --scalar-color-orange: #ffa656;
  --scalar-color-purple: #d2a8ff;

  --scalar-scrollbar-color: rgba(255, 255, 255, 0.24);
  --scalar-scrollbar-color-active: rgba(255, 255, 255, 0.48);
}
:root {
  --scalar-radius: 3px;
  --scalar-radius-lg: 6px;
  --scalar-radius-xl: 8px;
}
.scalar-card:nth-of-type(3) {
  display: none;
}"""



def get_scalar_ui_html(
        *,
        openapi_url: str,
        title: str,
        scalar_js_url: str = "https://cdn.jsdelivr.net/npm/@scalar/api-reference",
        scalar_proxy_url: str = "",
        scalar_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
        scalar_theme: str = scalar_theme,
        layout: Layout = Layout.MODERN,
        show_sidebar: bool = True,
        hide_download_button: bool = False,
        hide_models: bool = False,
        dark_mode: bool = True,
        search_hot_key: SearchHotKey = SearchHotKey.K,
        hidden_clients: bool | dict[str, bool | list[str]] | list[str] = [],
        servers: list[dict[str, str]] = [],
        default_open_all_tags: bool = False,
        init_oauth: dict[str, str] = None,
) -> HTMLResponse:
    authentication = ""
    if init_oauth:
        authentication = f"""
        authentication: {json.dumps({
            "oAuth2": {
                "clientId": init_oauth.get("clientId"),
                "clientSecret": init_oauth.get("clientSecret"),
                "scopes": init_oauth.get("scopes").split(" "),
            }
        })}"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="{scalar_favicon_url}">
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    <style>
    {scalar_theme}
    </style>
    </head>
    <body>
    <noscript>
        Scalar requires Javascript to function. Please enable it to browse the documentation.
    </noscript>
    <script
      id="api-reference"
      data-url="{openapi_url}"
      data-proxy-url="{scalar_proxy_url}"></script>
    <script>
      var configuration = {{
        layout: "{layout.value}",
        showSidebar: {json.dumps(show_sidebar)},
        hideDownloadButton: {json.dumps(hide_download_button)},
        hideModels: {json.dumps(hide_models)},
        darkMode: {json.dumps(dark_mode)},
        searchHotKey: "{search_hot_key.value}",
        hiddenClients: {json.dumps(hidden_clients)},
        servers: {json.dumps(servers)},
        defaultOpenAllTags: {json.dumps(default_open_all_tags)},
        {authentication}
      }}

      document.getElementById('api-reference').dataset.configuration =
        JSON.stringify(configuration)
    </script>
    <script src="{scalar_js_url}"></script>
    </body>
    </html>
    """
    return HTMLResponse(html)


def scalar(
        app: FastAPI,
        **kwargs
):
    _openapi_url = kwargs.pop("openapi_url", app.openapi_url)
    _title = kwargs.pop("title", app.title)
    _servers = kwargs.pop("servers", app.servers)
    _init_oauth = kwargs.pop("init_oauth", app.swagger_ui_init_oauth)
    _scalar_js_url = kwargs.pop("scalar_js_url", "https://cdn.jsdelivr.net/npm/@scalar/api-reference")

    @app.get("/scalar", include_in_schema=False)
    async def scalar_html(request: Request):
        root_path = request.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + _openapi_url
        scalar_js_url = root_path + _scalar_js_url
        return get_scalar_ui_html(
            openapi_url=openapi_url,
            title=f"{_title} - Swagger UI",
            servers=_servers,
            init_oauth=_init_oauth,
            scalar_js_url=scalar_js_url,
            **kwargs
        )

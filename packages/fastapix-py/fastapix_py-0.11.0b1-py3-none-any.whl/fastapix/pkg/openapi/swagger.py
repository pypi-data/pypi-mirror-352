from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
)
from starlette.requests import Request


def swagger(
        app: FastAPI,
        **kwargs
):
    _openapi_url = kwargs.pop("openapi_url", app.openapi_url)
    title = kwargs.pop("title", app.title)
    init_oauth = kwargs.pop("init_oauth", app.swagger_ui_init_oauth)
    _swagger_js_url = kwargs.pop("swagger_js_url", "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js")
    _swagger_css_url = kwargs.pop("swagger_css_url", "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css")

    _oauth2_redirect_url = "/swagger/oauth2-redirect.html"

    @app.get(_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_oauth2_redirect_html():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/swagger", include_in_schema=False)
    async def swagger_html(request: Request):
        root_path = request.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + _openapi_url
        swagger_js_url = root_path + _swagger_js_url
        swagger_css_url = root_path + _swagger_css_url

        oauth2_redirect_url = root_path + _oauth2_redirect_url
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=title,
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=init_oauth,
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
            **kwargs
        )



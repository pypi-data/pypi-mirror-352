from pathlib import Path as LibPath

from fastapi import FastAPI, APIRouter, Path
from pydantic import BaseModel
from starlette.responses import FileResponse


class OfflineJsPath(BaseModel):
    scalar_ui_js: str
    swagger_ui_js: str
    swagger_ui_css: str


def get_offline_js_path(app: FastAPI):
    static_url = '/openapi'
    static_path = LibPath(__file__).parent
    router = APIRouter(prefix=static_url)

    @router.get('/scalar-ui{suffix}', include_in_schema=False)
    async def get_scalar_ui(suffix: str = Path(...)):
        return FileResponse(static_path / f'scalar-ui{suffix}')

    @router.get('/swagger-ui{suffix}', include_in_schema=False)
    async def get_swagger_ui(suffix: str = Path(...)):
        return FileResponse(static_path / f'swagger-ui{suffix}')

    app.include_router(router)

    return OfflineJsPath(
        scalar_ui_js=f'{static_url}/scalar-ui.js',
        swagger_ui_js=f'{static_url}/swagger-ui-bundle.js',
        swagger_ui_css=f'{static_url}/swagger-ui.css'
    )

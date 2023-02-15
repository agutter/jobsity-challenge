from fastapi import FastAPI, Header, HTTPException, Request, Response
import http

"""
    This file defines the API webhooks for the application.
"""

#Creates the API Router
router = APIRouter()

@router.post('/', status_code=http.HTTPStatus.ACCEPTED)
async def webhook_post(request: Request):
    payload = await request.body()
    return {}

@router.get('/', status_code=http.HTTPStatus.ACCEPTED)
async def webhook_get_all(request: Request):
    payload = await request.body()
    return {}

@router.get('/{id}', status_code=http.HTTPStatus.ACCEPTED)
async def webhook_get_by_id(id: int, request: Request):
    payload = await request.body()
    return {}

@router.put('/{id}', status_code=http.HTTPStatus.ACCEPTED)
async def webhook_put_by_id(id: int, request: Request):
    payload = await request.body()
    return {}

@router.delete('/{id}', status_code=http.HTTPStatus.ACCEPTED)
async def webhook(id: int, request: Request):
    payload = await request.body()
    return {}


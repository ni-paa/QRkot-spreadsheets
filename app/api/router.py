# app/api/router.py
from fastapi import APIRouter

from app.api.endpoints import charity_project, donation, google

api_router = APIRouter()
api_router.include_router(
    charity_project.router,
    prefix='/charity_project',
    tags=['charity_projects'],
)
api_router.include_router(
    donation.router,
    prefix='/donation',
    tags=['donations'],
)
api_router.include_router(
    google.router,
    prefix='/google',
    tags=['Google'],
)

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

app = FastAPI(
    title=settings.project_name,
    description='Благотворительный фонд поддержки котиков QRKot',
)

app.include_router(api_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route
    for route in users_router.routes
    if route.name != 'users:delete_user'
]
app.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)


@app.get('/')
async def root():
    return {'message': 'QRKot API is running'}

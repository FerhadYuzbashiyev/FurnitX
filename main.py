from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from auth import validate_authorization_header
from routers import router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    endpoints = ["/login", "/register"]  # Эндпоинты, не требующие аутентификации
    if request.url.path not in endpoints:
        # Извлекаем токен из куков
        access_token = request.cookies.get("access_token")
        token = request.cookies.get("Authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        # Удаляем префикс "Bearer " перед проверкой
        token = token.replace("Bearer ", "")
        
        # Валидация токена
        try:
            payload = validate_authorization_header(token)
            print(f"Token payload: {payload}")
        except Exception as e:
            print(f"Token validation failed: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # else:
    #     response = RedirectResponse(url="/main")
    # Продолжение выполнения запроса
    response = await call_next(request)
    return response
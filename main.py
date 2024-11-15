from math import ceil
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, insert, select, delete
from auth import create_access_token, get_current_user, get_password_hash, verify_password
from database import get_async_session, AsyncSession
from models import Furniture, CountryEnum, MaterialEnum, CategoryEnum, User
from schemas import CreateUser, GetAllTables, GetAllTablesResponse, InsertFurniture, InsertFurnitureResponse, UserAuth, UserData, UserDataResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/insert_item")
async def insert_item(fullname: str, 
                        description: str, 
                         price: float,
                         category: CategoryEnum,
                          material: MaterialEnum,
                           manufacturer: CountryEnum,
                            image_url: str,
                             session: AsyncSession = Depends(get_async_session)):
    stmt_check = select(Furniture.c.fullname).where(Furniture.c.fullname == fullname)
    result_check = await session.execute(stmt_check)
    row_check = result_check.fetchone()
    if row_check is not None:
        raise HTTPException(status_code=200, detail="Table already exists")
    
    stmt = insert(Furniture).values(
        fullname = fullname,
        description = description,
        price = price,
        category = category,
        material = material,
        manufacturer = manufacturer,
        image_url = image_url
    )
    await session.execute(stmt)
    await session.commit()
    stmt_response = select(Furniture).where(Furniture.c.fullname == fullname)
    result_response = await session.execute(stmt_response)
    row = result_response.fetchone()
    print(row)
    data = InsertFurniture(
        fullname=row.fullname,
        description=row.description,
        price=row.price,
        category=row.category,
        material=row.material,
        manufacturer=row.manufacturer,
        image_url=row.image_url
    )
    return InsertFurnitureResponse(data=data)


@app.get("/tables", response_class=HTMLResponse)
async def get_tables(request: Request, session: AsyncSession = Depends(get_async_session), page: int = 1):
    items_per_page = 3
    offset = (page - 1) * items_per_page 

    total_items = await session.scalar(select(func.count()).select_from(Furniture).where(Furniture.c.category == CategoryEnum.TABLE))
    total_pages = ceil(total_items / items_per_page)

    stmt_get_all = (
        select(Furniture.c.id, Furniture.c.fullname, Furniture.c.description, Furniture.c.price, Furniture.c.image_url)
        .where(Furniture.c.category == CategoryEnum.TABLE)
        .offset(offset)
        .limit(items_per_page)
    )
    result_get_all = await session.execute(stmt_get_all)
    rows = result_get_all.fetchall()
    
    tables = [
        {
            "id": row.id,
            "title": row.fullname,
            "description": row.description,
            "price": row.price,
            "image_url": row.image_url
        }
        for row in rows
    ]
    
    return templates.TemplateResponse("tables.html", {
        "request": request,
        "tables": tables,
        "current_page": page,
        "total_pages": total_pages
    })

@app.get("/tables/{table_id}", response_class=HTMLResponse)
async def get_table_detail(table_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Furniture).where(Furniture.c.id == table_id)
    result = await session.execute(stmt)
    table = result.fetchone()
    
    if table is None:
        return HTMLResponse(content="Table not found", status_code=404)

    table_data = {
        "title": table.fullname,
        "description": table.description,
        "price": table.price,
        "image_url": table.image_url
    }
    
    return templates.TemplateResponse("table_detail.html", {"request": request, "table": table_data})


@app.get("/chairs", response_class=HTMLResponse)
async def get_chairs(request: Request, session: AsyncSession = Depends(get_async_session), page: int = 1):
    items_per_page = 3
    offset = (page - 1) * items_per_page 

    total_items = await session.scalar(select(func.count()).select_from(Furniture).where(Furniture.c.category == CategoryEnum.CHAIR))
    total_pages = ceil(total_items / items_per_page)

    stmt_get_all = (
        select(Furniture.c.id, Furniture.c.fullname, Furniture.c.description, Furniture.c.price, Furniture.c.image_url)
        .where(Furniture.c.category == CategoryEnum.CHAIR)
        .offset(offset)
        .limit(items_per_page)
    )
    result_get_all = await session.execute(stmt_get_all)
    rows = result_get_all.fetchall()
    
    chairs = [
        {
            "id": row.id,
            "title": row.fullname,
            "description": row.description,
            "price": row.price,
            "image_url": row.image_url
        }
        for row in rows
    ]

    return templates.TemplateResponse("chairs.html", {
        "request": request,
        "chairs": chairs,
        "current_page": page,
        "total_pages": total_pages
    })

@app.get("/chairs/{chair_id}", response_class=HTMLResponse)
async def get_chair_detail(chair_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Furniture).where(Furniture.c.id == chair_id)
    result = await session.execute(stmt)
    chair = result.fetchone()
    
    if chair is None:
        return HTMLResponse(content="Chair not found", status_code=404)

    chair_data = {
        "title": chair.fullname,
        "description": chair.description,
        "price": chair.price,
        "image_url": chair.image_url
    }
    
    return templates.TemplateResponse("chair_detail.html", {"request": request, "chair": chair_data})

@app.get("/beds", response_class=HTMLResponse)
async def get_bed(request: Request, session: AsyncSession = Depends(get_async_session), page: int = 1):
    items_per_page = 3
    offset = (page - 1) * items_per_page 

    total_items = await session.scalar(select(func.count()).select_from(Furniture).where(Furniture.c.category == CategoryEnum.BED))
    total_pages = ceil(total_items / items_per_page)

    stmt_get_all = (
        select(Furniture.c.id, Furniture.c.fullname, Furniture.c.description, Furniture.c.price, Furniture.c.image_url)
        .where(Furniture.c.category == CategoryEnum.BED)
        .offset(offset)
        .limit(items_per_page)
    )
    result_get_all = await session.execute(stmt_get_all)
    rows = result_get_all.fetchall()
    
    beds = [
        {
            "id": row.id,
            "title": row.fullname,
            "description": row.description,
            "price": row.price,
            "image_url": row.image_url
        }
        for row in rows
    ]

    return templates.TemplateResponse("beds.html", {
        "request": request,
        "beds": beds,
        "current_page": page,
        "total_pages": total_pages
    })


@app.get("/beds/{bed_id}", response_class=HTMLResponse)
async def get_chair_detail(bed_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Furniture).where(Furniture.c.id == bed_id)
    result = await session.execute(stmt)
    bed = result.fetchone()
    
    if bed is None:
        return HTMLResponse(content="Bed not found", status_code=404)

    bed_data = {
        "title": bed.fullname,
        "description": bed.description,
        "price": bed.price,
        "image_url": bed.image_url
    }
    
    return templates.TemplateResponse("bed_detail.html", {"request": request, "bed": bed_data})

@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request, current_user: Annotated[dict, Depends(get_current_user)]):
    # Выводим данные пользователя, чтобы убедиться, что аутентификация прошла успешно
    print(f"Current user: {current_user}")
    
    # Передаем данные пользователя в шаблон, если нужно
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user  # или передайте отдельные данные, например, current_user['fullname']
    })

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.delete("/delete")
async def delete_item(id: int, session: AsyncSession = Depends(get_async_session)):
    stmt_delete = delete(Furniture).where(Furniture.c.id == id)
    await session.execute(stmt_delete)
    await session.commit()

@app.get("/register", response_class=HTMLResponse)
async def show_registration_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def create_user(request: Request, user_fields: CreateUser = Form(...), session: AsyncSession = Depends(get_async_session)):
    hash_password = get_password_hash(user_fields.password)
    check = select(User).where(User.c.email == user_fields.email)
    result = await session.execute(check)
    row = result.fetchone()
    # print(some)
    if row is not None:
        raise HTTPException(status_code=400, detail="User already exists")
    stmt = insert(User).values(
        fullname = user_fields.fullname,
        email = user_fields.email,
        hashed_password = hash_password,
    )
    await session.execute(stmt)
    await session.commit()
    stmt_uuid = select(User.c.user_uuid).where(user_fields.email == User.c.email)
    result_uuid = await session.execute(stmt_uuid)
    uuid = result_uuid.fetchone()[0]
    get_response = UserData(
        user_uuid=uuid,
        email=user_fields.email
    )
    response = UserDataResponse(data=get_response)
    stmt_test = select(User.c.fullname, User.c.email,
    ).where(user_fields.email == User.c.email)
    result_test = await session.execute(stmt_test)
    row_test = result_test.fetchone()
    test = {
        "fullname": row_test.fullname,
        "email": row_test.email,
    }
    stmt_id = select(User.c.id).where(User.c.email == user_fields.email)
    result_stmt_id = await session.execute(stmt_id)
    row_id = result_stmt_id.fetchone()[0]
    access_token = create_access_token(data={"sub": row_id, "email": user_fields.email})
    response = templates.TemplateResponse("register.html", {"request": request, "response": response, "test": test})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response
    
@app.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_async_session)):
    stmt = select(User.c.id, User.c.email, User.c.hashed_password).where(User.c.email == form_data.username)
    result = await session.execute(stmt)
    user = result.fetchone()
    
    if user is None or not verify_password(form_data.password, user[2]):  # user[2] - hashed_password
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user[0], "email": user[1]})  # user[0] - id
    print(access_token)
    return templates.TemplateResponse("login.html", {"request": request, "access_token": access_token, "token_type": "bearer"})

@app.get("/protected-route")
async def protected_route(current_user: Annotated[UserAuth, Depends(get_current_user)]):
    print(current_user)
    return {"message": f"Hello, {current_user[0]}!"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path not in ["/login", "/register", "/open-route"]:
        token = request.headers.get("Authorization")
        print(token)
        print("TEST")
        if not token or not await get_current_user(token):  # Проверка авторизации
            raise HTTPException(status_code=401, detail="Not authenticated")
    response = await call_next(request)
    return response
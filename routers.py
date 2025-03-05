from math import ceil
from datetime import datetime, timedelta
import random
from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, insert, select, delete
from auth import create_access_token, get_current_user, get_password_hash, validate_authorization_header, verify_password
from database import get_async_session, AsyncSession
from models import Furniture, CountryEnum, MaterialEnum, CategoryEnum, OTPPurposeEnum, StatusEnum, User, OTP
from schemas import CreateUser, GetAllTables, GetAllTablesResponse, InsertFurniture, InsertFurnitureResponse, LoginRequest, OTPCheckFields, TokenResponse, UserAuth, UserData, UserDataResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# router.mount("/static", StaticFiles(directory="static"), name="static")
http_bearer = HTTPBearer()

@router.post("/insert_item")
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

@router.get("/tables", response_class=HTMLResponse)
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

@router.get("/tables/{table_id}", response_class=HTMLResponse)
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

@router.get("/chairs", response_class=HTMLResponse)
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

@router.get("/chairs/{chair_id}", response_class=HTMLResponse)
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

@router.get("/beds", response_class=HTMLResponse)
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

@router.get("/beds/{bed_id}", response_class=HTMLResponse)
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

@router.get("/main", response_class=HTMLResponse)
async def main_page(request: Request, Authorization: str = Cookie(None)):
    print("/main TEST")
    print("Authorization:", Authorization)
    print("END /main TEST")
    return templates.TemplateResponse("index.html", {
        "request": request,
        # "user": current_user
    })

@router.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@router.delete("/delete")
async def delete_item(id: int, session: AsyncSession = Depends(get_async_session)):
    stmt_delete = delete(Furniture).where(Furniture.c.id == id)
    await session.execute(stmt_delete)
    await session.commit()

@router.get("/register", response_class=HTMLResponse)
async def show_registration_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
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
        status = StatusEnum.CONTACT_VERIFICATION
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

    response = RedirectResponse(url="/main", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    response.headers["Authorization"] = f"Bearer {access_token}"
    await otp_create(email=user_fields.email, session=session)
    return response

@router.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, login_form: LoginRequest = Form(...), session: AsyncSession = Depends(get_async_session)):
    stmt = select(User.c.id, User.c.email, User.c.hashed_password).where(User.c.email == login_form.username)
    result = await session.execute(stmt)
    user = result.fetchone()
    if user is None or not verify_password(login_form.password, user[2]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user[0], "email": user[1]})
    print(user[0])
    response = RedirectResponse(url="/main", status_code=303)
    response.set_cookie(key="Authorization", value=f"Bearer {access_token}", httponly=True) # Setting JWT to Cookie file
    response.headers["Authorization"] = f"Bearer {access_token}" # Setting JWT to header
    print("Authorization: ", response.headers["Authorization"])
    return response

@router.post("/otp-create")
async def otp_create(email: str, session: AsyncSession = Depends(get_async_session)):
    print("OTP CREATE TEST")
    stmt_user = select(User.c.id, User.c.email).where(email == User.c.email) # id and email
    result_user = await session.execute(stmt_user)
    row_user = result_user.fetchone()
    # print(row)
    if row_user[1] is None: # email
        raise HTTPException(status_code=400, detail="No such user")
    stmt_insert = insert(OTP).values(
        purpose = OTPPurposeEnum.USER_REGISTER,
        otp_code = random.randint(1000,9999),
        user_id = row_user[0] # user id
    )
    await session.execute(stmt_insert)
    await session.commit()
    # stmt_exp = select(OTP.c.expiration_time).where(OTP.c.email == email)
    # result_exp = await session.execute(stmt_exp)
    # row_exp = result_exp.fetchone()[0]

    return {"status": 200, "details": f"OTP: {OTP.c.otp_code}"}

@router.get("/otp", response_class=HTMLResponse)
async def otp_get(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})

@router.post("/otp-check", response_class=HTMLResponse)
async def otp_check(fields: OTPCheckFields, request: Request, session: AsyncSession = Depends(get_async_session)):
    stmt_user = select(User.c.user_uuid, User.c.id, User.c.email, OTP.c.purpose).join(OTP, OTP.c.user_id == User.c.id).where(User.c.user_uuid == fields.user_uuid, User.c.email == fields.email, OTP.c.purpose == fields.purpose)
    result_user = await session.execute(stmt_user)
    row_user = result_user.fetchone()
    if row_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such user")
    stmt_otp = select(OTP.c.expiration_time).where(row_user[1] == OTP.c.user_id).order_by(OTP.c.id.desc())
    result_otp = await session.execute(stmt_otp)
    row_otp = result_otp.fetchone()[0]
    if row_otp < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP code time is expired")
    if row_otp != fields.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong OTP code")
    return templates.TemplateResponse("otp.html", {"request": request})
    

# @app.get("/protected-route")
# async def protected_route(current_user: Annotated[UserAuth, Depends(get_current_user)]):
#     print(current_user)
#     print("TEST_pr_route")
#     return {"message": f"Hello, {current_user[0]}!"}


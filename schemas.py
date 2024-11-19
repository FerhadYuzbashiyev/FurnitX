from typing import List, Optional
from uuid import UUID
from fastapi import Form
from pydantic import BaseModel, Field
from enum import Enum

from models import CountryEnum, CategoryEnum, MaterialEnum

class GetAllTables(BaseModel):
    fullname: str
    description: str
    price: float
    # category: CategoryEnum = CategoryEnum.TABLE
    # material: MaterialEnum
    # manufacturer: CountryEnum
    image_url: str

class GetAllTablesResponse(BaseModel):
    data: List[GetAllTables]

class InsertFurniture(BaseModel):
    fullname: str
    description: str
    price: float
    category: CategoryEnum
    material: MaterialEnum
    manufacturer: CountryEnum
    image_url: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class InsertFurnitureResponse(BaseModel):
    data: InsertFurniture

class UserAuth(BaseModel):
    email: str

class CreateUser(BaseModel):
    fullname: str
    email: str
    password: str

class UserData(BaseModel):
    user_uuid: UUID
    email: str

class UserDataResponse(BaseModel):
    data: UserData
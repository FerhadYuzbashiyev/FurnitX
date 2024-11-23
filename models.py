from datetime import datetime, timedelta
from unicodedata import category
import uuid

from sqlalchemy import UUID, Float, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, Enum
from enum import Enum as PyEnum

class CategoryEnum(str, PyEnum):
    TABLE = "table"
    CHAIR = "chair"
    BED = "bed"
    CLOSET = "closet"
    DRAWER = "drawer"

class MaterialEnum(str, PyEnum):
    WOOD = "wood"
    METAL = "metal"
    PLASTIC = "plastic"

class CountryEnum(str, PyEnum):
    AZERBAIJAN = "azerbaijan"
    UNITED_STATES = "united_states"
    RUSSIAN_FEDERATION = "russian_federation"
    UKRAINE = "ukraine"
    UNITED_KINGDOM = "united_kingdom"
    BELARUS = "belarus"
    ITALY = "italy"
    GERMANY = "germany"
    IRELAND = "ireland"

class OTPPurposeEnum(str, PyEnum):
    USER_REGISTER = "user_register"

class StatusEnum(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CONTACT_VERIFICATION = "contact_verification"

metadata = MetaData()

Furniture = Table(
    "furniture",
    metadata,
    Column("id", Integer, index=True, primary_key=True, nullable=False),
    Column("fullname", String, index=True, nullable=False),
    Column("description", String, nullable=False),
    Column("price", Float, nullable=False),
    Column("category", Enum(CategoryEnum), nullable=False),
    Column("material", Enum(MaterialEnum), nullable=False),
    Column("manufacturer", Enum(CountryEnum), nullable=False),
    Column("image_url", String, nullable=False)
)

User = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_uuid", UUID(as_uuid=True), default=uuid.uuid4),
    Column("fullname", String, nullable=True, unique=False),
    Column("email", String, nullable=False, unique=True),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("hashed_password", String, nullable=False),
    Column("status", Enum(StatusEnum), nullable=False)
    # Column("furniture_id", Integer, ForeignKey(Furniture.c.id), nullable=False)
)

OTP = Table(
    "otp",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("purpose", Enum(OTPPurposeEnum), nullable=False),
    Column("otp_code", Integer, nullable=False),
    Column("user_id", Integer, ForeignKey(User.c.id), nullable=False),
    Column("implementation_time", TIMESTAMP, default=lambda: datetime.utcnow()),
    Column("expiration_time", TIMESTAMP, default=lambda: datetime.utcnow() + timedelta(minutes=1)),
)
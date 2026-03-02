from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ------- Enums -------

class ChatStatus(str, Enum):
    bot = "bot"
    human = "human"
    paused = "paused"

class MessageDirection(str, Enum):
    incoming = "in"
    outgoing = "out"

class MessageType(str, Enum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    document = "document"
    sticker = "sticker"

class BroadcastStatus(str, Enum):
    pending = "pending"
    sending = "sending"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class UserRole(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    agent = "agent"


# ------- Auth -------

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ------- Company -------

class CompanyCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None
    evolution_instance: Optional[str] = None
    evolution_apikey: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    evolution_instance: Optional[str] = None
    evolution_apikey: Optional[str] = None
    is_active: Optional[bool] = None
    plan_status: Optional[str] = None


# ------- Contact -------

class ContactUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[dict] = None
    notes: Optional[str] = None

class TagApply(BaseModel):
    tag_ids: List[str]


# ------- Message -------

class SendMessageRequest(BaseModel):
    contact_id: str
    message_type: MessageType = MessageType.text
    content: str
    media_url: Optional[str] = None


# ------- Broadcast -------

class BroadcastCreate(BaseModel):
    title: str
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    target_tags: Optional[List[str]] = []
    target_phone_list: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None


# ------- Evolution Webhook -------

class EvolutionWebhookPayload(BaseModel):
    event: str
    instance: str
    data: dict
    date_time: Optional[str] = None
    server_url: Optional[str] = None
    apikey: Optional[str] = None


# ------- User -------

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: UserRole = UserRole.agent
    company_id: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_online: Optional[bool] = None

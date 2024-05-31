from pydantic import BaseModel, EmailStr


class HostCreateModel(BaseModel):
    name: str


class HostRegisterModel(BaseModel):
    ip_address: str
    port: int
    host_os: str
    cpu_count: int
    ram_count:int
    vm_type: str


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str


class UserRegisterModel(BaseModel):
    username: str
    email: EmailStr
    password: str
from pydantic import BaseModel, SecretStr


class AuthPayload(BaseModel):
    identifier: str
    password: str


class AuthResponse(BaseModel):
    jwt: SecretStr

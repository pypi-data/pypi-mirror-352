from pydantic import BaseModel, Field, field_validator


class AuthConfig(BaseModel):
    username: str
    client_id: str
    base_url: str
    token: str

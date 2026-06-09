from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db


def verify_token(x_api_token: str | None = Header(default=None), settings: Settings = Depends(get_settings)) -> None:
    if settings.api_token and settings.api_token != 'change-this-token':
        if x_api_token != settings.api_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or missing X-API-Token header')


DbDep = Depends(get_db)
TokenDep = Depends(verify_token)

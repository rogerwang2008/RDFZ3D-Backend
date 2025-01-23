from fastapi import HTTPException
from sqlmodel import Session, select, col

from . import db


# def get_user_by_id(session: Session, user_id: int) -> models.UserAccount:
#     statement = select(models.UserAccount).where(models.UserAccount.id == user_id)
#     user = session.exec(statement).one_or_none()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# 没用。fastapi_users 全封装好了

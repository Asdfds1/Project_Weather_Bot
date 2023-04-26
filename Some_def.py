from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from typing import Optional
from slqite import User

def check_user_id(user_id: int, _session) -> bool:
    session = _session
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return True
    except (InvalidRequestError, NoResultFound):
        return False
def get_user_by_id(user_id, _session) -> User:
    try:
        user = _session.query(User).filter_by(id=user_id).one()
        return user
    except (InvalidRequestError, NoResultFound):
        return None
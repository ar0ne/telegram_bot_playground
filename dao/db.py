from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from models import Base, User
from typing import Any, Dict, List, Optional


class DataBaseConnector:
    def __init__(self, url: str):
        self._engine = create_engine(url, echo=True)
        self.Session = sessionmaker(bind=self._engine)

        Base.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class UserDao:
    def __init__(self, conn):
        assert conn is not None, "Connection must be not null!"
        self.conn = conn

    def get_all(self) -> List[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            users = session.query(User).all()
            return [user._asdict() for user in users]

    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            user = session.query(User).get(id)
            if user:
                return user._asdict()

    def add(self, id: int, username: str, first_name: str, last_name: str) -> None:
        with self.conn.session_scope() as session:
            user = User(id=id, username=username, first_name=first_name, last_name=last_name)
            session.add(user)

    def update(self, id: int, username: str = None, first_name: str = None, last_name: str = None) -> None:
        with self.conn.session_scope() as session:
            user = session.query(User).get(id)
            if user:
                user.username = username if username is not None else user.username
                user.first_name = first_name if first_name is not None else user.first_name
                user.last_name = last_name if last_name is not None else user.last_name
            else:
                self.add(id=id, username=username, first_name=first_name, last_name=last_name)

    def delete(self, id: int) -> None:
        with self.conn.session_scope() as session:
            obj = session.query(User).filter(User.id == id).first()
            session.delete(obj)


if __name__ == '__main__':
    conn = DataBaseConnector('sqlite:///:memory:')
    userDao = UserDao(conn)
    print(userDao.get_all())
    userDao.add(1, 'hello', 'first', 'second')
    print(userDao.get_all())
    first_id = userDao.get_all()[0]['id']
    userDao.update(id=first_id, username='updated')
    print(userDao.get_all())
    print(userDao.get_by_id(first_id))

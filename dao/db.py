from sqlalchemy import create_engine, inspect
from contextlib import contextmanager
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from models import Base, User, Command
from typing import Any, Dict, List, Optional


class DataBaseConnector:
    def __init__(self, url: str):
        self._engine = create_engine(url, echo=True)
        self.Session = sessionmaker(bind=self._engine)

        Base.metadata.create_all(self._engine)

        # workaround for automap
        self.AutoMappedBase = automap_base()
        self.AutoMappedBase.prepare(self._engine, reflect=True)

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


class BaseDao:
    def __init__(self, conn: DataBaseConnector, entity_clazz):
        assert conn is not None, "Connection must be not null!"
        assert entity_clazz is not None, "Entity clazz must be not null!"
        self.conn = conn
        self.entity_clazz = entity_clazz

    def get_all(self) -> List[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            objects = session.query(self.entity_clazz).all()
            return [obj._asdict() for obj in objects]

    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz).get(id)
            if obj:
                return obj._asdict()

    def delete(self, id: int) -> None:
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz).filter(self.entity_clazz.id == id).first()
            session.delete(obj)


class UserDao(BaseDao):

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


class CommandDao(BaseDao):

    def add(self, id: int, name: str) -> None:
        with self.conn.session_scope() as session:
            obj = self.entity_clazz(id=id, name=name)
            session.add(obj)


class StatisticsDao:

    def _asdict(self, obj):
        return {
            c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs
        }

    def __init__(self, conn: DataBaseConnector, entity_clazz):
        assert conn is not None, "Connection must be not null!"
        assert entity_clazz is not None, "Entity clazz must be not null!"
        self.conn = conn
        self.entity_clazz = entity_clazz

    def get_all(self) -> List[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            objects = session.query(self.entity_clazz).all()
            return [self._asdict(obj) for obj in objects]

    def increment(self, user_id: int, command_id: int) -> None:
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz).filter(user_id == user_id).filter(command_id == command_id).first()
            if obj:
                obj.count += 1
            else:
                session.add(self.entity_clazz(user_id=user_id, command_id=command_id, count=1))


if __name__ == '__main__':
    conn = DataBaseConnector('sqlite:///:memory:')
    userDao = UserDao(conn, User)
    print(userDao.get_all())
    userDao.add(1, 'hello', 'first', 'second')
    print(userDao.get_all())
    first_user_id = userDao.get_all()[0]['id']
    userDao.update(id=first_user_id, username='updated')
    print(userDao.get_all())
    print(userDao.get_by_id(first_user_id))

    commandDao = CommandDao(conn, Command)
    commandDao.add(1, 'help')
    commandDao.add(2, 'say')

    print(commandDao.get_all())

    statDao = StatisticsDao(conn, conn.AutoMappedBase.classes.statistics)
    print(statDao.get_all())
    statDao.increment(first_user_id, 1)
    statDao.increment(first_user_id, 1)
    statDao.increment(first_user_id, 1)
    print(statDao.get_all())

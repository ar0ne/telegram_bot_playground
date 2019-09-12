from sqlalchemy import create_engine, inspect
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from .models import Base, User, Command
from typing import Any, Dict, List, Optional


class DataBaseConnector:
    def __init__(self, url: str = None):
        assert url is not None, "Can't create DataBase connector"

        self._engine = create_engine(url, echo=True)
        self.Session = sessionmaker(bind=self._engine)

        self.base = Base
        self.base.metadata.create_all(self._engine)
        self.base.prepare(self._engine, reflect=True)

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
    def __init__(self, connector: DataBaseConnector = None):
        assert connector is not None, "Connection must be not null!"
        self.conn = connector

    @property
    def entity_clazz(self):
        raise Exception("Entity clazz must be not null!")

    def get_all(self) -> List[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            objects = session.query(self.entity_clazz).all()
            return [self._asdict(obj) for obj in objects]

    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz).get(id)
            if obj:
                return self._asdict(obj)

    def delete(self, id: int) -> None:
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz) \
                .filter(self.entity_clazz.id == id) \
                .first()
            session.delete(obj)

    def _asdict(self, obj):
        return {
            c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs
        }


class UserDao(BaseDao):
    entity_clazz = User

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
    entity_clazz = Command

    def add(self, id: int, name: str) -> None:
        with self.conn.session_scope() as session:
            obj = self.entity_clazz(id=id, name=name)
            session.add(obj)

    def get_by_name(self, name: str):
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz) \
                .filter(self.entity_clazz.name == name) \
                .first()
            if obj:
                return self._asdict(obj)


class StatisticsDao(BaseDao):

    @property
    def entity_clazz(self):
        return self.conn.base.classes.statistics

    def get_all(self) -> List[Dict[str, Any]]:
        with self.conn.session_scope() as session:
            objects = session.query(UserDao.entity_clazz.id,
                                    UserDao.entity_clazz.username,
                                    CommandDao.entity_clazz.name,
                                    self.entity_clazz.count) \
                .join(UserDao.entity_clazz) \
                .join(CommandDao.entity_clazz) \
                .order_by(UserDao.entity_clazz.id) \
                .all()

            users = {}
            for r in objects:
                if r[0] not in users:
                    users[r[0]] = {'id': r[0], 'username': r[1], 'statistics': []}
                else:
                    users[r[0]]['statistics'].append({'cmd': r[2], 'count': r[3]})

            return list(users.values())

    def increment(self, user_id: int, command_id: int) -> None:
        with self.conn.session_scope() as session:
            obj = session.query(self.entity_clazz) \
                .filter_by(command_id=command_id) \
                .filter_by(user_id=user_id) \
                .first()
            if obj:
                obj.count += 1
            else:
                session.add(self.entity_clazz(user_id=user_id, command_id=command_id, count=1))


if __name__ == '__main__':
    conn = DataBaseConnector('sqlite:///:memory:')
    userDao = UserDao(conn)
    print(userDao.get_all())
    userDao.add(1, 'hello', 'first', 'second')
    print(userDao.get_all())
    first_user_id = userDao.get_all()[0]['id']
    userDao.update(id=first_user_id, username='updated')
    print(userDao.get_all())
    print(userDao.get_by_id(first_user_id))

    commandDao = CommandDao(conn)
    commandDao.add(1, 'help')
    commandDao.add(2, 'say')

    print(commandDao.get_all())

    statDao = StatisticsDao(conn)
    print(statDao.get_all())
    statDao.increment(first_user_id, 1)
    statDao.increment(first_user_id, 1)
    statDao.increment(first_user_id, 1)
    print(statDao.get_all())

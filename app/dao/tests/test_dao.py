"""
Unittests for DAO.
"""
from unittest import TestCase

from app.dao.db import DataBaseConnector, UserDao, CommandDao, StatisticsDao


class BaseDaoTestCase(TestCase):
    def setUp(self):
        conn = DataBaseConnector('sqlite:///:memory:')
        self.user_dao = UserDao(conn)
        self.command_dao = CommandDao(conn)
        self.stat_dao = StatisticsDao(conn)


class TestUserDao(BaseDaoTestCase):
    """ Unit tests for User Dao"""

    def test_get_all(self):
        """ tests getting user entity """
        self.assertEqual([], self.user_dao.get_all())

        self.user_dao.add(1, 'hello', 'first', 'second')

        users = self.user_dao.get_all()

        self.assertIsNotNone(users)
        self.assertEqual(1, len(users))

        user = users[0]

        self.assertEqual(1, user['id'])
        self.assertEqual('hello', user['username'])
        self.assertEqual('first', user['first_name'])
        self.assertEqual('second', user['last_name'])

    def test_update_user(self):
        """ Tests updating user entity """
        user_id = 1
        self.user_dao.add(user_id, 'hello', 'first', 'second')

        self.user_dao.update(id=user_id, username='updated')

        updated_user = self.user_dao.get_by_id(user_id)

        self.assertIsNotNone(updated_user)

        if updated_user:
            self.assertEqual(user_id, updated_user['id'])
            self.assertEqual('updated', updated_user['username'])
            self.assertEqual('first', updated_user['first_name'])
            self.assertEqual('second', updated_user['last_name'])


class TestCommandDao(BaseDaoTestCase):
    """ Unit tests for Command Dao"""

    def test_get_all(self):
        """ Tests getting all entities """
        self.assertEqual([], self.command_dao.get_all())

        self.command_dao.add(1, 'help')
        self.command_dao.add(2, 'say')

        commands = self.command_dao.get_all()

        self.assertEqual(2, len(commands))


class TestStatisticsDao(BaseDaoTestCase):
    """ Unit tests for Statistics Dao"""

    def setUp(self):
        super().setUp()

        self.user_id = 1
        self.command_id = 1
        self.user_dao.add(self.user_id, 'hello', 'first', 'second')
        self.command_dao.add(self.command_id, 'help')

    def test_get_all(self):
        """ Tests getting all entities """
        self.assertEqual([], self.stat_dao.get_all())

        self.stat_dao.increment(self.user_id, self.command_id)
        self.stat_dao.increment(self.user_id, self.command_id)
        self.stat_dao.increment(self.user_id, self.command_id)

        statistics = self.stat_dao.get_all()
        self.assertIsNotNone(statistics)

        self.assertEqual(1, len(statistics))

        command_statistic = statistics[0]

        self.assertEqual('hello', command_statistic['username'])
        self.assertIsNotNone(command_statistic['id'])

        stats = command_statistic['statistics']
        self.assertIsNotNone(stats)
        self.assertEqual(1, len(stats))

        self.assertEqual('help', stats[0]['cmd'])
        self.assertEqual(3, stats[0]['count'])

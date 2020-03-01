from sqlalchemy import Column, BigInteger, String, Sequence, ForeignKey, Table, Integer
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship

Base = automap_base()

Statistics = Table(
    'statistics', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('command_id', ForeignKey('commands.id'), primary_key=True),
    Column('count', Integer),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))

    commands = relationship(
        'Command',
        secondary=Statistics,
        back_populates='usages'
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, " \
            f"first_name={self.first_name}, last_name={self.last_name})"


class Command(Base):
    __tablename__ = 'commands'

    id = Column(BigInteger, Sequence('command_id_seq'), primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    usages = relationship(
        'User',
        secondary=Statistics,
        back_populates='commands'
    )

"""Test serializing sqlalchemy models"""

from helper import SkippableTest

import jsonpickle

try:
    import sqlalchemy as sqa
    from sqlalchemy import orm
    from sqlalchemy.ext import declarative
    from sqlalchemy.orm import Session

    HAS_SQA = True
except ImportError:
    HAS_SQA = False

if HAS_SQA:
    # sqlalchemy.ext.declarative.declarative_base() was deprecated in SQLAlchemy 2.0
    # and replaced by sqlalchemy.orm.declarative_base().
    if hasattr(orm, 'declarative_base'):
        Base = orm.declarative_base()
    else:
        Base = declarative.declarative_base()

    class Table(Base):
        __tablename__ = 'table'
        id = sqa.Column(sqa.Integer, primary_key=True)
        name = sqa.Column(sqa.Text)
        value = sqa.Column(sqa.Float)


class SQLAlchemyTestCase(SkippableTest):

    def setUp(self):
        """Create a new sqlalchemy engine for the test"""
        if HAS_SQA:
            url = 'sqlite:///:memory:'
            self.engine = sqa.create_engine(url)
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
            self.should_skip = False
        else:
            self.should_skip = True

    def test_sqlalchemy_roundtrip_with_detached_session(self):
        """Test cloned SQLAlchemy objects detached from any session"""
        if self.should_skip:
            return self.skip('sqlalchemy is not installed')
        expect = Table(name='coolness', value=11.0)
        session = Session(bind=self.engine, expire_on_commit=False)
        session.add(expect)
        session.commit()
        jsonstr = jsonpickle.dumps(expect)
        actual = jsonpickle.loads(jsonstr)
        # actual is a shadow object; it cannot be added to the same
        # session otherwise sqlalchemy will detect an identity conflict.
        # To make this work we use expire_on_commit=True so that sqlalchemy
        # allows us to do read-only operations detached from any session.
        assert expect.id == actual.id
        assert expect.name == actual.name
        assert expect.value == actual.value

    def test_sqlalchemy_roundtrip_with_two_sessions(self):
        """Test cloned SQLAlchemy objects attached to a secondary session"""
        if self.should_skip:
            return self.skip('sqlalchemy is not installed')
        expect = Table(name='coolness', value=11.0)
        session = Session(bind=self.engine, expire_on_commit=False)
        session.add(expect)
        session.commit()
        jsonstr = jsonpickle.dumps(expect)
        actual = jsonpickle.loads(jsonstr)
        # actual is a shadow object; it cannot be added to the same
        # session otherwise sqlalchemy will detect an identity conflict.
        # To make this work we use expire_on_commit=True so that sqlalchemy
        # allows us to do read-only operations detached from any session.
        assert expect.id == actual.id
        assert expect.name == actual.name
        assert expect.value == actual.value

    def test_sqlalchemy_with_dynamic_table(self):
        """Test creating a table dynamically, per #180"""
        if self.should_skip:
            return self.skip('sqlalchemy is not installed')
        meta = sqa.MetaData()
        expect = sqa.Table(
            'test',
            meta,
            sqa.Column('id', sqa.Integer()),
            sqa.Column('text', sqa.Text()),
        )
        jsonstr = jsonpickle.dumps(expect)
        actual = jsonpickle.loads(jsonstr)
        assert expect.__class__ == actual.__class__
        assert expect.name == actual.name
        # These must be unique instances
        assert expect.metadata != actual.metadata
        # Columns names must exactly match
        assert sorted(expect.columns.keys()) == sorted(actual.columns.keys())
        # As should the types
        assert expect.c.id.name == actual.c.id.name
        assert expect.c.id.type.__class__ == actual.c.id.type.__class__
        assert expect.c.text.name == actual.c.text.name
        assert expect.c.text.type.__class__ == actual.c.text.type.__class__

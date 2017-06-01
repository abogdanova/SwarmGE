from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, PickleType
from sqlalchemy.orm import sessionmaker
from representation.tree import Tree


# Define the database as being in-memory.
engine = create_engine('sqlite:///:memory:', echo=True)

# Define the base class as a declarative SQLAlchemy class.
Base = declarative_base()

# Create a session with which to talk to the database.
Session = sessionmaker(bind=engine)


class Snippets(Base):
    """
    Data class for describing a library of code snippets.
    """

    # Define the name of the table
    __tablename__ = 'snippets'
    
    id = Column(Integer, primary_key=True)
    phenotype = Column(String)
    fitness = Column(Integer)
    tree = Column(PickleType)
    root = Column(String)

    def __repr__(self):
        return "<Snippet(phenotype='%s', root='%s', fitness='%s')>" % (
               self.phenotype, self.root, self.fitness)


class TestCase(Base):
    """
    Data class for describing a library of test cases.
    """

    # Define the name of the table
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True)
    input = Column(String)
    output = Column(String)
    start = Column(Integer)
    end = Column(Integer)


class Relation(Base):
    """
    Data class that relates Snippets to TestCase instances.
    """
    
    # Define the name of the table
    __tablename__ = 'relations'

    id = Column(Integer, primary_key=True)


# Create the databases.
Base.metadata.create_all(engine)

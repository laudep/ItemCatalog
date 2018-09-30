from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class User(Base):
    """Class for user data

    Attributes:
        id      (int): user id
        name    (str): name of the user
        email   (str): user email address
        picture (str): URL for user picture
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String)


class Category(Base):
    """Class for category data

    Attributes:
        id      (int): category id
        name    (str): category name
        user_id (int): id of user who created the category
    """
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    """Class for catalog item data

    Attributes:
        id          (int): category id
        name        (str): item name
        description (str): item description
        category_id (int): id of the corresponding item category
        price       (str): price for the item
        user_id     (int): id of user who created the category
    """

    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(
        "Category", backref=backref("catalog_items", cascade="all, delete"))
    price = Column(String(8))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': '$' + self.price,
            'category_id': self.category_id,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)

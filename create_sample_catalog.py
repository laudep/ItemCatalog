"""
    Drop and create all database tables.
    Populate item catalog database with sample item data.

    Test data descriptions source: Wikipedia
"""
import sys
import warnings
from database_setup import *
from application import session

def createCategory(name, user_id):
    """ Create an item category """
    c = Category(name=name, user_id=user_id)
    session.add(c)
    session.commit()
    print "Category", name, "created."
    return c


def createItem(name, category, price, user_id):
    """ Create an item """
    try:
        description = wikipedia.summary(name)
    except wikipedia.exceptions.DisambiguationError as e:
        description = wikipedia.summary(name + " " + category.name)

    i = Item(name=name, description=description, category_id=category.id, price=price, user_id=user_id)
    session.add(i)
    session.commit()
    print "Item", name, "added."
    return i


def createUser(name, email, picture):
    """ Create a user """
    u = User(name=name, email=email, picture=picture)
    session.add(u)
    session.commit()
    print "User", name, "created."
    return u


def checkPipInstalled():
    """ Source: https://github.com/anhaidgroup/py_entitymatching/blob/master/setup.py """
    # Check if pip is installed. If not, raise an ImportError
    PIP_INSTALLED = True

    try:
        import pip
    except ImportError:
        PIP_INSTALLED = False

    if not PIP_INSTALLED:
        raise ImportError('pip is not installed.')


def install_and_import(package):
    """ Source: https://github.com/anhaidgroup/py_entitymatching/blob/master/setup.py """
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        checkPipInstalled()
        try:
            from pip import main as pipmain
        except:
            from pip._internal import main as pipmain
        pipmain(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


# install wikipedia using PIP if necessary
install_and_import('wikipedia')

# Clear database tables
clearDatabase()

# Create sample data
print "Generating sample data..."
sampleUser = createUser('Sample Data', 'john@smith.com',
                        'https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png')

fruit = createCategory('Fruit', sampleUser.id)
vegetables = createCategory('Vegetables', sampleUser.id)

# supress BeautifulSoup warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")

createItem('Apple',
           fruit,
           '0.49',
           sampleUser.id)

createItem('Banana',
           fruit,
           '0.29',
           sampleUser.id)

createItem('Grapes',
           fruit,
           '1.99',
           sampleUser.id)

createItem('Oranges',
           fruit,
           '0.59',
           sampleUser.id)

createItem('Strawberries',
           fruit,
           '2.22',
           sampleUser.id)

createItem('Broccoli',
           vegetables,
           '1.99',
           sampleUser.id)

createItem('Eggplant',
           vegetables,
           '1.99',
           sampleUser.id)

createItem('Lettuce',
           vegetables,
           '2.50',
           sampleUser.id)

createItem('Spinach',
           vegetables,
           '3',
           sampleUser.id)

createItem('Tomato',
           vegetables,
           '3',
           sampleUser.id)


print "Database refreshed and filled with sample data."

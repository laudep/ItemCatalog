from functools import wraps
from flask import Flask, render_template, flash
from flask import request, redirect, jsonify, url_for, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import SingletonThreadPool
from database_setup import Base, Item, Category, User
import random
import string
from pprint import pprint

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
                       poolclass=SingletonThreadPool)
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))

# Unauthorized alert
ALERT_UNAUTHORIZED = ("<script>function myFunction() {"
                      "alert('You are not authorized!')}"
                      "</script><body onload='myFunction()'>")


def login_required(f):
    """Login required decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# --------------------------------------
# JSON APIs to show Catalog information
# --------------------------------------
@app.route('/api/v1/catalog/JSON')
@app.route('/api/v1/catalog/json')
def showCatalogJSON():
    """Return JSON of all items in catalog"""
    items = session.query(Item).order_by(Item.id.desc())
    return jsonify(Items=[i.serialize for i in items])


@app.route(
    '/api/v1/categories/<int:category_id>/item/<int:catalog_item_id>/JSON')
@app.route(
    '/api/v1/categories/<int:category_id>/item/<int:catalog_item_id>/json')
def ItemJSON(category_id, catalog_item_id):
    """Return JSON of selected item in catalog"""
    Catalog_Item = session.query(
        Item).filter_by(id=catalog_item_id).first()
    return jsonify(Catalog_Item=Catalog_Item.serialize)


@app.route('/api/v1/categories/JSON')
@app.route('/api/v1/categories/json')
def categoriesJSON():
    """Return JSON with all categories in catalog"""
    categories = session.query(Category).all()
    return jsonify(Categories=[r.serialize for r in categories])


# --------------------------------------
# CRUD for categories
# --------------------------------------
# READ - home page: shows categories and recently added items
@app.route('/')
@app.route('/categories/')
def showCatalog():
    """Return catalog page with all categories and recently added items"""
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc())
    quantity = items.count()
    if 'username' not in login_session:
        return render_template(
            'public_catalog.html',
            categories=categories, items=items, quantity=quantity)
    else:
        return render_template(
            'catalog.html',
            categories=categories, items=items, quantity=quantity)


# CREATE - New category
@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    """Allow user to create new category"""
    if request.method == 'POST':
        print(login_session)
        if 'user_id' not in login_session and 'email' in login_session:
            login_session['user_id'] = getUserId(login_session['email'])
        newCategory = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        if not newCategory.name:
            flash("Category name is required.", "warning")
            return render_template('new_category.html')
        session.add(newCategory)
        session.commit()
        flash("New category created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_category.html')


# EDIT a category
@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """Allow user to edit an existing category"""
    editedCategory = session.query(
        Category).filter_by(id=category_id).first()
    if editedCategory.user_id != login_session['user_id']:
        return ALERT_UNAUTHORIZED
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            session.add(editedCategory)
            session.commit()
            flash(
                'Successfully edited category "%s".' % editedCategory.name,
                'success')
            return redirect(url_for('showCatalog'))
        else:
            flash("Category name is required.", "warning")
            return render_template('edit_category.html',
                                   category=editedCategory)
    else:
        return render_template(
            'edit_category.html', category=editedCategory)


# DELETE a category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """Allow user to delete an existing category"""
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).first()
    if categoryToDelete.user_id != login_session['user_id']:
        return ALERT_UNAUTHORIZED
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name, 'success')
        session.commit()
        return redirect(
            url_for('showCatalog', category_id=category_id))
    else:
        return render_template(
            'delete_category.html', category=categoryToDelete)


# --------------------------------------
# CRUD for category items
# --------------------------------------
# READ - show category items
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def showCategoryItems(category_id):
    """Return all items in given category.

    Args:
        category_id (int): The id of the category of the items.

    Returns:
        The rendered catalog template with all item data.
    """
    category = session.query(Category).filter_by(id=category_id).first()
    categories = session.query(Category).all()
    creator = getUserInfo(category.user_id)
    items = session.query(
        Item).filter_by(
            category_id=category_id).order_by(Item.id.desc())
    quantity = items.count()
    return render_template(
        'catalog_menu.html',
        categories=categories,
        category=category,
        items=items,
        quantity=quantity,
        creator=creator)


# READ ITEM - shows specific information for a given item
@app.route('/categories/<int:category_id>/item/<int:catalog_item_id>/')
def showItem(category_id, catalog_item_id):
    """Return a single catalog item

    Args:
        category_id     (int): The id of the item category.
        catalog_item_id (int): The id of the item.

    Returns:
        The rendered catalog template.
    """
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(
        Item).filter_by(id=catalog_item_id).first()
    creator = getUserInfo(category.user_id)
    return render_template(
        'catalog_menu_item.html',
        category=category, item=item, creator=creator)


# CREATE NEW ITEM
@app.route('/categories/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    """Handle new catalog item creation"""
    categories = session.query(Category).all()
    if request.method == 'POST':
        addNewItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        if not addNewItem.name:
            flash("Item name is required.", "warning")
            return render_template('new_item.html', categories=categories)
        session.add(addNewItem)
        session.commit()
        flash("New item created.", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_item.html', categories=categories)


# UPDATE ITEM
@app.route(
    '/categories/<int:category_id>/item/<int:catalog_item_id>/edit',
    methods=['GET', 'POST'])
@login_required
def editItem(category_id, catalog_item_id):
    """Handle catalog item editing

    Args:
        category_id     (int): The id of the item category.
        catalog_item_id (int): The id of the item to edit.
    """
    editedItem = session.query(
        Item).filter_by(id=catalog_item_id).first()
    if editedItem.user_id != login_session['user_id']:
        return ALERT_UNAUTHORIZED
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['category']:
            editedItem.category_id = int(request.form['category'])
        session.add(editedItem)
        session.commit()
        flash("Catalog item updated!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).all()
        return render_template(
            'edit_catalog_item.html',
            categories=categories,
            item=editedItem)


# DELETE ITEM
@app.route(
    '/categories/<int:category_id>/item/<int:catalog_item_id>/delete',
    methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, catalog_item_id):
    """Handle catalog item deletion

    Args:
        category_id     (int): The id of the item category.
        catalog_item_id (int): The id of the item to delete.
    """
    itemToDelete = session.query(
        Item).filter_by(id=catalog_item_id).first()
    if itemToDelete.user_id != login_session['user_id']:
        return ALERT_UNAUTHORIZED
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted', 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'delete_catalog_item.html', item=itemToDelete)


# --------------------------------------
# Login Handling
# --------------------------------------

# Login route, create anit-forgery state token
@app.route('/login')
def showLogin():
    """Show the login screen"""
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Handle Facebook OAuth login"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s&'
           'fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.1/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = ('https://graph.facebook.com/v3.1/me?fields=id'
           '%2Cname%2Cemail%2Cpicture&access_token=') + access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session
    # in order to properly logout
    login_session['access_token'] = access_token

    # Get user picture
    login_session['picture'] = data["picture"]["data"]["url"]

    # see if user exists
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')

    flash("Now logged in as %s." % login_session['username'], 'success')
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Handle Facebook OAuth logout"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."


# CONNECT - Google login get token
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Handle Google OAuth login"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        dumpMessage = 'Current user is already connected.'
        response = make_response(json.dumps(dumpMessage), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)
    login_session['provider'] = 'google'
    if 'name' in data:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email'].split("@")[0]
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("You are now logged in as %s" % login_session['username'], 'success')
    print("done!")
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """Handle Google OAuth logout"""
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_toke
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # token given is invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# User helper functions
def getUserId(email):
    """Get a user id given an email address

    Args:
        email (str): The email address of the user.

    Returns:
        int: The user's id
    """
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    """Get user info given an id

    Args:
        user_id (int): The user's id

    Returns:
        User: The user object
    """
    user = session.query(User).filter_by(id=user_id).first()
    return user


def createUser(login_session):
    """Save the currently logged in user in the database

    Args:
        login_session (Tuple[string]): The current login session.

    Returns:
        int: The created user's id
    """
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


@app.route('/disconnect')
def disconnect():
    """Handle logout/disconnect based on provider"""
    print(login_session)
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            if 'gplus_id' in login_session:
                del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in", 'danger')
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

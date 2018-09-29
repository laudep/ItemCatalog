# Item Catalog

A web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Everyone can view the catalog. Registered users are able to post, edit and delete their own items.

## About

This project was made as part of the Udacity [Full-stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).


## Technologies
- Python
- HTML
- CSS
<br><br>
- Flask
- SQLAchemy
<br><br>
- OAuth
- Google Login
- Facebook Login

## Dependencies
### Vagrant VM
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

### Custom Environment
Instead of using the Udacity supplied Vagrant setup the app can run from any environment where the required dependencies are available.
- [Python 2.7](https://www.python.org/downloads/)
- [SQLite](https://www.sqlite.org/index.html)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask](http://flask.pocoo.org/)


## Getting Started
### Preparation (Vagrant)
- Download and install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- Clone the Vagrantfile from the [Udacity Repository](https://github.com/udacity/fullstack-nanodegree-vm)
- Clone this repository into the `Vagrant` directory
- Run the VM with `vagrant up`
- Use `vagrant ssh` to login to the VM
- (Optional) run the sample data generator script (see below)

### Adding sample data
Warning: the steps below will overwrite any existing data.<br>
The sample data generator uses the [Wikipedia API](https://pypi.org/project/wikipedia/).<br>
To run generate sample data use the following commands:
- `pip install wikipedia` (if Wikipedia module isn't installed yet)
- `python create_sample_catalog.py`
- alternativly run `sudo python create_sample_catalog.py` to automatically install Wikipedia if needed

### Running the application
- Start the app by running `python application.py` within its root directory
- Visit [https://localhost.8000/categories](https://localhost.8000/categories) with your web browser to load it
- If the sample data generator wasn't used add a few categories and items if running for the first time



## JSON Endpoints
The JSON Endpoints are case insensitive; `JSON` and `json` can be used interchangeably.
| Data                   | URL                                                                          |
|------------------------|------------------------------------------------------------------------------|
| All catalog categories | `/api/v1/categories/JSON`                                                    |
| Full item catalog      | `/api/v1/catalog/JSON`                                                       |
| Single catalog item    | `/api/v1/categories/<int:category_id>`<br>`/item/<int:catalog_item_id>/JSON` |
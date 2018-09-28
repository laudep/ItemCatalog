# Item Catalog

A web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users are able to post, edit and delete their own items.

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
- Download and install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- Clone the Vagrantfile from the [Udacity Repository](https://github.com/udacity/fullstack-nanodegree-vm)
- Clone this repository into the `Vagrant` directory
- Run the VM with `vagrant up`
- Use `vagrant ssh` to login to the VM
  <br><br>
- Start the app by running `python application.py` within its root directory
- Visit `https://localhost.8000/categories` with your web browser to load it
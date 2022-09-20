""" database dependencies to support Users db examples """
import os
import shutil
from random import randrange

from __init__ import db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Notes(db.Model):
    __tablename__ = 'notes'

    # Define the Notes schema
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text, unique=False, nullable=False)
    # Define a relationship in Notes Schema to userid who originates the note, many-to-one (many notes to one user)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))

    # Constructor of a Notes object, initializes of instance variables within object
    def __init__(self, note, userid):
        self.note = note
        self.userid = userid
    # Returns a string representation of the Notes object, similar to java toString()
    # returns string
    def __repr__(self):
        return "Notes(" + str(self.id) + "," + self.note + "," + str(self.userid) + ")"

    # CRUD create, adds a new record to the Notes table
    # returns the object added or None in case of an error
    def create(self):
        try:
            # creates a Notes object from Notes(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Notes table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read, returns dictionary representation of Notes object
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "note": self.note,
            "userid": self.userid
        }

# Define the Users table within the model
# -- Object Relational Mapping (ORM) is the key concept of SQLAlchemy
# -- a.) db.Model is like an inner layer of the onion in ORM
# -- b.) Users represents data we want to store, something that is built on db.Model
# -- c.) SQLAlchemy ORM is layer on top of SQLAlchemy Core, then SQLAlchemy engine, SQL


class Users(UserMixin, db.Model):
    # define the Users schema
    userid = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=False, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=False)
    notes = db.relationship("Notes", cascade='all, delete', backref='users', lazy=True)

    # constructor of a User object, initializes of instance variables within object
    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        self.password = password


    def __repr__(self):
        return "Users(" + str(self.userid) + "," + self.fullname + "," + str(self.email) + ")"
    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            # creates a person object from Users(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "userid": self.userid,
            "fullname": self.fullname,
            "email": self.email,
            "password": self.password,
            "notes": self.notes,
            "query": "by_alc"  # This is for fun, a little watermark
        }

    def read2(self):
        return {
            "userid": self.userid,
            "fullname": self.fullname,
            "email": self.email
        }
    # CRUD update: updates users name, password, phone
    # returns self
    def update(self, fullname="", email="", password=""):
        """only updates values with length"""
        if len(fullname) > 0:
            self.fullname = fullname
        if len(email) > 0:
            self.email = email
        if len(password) > 0:
            self.set_password(password)
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    # set password method is used to create encrypted password
    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    # check password to check versus encrypted password
    def is_password_match(self, password):
        """Check hashed password."""
        result = check_password_hash(self.password, password)
        return result
    # required for login_user, overrides id (login_user default) to implemented userid
    def get_id(self):
        return self.userid


"""Database Creation and Testing section"""


def model_builder():
    print("--------------------------")
    print("Seed Data for Table: users")
    print("--------------------------")
    db.create_all()
    """Tester data for table"""
    u1 = Users(fullname='Dylan Luo', email='dragonfly.luo@gmail.com', password='test')
    u2 = Users(fullname='Sohan Sankuratri', email='ssftype@gmail.com', password='test')
    u3 = Users(fullname='Jean Kim', email='jeaneonkim@gmail.com', password='test')
    u4 = Users(fullname='Ritvik Keerthi', email='Ritvik.Keerthi@gmail.com', password='test')
    u5 = Users(fullname='Adi Nawandhar', email='adityanawandhar0986@gmail.com', password='test')
    for row in table:
        # prime uploads folder
        try:
            os.makedirs('../volumes/uploads')
        except:
            pass
        shutil.copy("../static/HackClub.png", "../volumes/uploads")
        # add some notes with default image
        try:
            '''add a few 1 to 4 notes per user'''
            for num in range(randrange(1, 4)):
                note = "#### " + row.name + " note " + str(num) + ". \n Generated by test data."
                row.notes.append(Notes(userid=row.userid, note=note, image='HackClub.png'))
            '''add user/note data to table'''
            db.session.add(row)
            db.session.commit()
        except IntegrityError:
            '''fails with bad or duplicate data'''
            db.session.remove()
            print(f"Records exist, duplicate email, or error: {row.email}")

def model_driver():
    print("---------------------------")
    print("Create Tables and Seed Data")
    print("---------------------------")
    model_builder()

    print("---------------------------")
    print("Table: " + Users.__tablename__)
    print("Columns: ", Users.__table__.columns.keys())
    print("---------------------------")
    print("Table: " + Notes.__tablename__)
    print("Columns: ", Notes.__table__.columns.keys())
    print("---------------------------")
    print()

    users = Users.query
    for user in users:
        print("User" + "-" * 81)
        print(user.read())
        print("Notes" + "-" * 80)
        for note in user.notes:
            print(note.read())
        print("-" * 85)
        print()

def model_printer():
    print("------------")
    print("Table: users with SQL query")
    print("------------")
    result = db.session.execute('select * from users')
    print(result.keys())
    for row in result:
        print(row)


if __name__ == "__main__":
    model_driver()  # builds model of Users
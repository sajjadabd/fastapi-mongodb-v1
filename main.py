from typing import Optional

from fastapi import FastAPI
import connection
from bson import ObjectId
from json import dumps
from schematics.models import Model
from schematics.types import StringType, EmailType

from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder




class Item(BaseModel):
    email: str
    username: str
    password: str



class User(Model):
    user_id = ObjectId()
    email = EmailType(required=True)
    username = StringType(required=True)
    password = StringType(required=True)


# An instance of class User
newuser = User()

# funtion to create and assign values to the instanse of class User created
def create_user(email, username, password):
    newuser.user_id = ObjectId()
    newuser.email = email
    newuser.username = username
    newuser.password = password
    return dict(newuser)

def email_exists(email):
    user_exist = True
    if connection.db.users.find(
        {"email": email}
    ).count() == 0:
        user_exist = False
        return user_exist

def check_login_creds(email, password):
    if not email_exists(email):
        activeuser = connection.db.users.find(
            {"email": email}
        )
        for actuser in activeuser:
            actuser = dict(actuser)
            actuser['_id'] = str(actuser['_id'])    
            return actuser


app = FastAPI()


# Our root endpoint
@app.get("/")
def index():
    return {"message": "Hello MongoDB"}

# Signup endpoint with the POST method
@app.post("/signup")
def signup(data : Item):
    user_exists = False
    #data = create_user(email, username, password)
    #data = jsonable_encoder(data) 
    # Covert data to dict so it can be easily inserted to MongoDB
    #data = dict(data)

    # Checks if an email exists from the collection of users
    if connection.db.users.find(
        {"email": data.email}
        ).count() > 0:
        user_exists = True
        print("USer Exists")
        return {"message":"User Exists"}
    # If the email doesn't exist, create the user
    elif user_exists == False:
        connection.db.users.insert_one(dict(data))
        return { 
          "message":"User Created",
          "email": data.email, 
          "username": data.username, 
          "password": data.password
        }

# Login endpoint
@app.get("/login/{email}/{password}")
def login(email, password):
    def log_user_in(creds):
        if creds['email'] == email and creds['password'] == password:
            return {"message": creds['username'] + ' successfully logged in'}
        else:
            return {"message":"Invalid credentials!!"}
    # Read email from database to validate if user exists and checks if password matches
    logger = check_login_creds(email, password)
    if bool(logger) != True:
        if logger == None:
            logger = "Invalid Email"
            return {"message":logger}
    else:
        status = log_user_in(logger)
        return {"Info":status}
from .utils.cxplogging import logging
from .utils.easy_imports import *
from .utils.database import db
from .utils.database import MysqlDB
from .utils.database import mongo
from .utils.database import redis
debug()

database_dict={}
def add_db(name,database):
    database_dict[name]=database
def get_db(name):
    return database_dict[name]


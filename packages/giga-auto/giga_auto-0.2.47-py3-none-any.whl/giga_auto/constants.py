import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "giga_auto", "config")

class DBType:
    oracle = 'oracle'
    mysql = 'mysql'
    sqlserver = 'sqlserver'
    mongodb = 'mongodb'
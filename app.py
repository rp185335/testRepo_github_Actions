
from main import main, shutdown_server
from flask import Flask
from multiprocessing import Process
from threading import Timer



app = Flask(__name__)


main()



@app.route('/')
def dummy():
    return "Processing Request",200





from main import main, shutdown_server
from flask import Flask
from multiprocessing import Process
from threading import Timer



app = Flask(__name__)


@app.route('/')
def dummy():
    main()
    return "Processing Request",200




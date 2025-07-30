from bottle import Bottle
from pathlib import Path
from .model import MaXProjectConfig

app = Bottle()


@app.get("/")
def home():
    return f"HomePage {app.max_directory}"


@app.get("/conf")
def config():
    conf_path = Path(app.max_directory, "config.xml")
    print(conf_path)
    conf = MaXProjectConfig(conf_path)
    return conf.available_bundles

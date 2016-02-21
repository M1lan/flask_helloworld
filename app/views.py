from app import app
import subprocess


@app.route('/')
@app.route('/index')
def index():
    return "Hello, Boby!"


@app.route('/version')
def version():
    cmd = ['git', 'rev-parse', 'HEAD']
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    out, err = p.communicate()
    return out

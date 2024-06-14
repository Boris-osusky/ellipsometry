# Ellipsoserver

## How to run it

### Production
#### macOS/Linux
```bash
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
gunicorn app:app
```

#### Windows
```ps1
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install -r requirements.txt
py -3 -m gunicorn app:app
```


### Development

#### macOS/Linux
```bash
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
flask run --debug --port=8000
```

#### Windows
```ps1
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install -r requirements.txt
$env:FLASK_DEBUG=1
py -3 -m flask run --port=8000
```

### Visit app

[http://127.0.0.1:8000](http://127.0.0.1:8000)

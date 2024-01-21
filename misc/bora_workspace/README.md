## Getting started

1. Clone this repo first
```bash
$ git clone https://github.com/nicolaisi/msu.git
```

2. Run the following command to pull the content of bora folder
```bash
$ git submodule update --init
```

3. Install dependencies and create virtual environment
```bash
$ python3 -m venv env
$ source env/bin/activate
$ pip3 install -r bora/requirements.txt
```

4. Launch
```bash
$ python bora/core.py
```

5. Open status page at `http://localhost:8005` and/or the designer page at `http://localhost:8005/designer`




# Node-whisper
Worked node to be deployed at the edge

## Setup
### Initial steps
```console
foo@bar:node-whisper$ python3 -m venv env
foo@bar:node-whisper$ source env/bin/activate
(env) foo@bar:node-whisper$ pip install -U openai-whisper
(env) foo@bar:node-whisper$ pip freeze > requirements.txt
(env) foo@bar:node-whisper$ python main.py
(env) foo@bar:node-whisper$ deactivate

```
### Virtual env
```console
foo@bar:node-whisper$ source env/bin/activate
(env) foo@bar:node-whisper$ python main.py -h
(env) foo@bar:node-whisper$ python main.py -m tiny -i speech.flac
(env) foo@bar:node-whisper$ deactivate
```

### Docker container
```console
foo@bar:node-whisper$ docker build -t node-whisper .
foo@bar:node-whisper$ docker run node-whisper
```

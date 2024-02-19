# Node-whisper
A worker node to be deployed in a cluster at the edge of the cloud. Loads the OpenAI Whisper framework and a selected model and opens a tcp socket on port 56789. Listens for incoming audiostreams, accepts them and queues them for transcription. Currently the transcriptions are output to stdout, so either run the application locally or in interactive mode for the containerized version.

## Format of audio
All data must be encoded in binary form, consisting of a stream with the following parts:
 - fixed 2-byte unsigned short (integer) in network byte order, specifying the length of the JSON-header in bytes
 - JSON-header: Description of the content, must contain the fields { byteorder, content-length, content-type, content-encoding }
 - Content: Bytes of a audiosignal, for example a encoded flac file.
See the testing script `client.py` for a simple example.

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
Select model to use with the `-m <model>` flag.
```console
foo@bar:node-whisper$ source env/bin/activate
(env) foo@bar:node-whisper/src$ python main.py -h
usage: main.py [-h] [-lv] [-m <tiny|small|medium|...>]

Node-Whisper

optional arguments:
  -h, --help            show this help message and exit
  -lv, --log-verbose    Enable verbose logging
  -m <tiny|small|medium|...>, --model <tiny|small|medium|...>
                        Whisper model to load
(env) foo@bar:node-whisper/src$ python main.py -m tiny|small|medium|<specify_model>
(env) foo@bar:node-whisper/src$ deactivate
```

### Docker container
Loads the tiny model as the default one, selection of model is not implemented.
```console
foo@bar:node-whisper$ docker build -t node-whisper .
foo@bar:node-whisper$ docker run -p 56789:56789/tcp -it node-whisper
```

### Send audio for transcription
A very simple testing script that demonstrates the functionality of the system. Loads the bytes from the audiofile passed as the only argument, creates needed headers and opens a connection to the whisper-node and sends the message to be processed.
```console
foo@bar:node-whisper$ python3 client.py /my/collection/flacs/speech.flac
```

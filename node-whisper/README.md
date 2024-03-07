# Node-whisper
A worker node to be deployed in a cluster at the edge of the cloud. Loads the OpenAI Whisper framework and a selected model and opens a tcp socket on port 56789. Listens for incoming audiostreams, accepts them and queues them for transcription. Currently the transcriptions are output to stdout, so either run the application locally or in interactive mode for the containerized version.

## Format of audio
All data must be encoded in binary form, consisting of a stream with the following parts:
 - fixed 2-byte unsigned short (integer) in network byte order, specifying the length of the JSON-header in bytes
 - JSON-header: Description of the content, must contain the fields { byteorder, content-length, content-type, content-encoding }
 - Content: The actual bytes of the audio signal to be processed

See the implementation of [node-client](https://github.com/kordaniel/hy-net-ai/tree/main/node-client) for a more detailed example. Currently only FLAC encoded bytestreams are supported by the whisper node.

## Setup
### Initial steps
```console
foo@bar:node-whisper$ python3 -m venv env
foo@bar:node-whisper$ source env/bin/activate
(env) foo@bar:node-whisper$ pip install -U openai-whisper
(env) foo@bar:node-whisper$ pip freeze > requirements.txt
(env) foo@bar:node-whisper$ python src/main.py
(env) foo@bar:node-whisper$ deactivate

```
### Virtual env
Select model to use with the `-m <model>` flag.
```console
foo@bar:node-whisper$ source env/bin/activate
(env) foo@bar:node-whisper$ cd src
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
Loads the tiny model as the default one, selection of model is not implemented. If you wish to use an another model you can update the Dockerfile CMD statement with the desired model.

```console
foo@bar:node-whisper$ docker build -t node-whisper .
foo@bar:node-whisper$ docker run -p 56789:56789/tcp -it node-whisper
```

### Send audio for transcription/translation
You can use the example [node-client](https://github.com/kordaniel/hy-net-ai/tree/main/node-whisper) application to test the system. Follow the instructions in it's README.md and talk in any language to send speech for the node-whisper to translate and/or transcribe

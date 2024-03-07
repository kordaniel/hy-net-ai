# Node-client
A short and simple example client application that can be used to test the system. The program will listen to the microphone, record the input and for every sentence (separated by silence), encode the sentence in flac format and send the flac bytestream to node-whisper to be processed.

To maximise the probability that the input is actually clipped into sentence segments, you can keep the mic muted and only unmute it separately for every sentence.

## Requirements
On linux systems the following packages are needed:
- portaudio19
- python3-pyaudio  

For example on debian based systems:
```console
foo@bar$ apt-get update
foo@bar$ apt-get install portaudio19 python3-pyaudio
```

## Running (with node-whisper on local device)
First start node-whisper as per it's instructions in a separate terminal. After that follow the instructions below and run the client in an another terminal. Follow the instruction of the client terminal, and enjoy the transcriptions that are outputted in the terminal of node-whisper.

## Running (with node-whisper deployed in cluster)
Start by configuring and running the cluster by following the instructions in the root [README.md](https://github.com/kordaniel/hy-net-ai) file.  
Modify the HOST and PORT variables in [main.py](main.py) to bind to the worker endpoint.  
Follow the instructions below to run the client.

## Setup
### Initial steps
```console
foo@bar:node-client$ python3 -m venv env
foo@bar:node-client$ source env/bin/activate
(env) foo@bar:node-client$ pip install -U pyaudio SpeechRecognition
(env) foo@bar:node-client$ pip freeze > requirements.txt
(env) foo@bar:node-client$ python main.py
(env) foo@bar:node-client$ deactivate

```
### Run in virtual env
```console
foo@bar:node-client$ source env/bin/activate
(env) foo@bar:node-client$ python main.py
(env) foo@bar:node-client$ deactivate
```

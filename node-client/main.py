import socket
import sys
import struct
import json

import speech_recognition as sr
# https://github.com/Uberi/speech_recognition
# https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst


r = sr.Recognizer()
mic = sr.Microphone()

# Might be needed on some systems, load selected mic with mic = sr.Microphone(device_index=mic_i)
# ###############################################################################################
#mic_i = None
#for i,m in enumerate(sr.Microphone.list_microphone_names()):
#    if m == "default":
#        mic_i = i
#        break
#if mic_i == None:
#    print("Error connecting to mic")
#    exit(1)


def send_file(flac_bytes: bytes):
    HOST = "127.0.0.1"
    PORT = 56789

    jsonheader = {
        "byteorder": sys.byteorder,
        "content-type": "binary/flac",
        "content-encoding": "flac",
        "content-length": len(flac_bytes),
    }
    jsonheader_bytes = json.dumps(jsonheader, ensure_ascii=False).encode("utf8")
    hdr = struct.pack(">H", len(jsonheader_bytes))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(hdr + jsonheader_bytes + flac_bytes)
        data = s.recv(1024)
        while data:
            print(data)
            data = s.recv(1024)


def main():
    try:
        with mic as source:
            print("Adjusting microphone, please be quiet")
            r.adjust_for_ambient_noise(source, duration=1) # duration should be > 0.5 (seconds)
            print("Adjusting done.")
            while True:
                print("Listening for sentence (mute mic to clip segment)")
                audio = r.listen(source)
                print("Sending segment to node-whisper for processing")
                send_file(audio.get_flac_data())
                print("Done")
    except KeyboardInterrupt:
        # exits with return code == 0
        print("Caught keyboard interrupt, exiting")


if __name__ == '__main__':
    main()


# transcribe using google API (library contains free-to-use apikey) =>
#transcriptions = r.recognize_google(audio, show_all=True) # => { "alternative": [], "final": bool }

#for alt in transcriptions["alternative"]:
#    print(alt)


# Load audio from local file
#speech = sr.AudioFile("jackhammer.wav") # the stale smell of old beer lingers
#
#with speech as source:
#    r.adjust_for_ambient_noise(source, duration=0.5)
#    audio = r.record(source)
#

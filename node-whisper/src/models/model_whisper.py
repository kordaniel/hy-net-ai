import logging
import threading
import time
import queue

from typing import Optional, Tuple

import whisper
import torch

from utils.io_utils import write_binary_file, delete_file


class Whisper(threading.Thread):
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    TMP_FPATH = "/tmp/node-whisper-audio-buff-"
    file_i = 0

    def __init__(self):
        super().__init__()

        self.__loaded_models = {}
        self.__queue = queue.Queue()
        self.__continue = True

    def load_model(self, model: str) -> bool:
        if model in self.__loaded_models:
            return True
        if "." in model:
            logging.error("Language specific models <model>.en are not supported")
            return False

        logging.info(f"Loading whisper model: {model}")
        t1 = time.time()
        self.__loaded_models[model] = whisper.load_model(model, device=Whisper.DEVICE)
        t2 = time.time()
        logging.debug(f"Done loading model: '{model}', in {t2-t1} seconds.")

        return True

    def transcribe(self, audio_data: bytes, whisper_model: str) -> Tuple[bool, str]:
        if not whisper_model in self.__loaded_models:
             if not self.load_model(whisper_model):
                 return False, "Requested model is not supported"

        fpath = f"{Whisper.TMP_FPATH}{Whisper.file_i}"
        Whisper.file_i += 1

        # whisper has no functions to load audio data directly, but uses ffmpeg to decode audiofiles.
        # => So we implement a quick and ugly hack to get around this annoying limitation:
        write_binary_file(fpath, audio_data)
        audio = whisper.load_audio(fpath)
        audio = whisper.pad_or_trim(audio)

        model = self.__loaded_models[whisper_model]

        t1 = time.time()
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # cleanup tmp files
        delete_file(fpath)

        _, probs = model.detect_language(mel)
        t2 = time.time()
        logging.info(f"Detected language: '{max(probs, key=probs.get)}', in {t2-t1} seconds.")
        t1 = time.time()
        # Transcribe with translation
        options = whisper.DecodingOptions(task="translate")
        result = whisper.decode(model, mel, options)
        t2 = time.time()
        logging.debug(f"Transcription completed, in {t2-t1} seconds.")
        ##Begin:print Translation, This must be usless, remove it after investging reasons
        print(result.text)
        ##End

        return True, result.text

    def enqueue_audio(self, object: Optional[Tuple[bytes, str]]) -> None:
        try:
            self.__queue.put(object, block=True, timeout=120)
        except queue.Full as ef:
            logging.warning(f"Queue is full, discarding audio input. Exception: {ef}")

    def run(self) -> None:
        '''
        Called by threading.Thread.start, the main function of the thread.
        '''
        logging.debug("Whisper thread started")
        while self.__continue:
            obj = self.__queue.get()
            if obj is None:
                break

            audio_data, whisper_model = obj
            success, transcription = self.transcribe(audio_data, whisper_model)
            self.__queue.task_done()
            # TODO: Relay transcription to user UI
            if success:
                logging.info(f"Transcription: {transcription}")
            else:
                logging.error(f"Unable to transcript: {transcription}")

    def close(self) -> None:
        self.__continue = False
        try:
            self.__queue.put(None, block=True, timeout=120)
        except queue.Full as ef:
            logging.warning(f"Queue is full, cannot close. Exception: {ef}")

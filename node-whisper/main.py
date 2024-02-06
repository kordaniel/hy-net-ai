import sys
import time
from argparse import ArgumentParser
from typing import List

import whisper
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS = {}

print("Running on python version:", sys.version)
print("Using device:", DEVICE)


def load_models(models: List[str]) -> None:
        for m in models:
            print(f"Loading model '{m}'..", end="")
            t1 = time.time()
            MODELS[m] = whisper.load_model(m, device=DEVICE)
            t2 = time.time()
            print(f" Done in {t2-t1} seconds.")
        print("All requested models loaded")


def main(fpath: str) -> None:
    print("Loading audiofile:", fpath)
    audio = whisper.load_audio(fpath)
    audio = whisper.pad_or_trim(audio)

    for m, model in MODELS.items():
        print("\nModel:", m)
        # Tiny needs different setup (?)
        if m != "tiny.en" and m != "tiny":
            t1 = time.time()
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            _, probs = model.detect_language(mel)
            t2 = time.time()
            print(f"Detected language: '{max(probs, key=probs.get)}'. Took {t2-t1} seconds.")
            t3 = time.time()    
            options = whisper.DecodingOptions()
            result = whisper.decode(model, mel, options)
            t4 = time.time()
            #print(result)
            print(result.text)
            print(f"Decoding time: {t4-t3} seconds.")


if __name__ == '__main__':
    parser = ArgumentParser(description="Node-Whisper")
    parser.add_argument(
         "-m",
         "--model",
         dest="model",
         help="Whisper model to load",
         metavar="<tiny|small|medium|...>",
         default="medium"
    )
    required_args = parser.add_argument_group("Required arguments")
    required_args.add_argument(
        "-i",
        "--input",
        dest="input_audio",
        help="filepath of audiofile to be processed",
        metavar="<filepath>",
        required=True
    )
    args = parser.parse_args()


    input_fpath = args.input_audio

    load_models([args.model])
    main(input_fpath)

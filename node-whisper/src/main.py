from argparse import ArgumentParser, Namespace
from functools import partial
import logging
import selectors
import socket
import sys
import traceback

from typing import Tuple

from services.message import Message
from models.model_whisper import Whisper


# TODO: 
#       - Implement translation (model configuration)
#       - <model>.en models not supported, needs different configuration
#       - Specify language of input for the model? (Meeting 16.2)


# Listening socket
HOST = "" # ip, hostname or empty string for all ipv4 addresses. TODO: specify address in env var?
PORT = 56789


def enqueue_audio(audio_input: Tuple[str, bytes], whisper_thread: Whisper) -> None:
        #print("Main thread got:", audio_input[0], "bytes:", len(audio_input[1]))
        # audio_input[0]: content-encoding, audio_input[1]: bytestream (audio file)
        whisper_thread.enqueue_audio((audio_input[1], args.model))


def accept_wrapper(sock, selector: selectors.DefaultSelector, whisper_thread: Whisper) -> None:
        conn, addr = sock.accept()
        logging.info(f"Accepted connection from {addr[0]}:{addr[1]}")
        conn.setblocking(False)
        message = Message(selector, conn, addr, partial(enqueue_audio, whisper_thread=whisper_thread))
        selector.register(conn, selectors.EVENT_READ, data=message)


def main(args: Namespace) -> None:
    thread_whisper = Whisper()
    thread_whisper.start()
    if not thread_whisper.load_model(args.model):
        logging.info("Whisper node shutting down")
        thread_whisper.close()
        thread_whisper.join()
        return

    sel = selectors.DefaultSelector()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    # This can happen if the server closed an connection and a new one is established
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, PORT))
    lsock.listen()
    logging.info(f"Listening TCP Socket bound to: {HOST}:{PORT}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    # Main event loop
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj, sel, thread_whisper)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        logging.warning(
                            f"Main: Error: Exception for {message.addr}:\n"
                            f"{traceback.format_exc()}"
                        )
                        message.close()
    except KeyboardInterrupt:
        # exits with return code == 0
        logging.debug("Caught keyboard interrupt, exiting")
    except Exception as e:
        # exits with return code != 0
        logging.debug("Caught exception:", e)
    finally:
        logging.info("Whisper node shutting down")
        sel.close()
        thread_whisper.close()
        thread_whisper.join()


if __name__ == '__main__':
    parser = ArgumentParser(description="Node-Whisper")
    parser.add_argument(
         "-lv",
         "--log-verbose",
         action="store_true",
         dest="log_verbose",
         help="Enable verbose logging",
         default=False
    )
    parser.add_argument(
         "-m",
         "--model",
         dest="model",
         help="Whisper model to load",
         metavar="<tiny|small|medium|...>",
         default="medium"
    )

    args = parser.parse_args()

    log_format = "[%(asctime)s] [%(threadName)-10s] [%(levelname)-8s] %(filename)s:%(lineno)d:\t%(message)s" \
        if args.log_verbose else "%(message)s"
    logging.basicConfig(
         level=logging.DEBUG if args.log_verbose else logging.INFO,
         format=log_format
    )

    logging.info("Whisper node initializing")
    logging.debug(f"Running on python version: {sys.version}")
    logging.debug(f"Attempting to bind tcp input socket to: {HOST}:{PORT}")

    main(args)

import io
import json
import selectors
import socket
import struct

from typing import Callable, Tuple

class Message:
    '''
    Wraps a network socket and keeps it open until all bytes are read, parsed and transferred to the callable to the queue.

    A message is a stream of bytes, consisting of:
        - protoheader: fixed 2-byte unsigned short in network (big-endian) byte order, holding the length of the JSON-header
        - JSON_header: a header describing the content, including length in bytes
        - Content: the actual message (audiofile)
    '''

    REQ_HEADERS = (
        "byteorder",
        "content-length",
        "content-type",
        "content-encoding"
    )


    def __init__(self,
                 selector: selectors.DefaultSelector,
                 sock: socket.socket,
                 addr: Tuple[str, int],
                 queue_cb: Callable[[Tuple[str, bytes]], None]):
        self.__selector = selector
        self.__sock = sock
        self.__addr = addr
        self.__append_to_queue_cb = queue_cb

        self.__recv_buffer = b""

        self.__jsonheader_len = None
        self.__jsonheader = None
        self.__binary_stream = None


    @property
    def addr(self) -> Tuple[str, int]:
        return self.__addr

    def process_events(self, mask: int) -> None:
        if mask & selectors.EVENT_READ:
            self.read()

    def read(self) -> None:
        self.__read()

        if self.__jsonheader_len is None:
            self.__process_protoheader()

        if self.__jsonheader_len is not None:
            if self.__jsonheader is None:
                self.__process_jsonheader()

        if self.__jsonheader:
            if self.__binary_stream is None:
                self.__process_message()

    def close(self) -> None:
        print(f"Closing connection to {self.__addr}")
        try:
            self.__selector.unregister(self.__sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.__addr}: {e!r}"
            )

        try:
            self.__sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.__addr}: {e!r}")
        finally:
            self.__sock = None # Delete reference to socket object for garbage collection

    def __process_protoheader(self) -> None:
        hdrlen = 2
        if len(self.__recv_buffer) >= hdrlen:
            # >H  == Bigendian unsigned short
            self.__jsonheader_len = struct.unpack(">H", self.__recv_buffer[:hdrlen])[0]
            self.__recv_buffer = self.__recv_buffer[hdrlen:]

    def __process_jsonheader(self) -> None:
        hdrlen = self.__jsonheader_len
        if len(self.__recv_buffer) >= hdrlen:
            self.__jsonheader = self.__json_decode(self.__recv_buffer[:hdrlen], "utf-8")
            self.__recv_buffer = self.__recv_buffer[hdrlen:]
            for reqhdr in Message.REQ_HEADERS:
                if reqhdr not in self.__jsonheader:
                    raise ValueError(f"Missing required header: '{reqhdr}'.")

    def __process_message(self) -> None:
        content_len = self.__jsonheader["content-length"]
        if not len(self.__recv_buffer) >= content_len:
            return

        data = self.__recv_buffer[:content_len]
        self.__recv_buffer = self.__recv_buffer[content_len:]

        if self.__jsonheader["content-type"] in ("binary/flac", ): # TODO: Add other encodings than flac
            encoding = self.__jsonheader["content-encoding"]
            self.__binary_stream = data
            print("Buffered", len(self.__binary_stream), "bytes of", self.__jsonheader["content-type"], "data")
            self.__append_to_queue_cb((encoding, self.__binary_stream))
        else:
            print(
                f"Received not supported {self.__jsonheader['content-type']} message",
                "from {self.addr} encoded as {self.__jsonheader['content-encoding']}",
                "\nIgnoring message.."
            )
            self.__binary_stream = data

        self.close()

    def __json_decode(self, json_bytes: bytes, encoding: str) -> None:
        tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj

    def __read(self) -> None:
        try:
            data = self.__sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self.__recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

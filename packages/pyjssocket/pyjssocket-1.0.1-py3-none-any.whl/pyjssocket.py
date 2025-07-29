import base64
import hashlib
import logging
import re
import socketserver

from functools import reduce

logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

response_format = '''HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Accept: {}

'''

magic_word = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

class JSBaseRequestHandler(socketserver.BaseRequestHandler):

    def setup(self):
        message = ''

        while True:
            message += self.request.recv(1024).decode('utf-8')

            if message[-4:] == '\r\n\r\n':
                break

        host   = re.search('Host:(.*)', message)
        url    = re.search('GET (.*) HTTP/1.1', message)
        seqKey = re.search('Sec-WebSocket-Key: (.*)', message)

        if not host or not url:
            if not host:
                logger.warning('unknown host value')
            else:
                logger.warning('unknown url value')

            return

        logger.info('received handshake message')

        if not seqKey:
            logger.warning('unknown Sec-WebSocket-Key value')
            return

        self.on_handshake(host.group(1).strip(), url.group(1), seqKey.group(1).strip())

    def handle(self):
        try:
            while True:
                m = self.request.recv(20)

                if m[1] >> 7 != 1:
                    logger.warning('unmasked message detected')
                    self.send_response('All messages must use masking!')
                    continue

                if m[1] & 0x7F < 126:
                    start_byte = 2
                    message_len = m[1] & 0x7F
                elif m[1] & 0x7F == 126:
                    start_byte = 4
                    message_len = reduce(lambda a, b: a + b, map(lambda item: item[1] << (item[0] * 8), enumerate(m[3:1:-1])), 0)
                else:
                    start_byte = 10
                    message_len = reduce(lambda a, b: a + b, map(lambda item: item[1] << (item[0] * 8), enumerate(m[9:1:-1])), 0)

                keys    = m[start_byte:start_byte + 4]
                decoded = bytearray()

                m = m[start_byte + 4:]

                while True:
                    decoded += bytearray(map(lambda item: item[1] ^ keys[item[0] & 0x3], enumerate(m)))

                    if message_len <= len(decoded):
                        break

                    m = self.request.recv(1024)

                self.on_message(decoded)
        except IndexError:
            logger.info('connection aborted')

    def on_handshake(self, host: str, url: str, seqKey: str):
        self.accept_handshake(seqKey)

    def on_message(self, data: bytes):
        pass

    def on_error(self, value: str):
        pass

    def accept_handshake(self, seqKey: str):
        hash = base64.b64encode(hashlib.sha1((seqKey + magic_word).encode('utf-8')).digest())\
            .decode('utf-8')
        self.request.sendall(response_format.format(hash).encode('utf-8'))

    def send_response(self, data: str):
        def prepare_length_bits() -> bytes:
            data_len = len(data)

            if data_len < 126:
                return data_len.to_bytes(1)

            if data_len < 2 ** 16:
                return b'\x7e' + data_len.to_bytes(2)

            return b'\x7f' + data_len.to_bytes(8)

        res = b'\x81' + prepare_length_bits()

        for b in data.encode('utf-8'):
            res += b.to_bytes(1)

        self.request.sendall(res)

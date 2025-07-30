from aia_protocol.pipeline.base_stage import PipelineStage
import struct

class ChecksumStage(PipelineStage):
    def processToSend(self, message: bytes) -> bytes:
        message = message or b""
        checksum = sum(b & 0xFF for b in message)
        return message + struct.pack('>I', checksum)

    def processToReceive(self, message: bytes) -> bytes:
        if not message or len(message) < 4:
            raise ValueError("Invalid or empty message")
        payload, checksum_bytes = message[:-4], message[-4:]
        expected = sum(b & 0xFF for b in payload)
        actual = struct.unpack('>I', checksum_bytes)[0]
        if expected != actual:
            raise ValueError("Checksum verification failed")
        return payload
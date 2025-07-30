from aia_protocol.pipeline.base_stage import PipelineStage
import zlib

class CompressionStage(PipelineStage):
    def processToSend(self, message: bytes) -> bytes:
        return zlib.compress(message or b"")

    def processToReceive(self, message: bytes) -> bytes:
        return zlib.decompress(message or b"")

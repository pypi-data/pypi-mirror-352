class PipelineStage:
    def processToSend(self, message: bytes) -> bytes:
        raise NotImplementedError

    def processToReceive(self, message: bytes) -> bytes:
        raise NotImplementedError
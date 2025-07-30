from aia_protocol.pipeline.base_stage import PipelineStage

class Pipeline:
    def __init__(self):
        self.stages = []
        self.reversed_stages = []

    def addStage(self, stage: PipelineStage):
        self.stages.append(stage)
        self.reversed_stages.insert(0, stage)

    def processToSend(self, message: bytes) -> bytes:
        for stage in self.stages:
            message = stage.processToSend(message)
        return message

    def processToReceive(self, message: bytes) -> bytes:
        for stage in self.reversed_stages:
            message = stage.processToReceive(message)
        return message
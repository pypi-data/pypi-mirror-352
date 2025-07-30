from dataclasses import dataclass

@dataclass
class ProtocolMessage:
    packet_id: int
    payload: bytes
    ack_requested: bool = True
    is_ack: bool = False
    chunk_index: int = 0
    total_chunks: int = 1
    transport: bool = False

    def __repr__(self):
        return f"<ProtocolMessage id={self.packet_id} chunk={self.chunk_index}/{self.total_chunks} ack={self.ack_requested} is_ack={self.is_ack} payload={self.payload[:10]}...>"

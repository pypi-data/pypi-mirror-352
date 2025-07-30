from aia_protocol.core.message import ProtocolMessage
from aia_protocol.core.frame_manager import ProtocolFrameManager

def test_message_roundtrip():
    original = ProtocolMessage(packet_id=42, payload=b'hello world', ack_requested=True, is_ack=False)
    framer = ProtocolFrameManager()
    encoded = framer.encode(original)
    decoded = framer.decode(encoded)
    assert decoded.packet_id == original.packet_id
    assert decoded.payload == original.payload
    assert decoded.ack_requested == original.ack_requested
    assert decoded.is_ack == original.is_ack
    assert decoded.chunk_index == original.chunk_index
    assert decoded.total_chunks == original.total_chunks

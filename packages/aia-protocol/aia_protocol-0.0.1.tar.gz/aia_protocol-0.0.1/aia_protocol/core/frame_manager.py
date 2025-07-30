from aia_protocol.core.message import ProtocolMessage
import struct
import zlib

class ProtocolFrameManager:
    HEADER_FORMAT = '>BBIIIII'  # version, flags, message_id, chunk_index, total_chunks, orig_len, transf_len
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    FLAG_TRANSPORT     = 1 << 0
    FLAG_ACK           = 1 << 1
    FLAG_ACK_REQUESTED = 1 << 2

    def encode(self, message: ProtocolMessage, transform_fn=None) -> bytes:
        version = 1

        flags = 0
        if message.transport:
            flags |= self.FLAG_TRANSPORT
        if message.is_ack:
            flags |= self.FLAG_ACK
        if message.ack_requested:
            flags |= self.FLAG_ACK_REQUESTED

        original_payload = message.payload or b''
        transformed_payload = (transform_fn(original_payload) if transform_fn and not message.is_ack else original_payload) or b''

        buffer = bytearray()
        buffer.extend(struct.pack(
            self.HEADER_FORMAT,
            version,
            flags,
            message.packet_id,
            message.chunk_index,
            message.total_chunks,
            len(original_payload),
            len(transformed_payload)
        ))
        buffer.extend(transformed_payload)

        checksum = zlib.crc32(buffer) & 0xFFFFFFFF
        buffer.extend(struct.pack('>I', checksum))
        return bytes(buffer)

    def decode(self, data: bytes, responder_id="unknown", reverse_transform_fn=None) -> ProtocolMessage:
        if len(data) < self.HEADER_SIZE + 4:
            raise ValueError("Frame too short")

        checksum_expected = struct.unpack('>I', data[-4:])[0]
        checksum_actual = zlib.crc32(data[:-4]) & 0xFFFFFFFF
        if checksum_expected != checksum_actual:
            raise ValueError("Checksum mismatch")

        header = struct.unpack(self.HEADER_FORMAT, data[:self.HEADER_SIZE])
        version, flags, msg_id, chunk_index, total_chunks, orig_len, transf_len = header

        transformed_payload = data[self.HEADER_SIZE:-4]
        if len(transformed_payload) != transf_len:
            raise ValueError("Payload length mismatch")

        is_ack = bool(flags & self.FLAG_ACK)
        ack_requested = bool(flags & self.FLAG_ACK_REQUESTED)
        transport = bool(flags & self.FLAG_TRANSPORT)

        payload = reverse_transform_fn(transformed_payload) if reverse_transform_fn and not is_ack else transformed_payload
        return ProtocolMessage(
            packet_id=msg_id,
            payload=payload,
            ack_requested=ack_requested,
            is_ack=is_ack,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            transport=transport
        )
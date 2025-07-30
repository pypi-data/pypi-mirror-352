from aia_protocol.core.frame_manager import ProtocolFrameManager
from aia_protocol.core.message import ProtocolMessage
from aia_protocol.transport.udp_transport import UdpTransport
from aia_protocol.pipeline.pipeline import Pipeline
import threading
import time
import socket
import queue

class ProtocolEngine:
    def __init__(self, transport: UdpTransport, pipeline: Pipeline = None):
        self.transport = transport
        self.pipeline = pipeline
        self.frame_manager = ProtocolFrameManager()
        self.send_queue = queue.Queue()
        self.ack_wait_locks = {}
        self.packet_id_counter = 1
        self.running = False
        self.receive_callback = None
        self.ack_callback = None
        self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.receiver_thread = threading.Thread(target=self._receiver_loop, daemon=True)

    def start(self, on_receive, on_ack):
        self.receive_callback = on_receive
        self.ack_callback = on_ack
        self.running = True
        self.sender_thread.start()
        self.receiver_thread.start()

    def stop(self):
        self.running = False

    def send_message(self, destination: tuple, payload: bytes, ack_requested=True) -> int:
        packet_id = self.packet_id_counter
        self.packet_id_counter += 1

        message = ProtocolMessage(
            packet_id=packet_id,
            payload=payload,
            ack_requested=ack_requested
        )
        frame = self.frame_manager.encode(message, transform_fn=self.pipeline.processToSend if self.pipeline else None)
        self.ack_wait_locks[packet_id] = time.time()
        self.send_queue.put((destination, packet_id, frame))
        return packet_id

    def _sender_loop(self):
        while self.running:
            try:
                destination, packet_id, frame = self.send_queue.get(timeout=1)
                self.transport.send(destination, frame)
                time.sleep(0.01)
            except queue.Empty:
                continue

    def _receiver_loop(self):
        while self.running:
            data, addr = self.transport.receive()
            if not data:
                time.sleep(0.01)
                continue
            try:
                message = self.frame_manager.decode(data, reverse_transform_fn=self.pipeline.processToReceive if self.pipeline else None)
                if message.is_ack:
                    if message.packet_id in self.ack_wait_locks:
                        del self.ack_wait_locks[message.packet_id]
                        if self.ack_callback:
                            self.ack_callback(message.packet_id)
                else:
                    if message.ack_requested:
                        ack = ProtocolMessage(packet_id=message.packet_id, payload=b"", is_ack=True)
                        ack_frame = self.frame_manager.encode(ack)
                        self.transport.send(addr, ack_frame)
                    if self.receive_callback:
                        self.receive_callback(message, addr)
            except Exception as e:
                print("Receive/decode failed:", e)
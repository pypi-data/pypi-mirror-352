
from .exceptions import PeerDisconnectedException


def send(args, tcp_sock, payload_bytes):
    num_payload_bytes = len(payload_bytes)

    num_bytes_sent = tcp_sock.send(payload_bytes)

    if num_bytes_sent != num_payload_bytes:
        raise Exception("ERROR: tcp_helper.send(): send failed: wrong number of bytes sent: expected {}, actual {}".format(
            num_payload_bytes,
            num_bytes_sent
        ))

    if args and args.verbosity > 2:
        print("tcp send: {}".format(payload_bytes.decode()), flush=True)


def send_string(args, tcp_sock, str0):
    send(args, tcp_sock, str0.encode())


def recv(args, tcp_sock, num_bytes_to_read):

    # blocking
    recv_bytes = tcp_sock.recv(num_bytes_to_read)

    if len(recv_bytes) == 0:
        raise PeerDisconnectedException()

    if args and args.verbosity > 2:
        print("tcp_helper.recv(): {}".format(recv_bytes.decode()), flush=True)

    return recv_bytes


def recv_exact_num_bytes(tcp_sock, total_num_bytes_to_read):
    payload_bytes = bytearray()
    num_bytes_read = 0

    while num_bytes_read < total_num_bytes_to_read:

        num_bytes_remaining = total_num_bytes_to_read - num_bytes_read

        # blocking
        recv_bytes = tcp_sock.recv(num_bytes_remaining)

        num_bytes_received = len(recv_bytes)

        if num_bytes_received == 0:
            raise PeerDisconnectedException()

        num_bytes_read += num_bytes_received

        payload_bytes.extend(recv_bytes)

    return payload_bytes


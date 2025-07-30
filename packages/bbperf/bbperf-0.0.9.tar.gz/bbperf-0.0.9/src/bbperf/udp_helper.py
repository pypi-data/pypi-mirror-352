

def send(args, udp_sock, payload_bytes):
    num_payload_bytes = len(payload_bytes)

    num_bytes_sent = udp_sock.send(payload_bytes)

    if num_bytes_sent <= 0 or num_bytes_sent != num_payload_bytes:
        raise Exception("ERROR: udp_helper.sendto(): send failed")

    if args.verbosity > 2:
        print("udp_helper.send(): data sent: {}".format(
            payload_bytes.decode()), flush=True)


def send_string(args, udp_sock, str0):
    send(args, udp_sock, str0.encode())


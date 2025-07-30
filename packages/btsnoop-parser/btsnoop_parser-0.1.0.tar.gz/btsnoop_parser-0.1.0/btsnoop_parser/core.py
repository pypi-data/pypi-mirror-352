import struct
import datetime
from .constants import HCI_PACKET_TYPES

BTSNOOP_HEADER = b'btsnoop\0'
BTSNOOP_TIMESTAMP_OFFSET = 0x00E03AB44A676000


def parse_btsnoop_file(filename):
    records = []
    with open(filename, 'rb') as f:
        if f.read(8) != BTSNOOP_HEADER:
            raise ValueError("Invalid BTSnoop file header")
        _ = struct.unpack('>II', f.read(8))  # version, datalink
        f.read(8)  # reserved

        while True:
            header = f.read(24)
            if len(header) < 24:
                break
            orig_len, incl_len, flags, drops, timestamp = struct.unpack('>IIIIQ', header)
            packet = f.read(incl_len)
            if not packet:
                break

            ts = datetime.datetime(1, 1, 1) + datetime.timedelta(
                microseconds=timestamp - BTSNOOP_TIMESTAMP_OFFSET
            )

            record = {
                'timestamp': ts,
                'flags': flags,
                'direction': 'RX' if flags == 1 else 'TX',
                'packet_type': HCI_PACKET_TYPES.get(packet[0], 'UNKNOWN'),
                'packet_data': packet[1:],
                'raw': packet
            }
            records.append(record)

    return records
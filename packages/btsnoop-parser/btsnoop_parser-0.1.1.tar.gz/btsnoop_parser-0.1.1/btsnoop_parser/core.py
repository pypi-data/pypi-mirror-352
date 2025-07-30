import struct
import datetime

BTSNOOP_HEADER = b'btsnoop\0'
BTSNOOP_TIMESTAMP_OFFSET = 0x00E03AB44A676000

def parse_btsnoop_file(filename):
    records = []

    with open(filename, 'rb') as f:
        # Step 1: Check file header
        header = f.read(8)
        if header != BTSNOOP_HEADER:
            raise ValueError("Invalid BTSnoop file header")

        version, datalink = struct.unpack('>II', f.read(8))
        f.read(8)  # skip reserved
        print(f"[INFO] File header OK. Version={version}, Datalink={datalink}")

        while True:
            record_header = f.read(24)
            if len(record_header) < 24:
                print("[INFO] End of file or incomplete record header")
                break

            try:
                orig_len, incl_len, flags, drops, timestamp = struct.unpack('>IIIIQ', record_header)
            except struct.error as e:
                print(f"[ERROR] Failed to unpack record header: {e}")
                break

            packet = f.read(incl_len)
            if len(packet) < incl_len:
                print(f"[WARN] Incomplete packet read (expected {incl_len}, got {len(packet)}), skipping")
                break

            if incl_len == 0:
                print("[INFO] Skipping 0-length packet")
                continue

            try:
                ts = datetime.datetime(1, 1, 1) + datetime.timedelta(
                    microseconds=timestamp - BTSNOOP_TIMESTAMP_OFFSET
                )
            except Exception as e:
                print(f"[ERROR] Invalid timestamp: {timestamp} -> {e}")
                continue

            packet_type = packet[0] if len(packet) > 0 else None
            record = {
                'timestamp': ts,
                'flags': flags,
                'direction': 'RX' if flags == 1 else 'TX',
                'packet_type': packet_type,
                'packet_data': packet[1:] if len(packet) > 1 else b'',
                'raw': packet
            }

            print(f"[RECORD] {ts} {record['direction']} packet_type=0x{packet_type:02X}")
            records.append(record)

    print(f"[SUMMARY] Total parsed records: {len(records)}")
    return records

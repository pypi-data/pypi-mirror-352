from .constants import HCI_OPCODE_NAMES

def decode_hci_packet(packet_type, data):
    if packet_type == 'COMMAND':
        opcode = int.from_bytes(data[0:2], 'little')
        plen = data[2]
        params = data[3:3+plen]
        return {
            'type': 'COMMAND',
            'opcode': opcode,
            'name': HCI_OPCODE_NAMES.get(opcode, 'Unknown'),
            'params': params.hex()
        }
    elif packet_type == 'EVENT':
        event_code = data[0]
        plen = data[1]
        params = data[2:2+plen]
        return {
            'type': 'EVENT',
            'event_code': event_code,
            'params': params.hex()
        }
    else:
        return {
            'type': packet_type,
            'raw': data.hex()
        }
import argparse
from .core import parse_btsnoop_file
from .hci_decoder import decode_hci_packet

def main():
    parser = argparse.ArgumentParser(description="Parse Android btsnoop_hci.log files")
    parser.add_argument("file", help="Path to btsnoop_hci.log")
    parser.add_argument("--limit", type=int, default=10, help="Limit output")
    args = parser.parse_args()

    records = parse_btsnoop_file(args.file)
    for r in records[:args.limit]:
        decoded = decode_hci_packet(r['packet_type'], r['packet_data'])
        print(f"[{r['timestamp']}] {r['direction']} {r['packet_type']} - {decoded}")

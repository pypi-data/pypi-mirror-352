import os
import qrcode
import socket
import netifaces

def is_safe_path(base, path):
    safe_path = os.path.abspath(os.path.join(base, path))
    return base == os.path.commonpath((base, safe_path))


def display_qr_code_in_terminal(text):
    """
    Generates a QR code for the given text and prints it to the terminal.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=2,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)

    qr_matrix = qr.get_matrix()

    # Print the QR code to the terminal
    for row in qr_matrix:
        line = ''.join(['\u2588\u2588' if cell else '  ' for cell in row])  # Use block characters
        print(line)

if __name__ == "__main__":
    text = input("Enter the text to encode in the QR code: ")
    display_qr_code_in_terminal(text)


def get_public_ip():
    """
    Attempts to determine the public IP address of the machine.
    """
    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for addr in addresses[netifaces.AF_INET]:
                    ip = addr['addr']
                    # Exclude loopback and private IP ranges
                    if not ip.startswith('127.'):
                        # and not ip.startswith('192.168.') and not ip.startswith('10.') and not ip.startswith('172.16.'):
                        return ip
    except Exception as e:
        print(f"Error getting public IP: {e}")
    return None
import socket
import ssl

HOSTS = {
    "generativelanguage.googleapis.com": "45.88.174.254",
    "daily-cloudcode-pa.googleapis.com": "45.88.174.254",
    "antigravity-unleash.goog": "45.88.174.254"
}

def test_host(host, ip):
    print(f"Testing {host} via {ip}...")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((ip, 443), timeout=3.0) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                req = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
                ssock.sendall(req.encode("ascii"))
                resp = ssock.recv(1024).decode("utf-8", errors="ignore")
                status_line = resp.split("\r\n")[0] if resp else "Empty"
                print(f"  [+] Status: {status_line}")
                if "400" in status_line and "User location is not supported" in resp:
                    print("  [-] GEOBLOCKED (returned Russian edge error)")
                else:
                    print("  [+] PASS (reached Google Front End without location block)")
    except Exception as e:
        print(f"  [-] Error: {e}")

if __name__ == "__main__":
    for h, ip in HOSTS.items():
        test_host(h, ip)

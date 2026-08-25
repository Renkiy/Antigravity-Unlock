import socket
import ssl
import time

PROXIES = [
    "87.228.47.194",
    "87.228.47.202",
    "45.155.204.190",
    "37.230.192.51",
    "45.88.174.254",
    "95.182.120.241"
]

SNI_HOSTS = [
    "generativelanguage.googleapis.com",
    "daily-cloudcode-pa.googleapis.com",
    "antigravity-unleash.goog"
]

def probe_proxy(ip):
    print(f"\n--- Probing Proxy IP: {ip} ---")
    for sni in SNI_HOSTS:
        t0 = time.time()
        try:
            ctx = ssl.create_default_context()
            sock = socket.create_connection((ip, 443), timeout=3.0)
            ssock = ctx.wrap_socket(sock, server_hostname=sni)
            cert = ssock.getpeercert()
            issuer = dict(x[0] for x in cert.get('issuer', [])).get('commonName', 'Unknown')
            latency = (time.time() - t0) * 1000
            print(f"  [+] {sni:35} -> OK ({latency:.0f} ms, Issuer: {issuer})")
            ssock.close()
        except Exception as e:
            latency = (time.time() - t0) * 1000
            print(f"  [-] {sni:35} -> FAIL ({latency:.0f} ms): {e}")

if __name__ == "__main__":
    for p in PROXIES:
        probe_proxy(p)

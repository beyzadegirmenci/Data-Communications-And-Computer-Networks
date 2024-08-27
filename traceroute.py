import os
import sys
import socket
import struct
import time

def traceroute_func(hedef_url):
    hedef_port = 33434
    max_atlama = 64
    bekleme_suresi = 5.0
    ttl = 1

    hedef_ip = socket.gethostbyname(hedef_url)
    print(f"Tracing route to {hedef_url} ...")

    for ttl in range (1, max_atlama + 1 ):
        alici_soket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        gonderici_soket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        alici_soket.settimeout(bekleme_suresi)
        alici_soket.bind(("", hedef_port))
        gonderici_soket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        gonderici_soket.sendto(b"", (hedef_url, hedef_port))

        adres = None
        try:
            _, adres = alici_soket.recvfrom(512)
            adres = adres[0]
        except socket.error:
            pass
        finally:
            gonderici_soket.close()
            alici_soket.close()

        if adres is not None:
            if adres.startswith(hedef_ip):
                print(f"{ttl}\t{adres}\tReached")
                break
            else:
                print(f"{ttl}\t{adres}")
        else:
            print(f"{ttl}\t*\tRequest timed out.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <hedef_url>")
        sys.exit(1)

    traceroute_func(sys.argv[1])
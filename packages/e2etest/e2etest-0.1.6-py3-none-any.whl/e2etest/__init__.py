import subprocess
subprocess.run(["pip", "install", "-r", "requirements.txt"])

from .e2e import E2E

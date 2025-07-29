import subprocess
subprocess.run(["pip", "install", "-q", "requests_html"])
subprocess.run(["pip", "install", "-q", "lxml_html_clean"])

from .e2e import E2E

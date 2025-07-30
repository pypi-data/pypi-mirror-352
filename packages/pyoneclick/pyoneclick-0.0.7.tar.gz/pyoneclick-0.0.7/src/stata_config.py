import os
import stata_setup
stata_path = os.environ.get("STATA_PATH")
if not stata_path:
    raise KeyError("Environment variable STATA_PATH not found.")
stata_root = os.path.dirname(stata_path)
stata_executable = os.path.basename(stata_path)
version_info = stata_executable[5:7].lower()
stata_setup.config(stata_root, version_info, splash=False)
from pystata import stata

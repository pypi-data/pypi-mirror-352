import os
import platform
import subprocess
import sys

module_path = os.path.abspath(os.path.dirname(__file__))

os.environ['MINDOPT_HOME'] = module_path

if platform.system() == "Windows":
    sys.path.append(os.path.join(module_path, 'win64-x86', 'lib'))
elif platform.system() == "Darwin":
    if subprocess.check_output(['sysctl', '-in', 'sysctl.proc_translated'], universal_newlines=True).strip() == "1":
        raise ImportError("MindOpt won't run in Rosetta environment. (Got virtual x86_64, actually arm64)")

from .mindoptpy import *


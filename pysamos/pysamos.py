import os
import subprocess


        
def run(cfgfile: str, silent: bool = False, debug: bool = False):
    """ Run a SAMoS simulation from config file. 

    We require the 'samos' and 'samos_debug' executable to be present in env.
    """

    out = subprocess.PIPE if silent else None

    # Run.
    samosbin = 'samos_debug' if debug else 'samos'
    res = subprocess.run(f'{samosbin} {cfgfile}', shell=True, stdout=out, stderr=out)
    return res


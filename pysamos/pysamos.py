import subprocess
import shutil


        
def run(cfgfile: str, silent: bool = False, debug: bool = False):
    """ Run a SAMoS simulation from config file. 

    We require the 'samos' and 'samos_debug' executable to be present in env.
    """

    # Make sure SAMoS installed.
    samosbin = shutil.which('samos')
    if samosbin is None:
        raise Exception('No SAMoS binary found.')
    else:
        out = subprocess.PIPE if silent else None
        # Run.
        res = subprocess.run(f'{samosbin} {cfgfile}', shell=True, stdout=out, stderr=out)
        return res


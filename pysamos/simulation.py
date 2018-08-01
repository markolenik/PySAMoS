import os
import glob
import scipy as sp

from . import helpers
from . import tissue
from . import config
from . import generator
from . import pysamos


class Simulation():

    def __init__(self, config: config.Config, tissue: tissue.Tissue):
        self.config = config
        self.tissue = tissue

    # Convenience properties.

    @property
    def config_file(self):
        return self.config.config[-1] + '.conf'

    @property
    def tissue_file(self):
        return self.config.input[-1]

    @property
    def bound_file(self):
        return self.config.bounds[-1]


def setup(sim: Simulation, directory: str = '.', silent: bool = False):
    """ Setup simulation for a run by writing the necessary files. """
    # Write files.
    if not silent:
        print(("Write config file into "
                f"\"{os.path.join(directory, sim.config_file)}\"."))
        print(("Write tissue file into "
                f"\"{os.path.join(directory, sim.tissue_file)}\"."))
        print(("Write bound file into "
                f"\"{os.path.join(directory, sim.bound_file)}\"."))

    with helpers.cd(directory):
        generator.write(sim.config, sim.config_file)
        tissue.write(sim.tissue, sim.tissue_file)
        tissue.write_bound_connectivity(sim.tissue, sim.bound_file)


def run(sim: Simulation, directory: str = '.', silent: bool = False, **kw) -> None:
    """ Run simulation with tissue. """

    # Prepare run.
    if not os.path.isdir(directory):
        if not silent:
            print((f"Creating write directory \"{directory}\"."))
        os.makedirs(directory)

    with helpers.cd(directory):
        setup(sim, silent=silent)
        # Run.
        return pysamos.run(sim.config_file, silent, **kw)


def clear(directory: str):
    """ Clear simulation result files from directory. """
    with helpers.cd(directory):
        dats = glob.glob('*.dat')
        vtps = glob.glob('*.vtp')
        fcs = glob.glob('*.fc')
        for f in dats + vtps + fcs:
            os.remove(f)
    

def result(directory: str) -> str:
    """ Return result data file of last simulation step. """
    dats = glob.glob(os.path.join(directory, '*[0-9].dat'))
    steps = [int(dat.split('_')[-1].split('.')[0]) for dat in dats]
    last_dat = dats[sp.argmax(steps)]
    return last_dat
        

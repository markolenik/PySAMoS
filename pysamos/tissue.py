import itertools
import os
import subprocess
import contextlib
from typing import Tuple, Union, NewType, List, Sequence, NamedTuple, Callable

import scipy as sp
import scipy.spatial
import scipy.interpolate
import pandas as pd
from pandas import DataFrame

from . import generator
from . import parser
from . import helpers
from . import pysamos
from . import config


class Particle(NamedTuple):
    """ A particle type with default values. """
    type: int = 1                # Particle type.
    boundary: int = 0            # Boundary particle yes/no?
    x: float = 0.                # Coordinates.
    y: float = 0.
    vx: float = 0.               # Velocity.
    vy: float = 0.
    nx: float = 1.               # Director.
    ny: float = 0.
    nvz: float = 1.              # Normal nonzero component.
    area: float = round(sp.pi, 3) # Preferred area.


# TODO center lesion    
# TODO rows
class Tissue(DataFrame):
    """ A tissue is represented as a table, each row corresponds to a particle. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return Tissue

    # Convenience properties.

    @property
    def points(self):
        return self[['x', 'y']].as_matrix()

    @property
    def is_cell(self):
        return self.boundary == 0

    @property
    def is_bound(self):
        return self.boundary == 1
    
    @property
    def cells(self):
        return self[self.is_cell]

    @property
    def bounds(self):
        return self[self.is_bound]

    @property
    def types(self):
        return self.type.unique()

    @property
    def num_types(self):
        return len(self.types)

    @property
    def num_cells(self):
        return len(self.cells)

    @property
    def num_bounds(self):
        return len(self.bounds)
    

def new_tissue(cell_points: sp.ndarray,
               bound_points: sp.ndarray = None,
               nbounds: int = None,
               bound_thresh: float = None,
               **kwargs) -> Tissue:
    """ Create new tissue from cell and bound coordinates.
    
    In case no bound points provided, use convex hull of cell of cell points.
    For numerical stability of the simulation, cell points lying to close to
    the boundary will be removed.
    We assume that bound points form a convex curve. 
    
    """
    if nbounds is None:
        nbounds = len(cell_points)/10 # Default value.

    # Create bounds.
    if bound_points is None:
        # Use convex hull to find boundary points.
        hull = sp.spatial.ConvexHull(cell_points)
        bound_points = helpers.hull_points(hull, nbounds)

    # Remove all cell points that lie too close to border.
    if bound_thresh is not None:
        dist = sp.spatial.distance.cdist(bound_points, cell_points) 
        bidx, cidx = sp.nonzero(dist < bound_thresh)
        new_cell_points = sp.delete(cell_points, cidx, axis=0)
    else:
        new_cell_points = cell_points.copy()

    # Assign type for cells first.
    cell_type = Particle._field_defaults['type']
    bound_type = cell_type + 1
    cells = [
        Particle(x=cp[0], y=cp[1], type=cell_type, boundary=0, **kwargs)
        for cp in new_cell_points
    ]
    bounds = [
        Particle(x=bp[0], y=bp[1], type=bound_type, boundary=1, **kwargs)
        for bp in bound_points
    ]

    return add_shapeinfo(organise(Tissue(cells + bounds)))


def organise(tissue: Tissue) -> Tissue:
    """ Assign correct tissue types to particles and reindex.

    We set the convention to first assign cell types in increasing order,
    starting at 1, and only then assign bound types.

    """
    def update_particle_types(particles: Tissue, startidx: int) -> Tissue:
        """ Assign the correct type for cell or bound particles. """
        types = sp.array(range(particles.num_types)) + startidx # Correct types.
        if not sp.array_equal(particles.types, types):
            ntypes = particles.type.map(
                    lambda ptype:
                    types[sp.where(particles.types == ptype)[0][0]]
            )
            return particles.assign(type=ntypes)
        else:
            return particles
    IDX0 = 1
    cells = update_particle_types(tissue.cells, IDX0)
    bounds = update_particle_types(tissue.bounds, cells.num_types + 1)

    return pd.concat((cells, bounds)).reset_index(drop=True)


def read(fname: str) -> Tissue:
    """ Read tissue from SAMoS generated output."""
    dat = sp.genfromtxt(fname, skip_header=1)
    with open(fname, 'r') as f:
        line1 = f.readline()
    header = line1.split()[1:]    
    # NOTE I'm not trying to fit the data to my cell namedtuple.
    # The stuff that's being saved is different from the stuff that
    # is read at the start. No idea why...
    df = pd.DataFrame(dat, columns=header)
    df['nvx'] = sp.zeros(len(df)) 
    df['nvy'] = sp.zeros(len(df)) 
    df['nvz'] = sp.ones(len(df)) 
    # cast proper types
    for col in ['id', 'type', 'boundary']:
        df[col] = df[col].astype(int)
    return add_shapeinfo(organise(Tissue(df[list(Particle._field_defaults)])))


def write(tissue: Tissue, fname: str) -> None:
    # Add columns.
    _tissue = organise(tissue)
    # Write.
    _tissue.to_csv(fname, sep='\t', float_format='%10.5f',
                   index=True, index_label='keys: id',
                   columns=Particle._fields)



def bound_connectivity(tissue: Tissue) -> list:
    """ Compute connectivities of all types of boundary particles."""
    bound_cons = [
        _connect_bounds(tissue.bounds[tissue.bounds.type == btype])
        for btype in tissue.bounds.types
    ]
    return sp.concatenate(bound_cons)


def _connect_bounds(bounds: Tissue) -> sp.ndarray:
        """ Compute connectivity of some boundary particles."""
        con = helpers.connect_points(bounds.points)  # Connectivity.
        # Get bound connectivity based on actual particle index.
        idx_con = bounds.index[con].values
        return sp.c_[range(len(idx_con)), idx_con]


def _write_bound_connectivity(con: sp.ndarray, fname: str) -> None:
    """ Write bound connectivity to file. """
    # Append connection index column for SAMoS.
    sp.savetxt(fname, con, delimiter=' ', fmt='%d')


def write_bound_connectivity(tissue: Tissue, fname: str) -> None:
    bcon = bound_connectivity(tissue) 
    _write_bound_connectivity(bcon, fname)


def add_shapeinfo(tissue: Tissue) -> Tissue:
    """ Add columns with cell shape info, such as vertices of dual, area, perimeter etc. """
    vs = helpers.vor_vertices(tissue.points)
    A = [helpers.poly_area(poly) for poly in vs]         # Area.
    P = [helpers.poly_perimeter(poly) for poly in vs]    # Perimeter.
    p0 = [P0/sp.sqrt(A0) for A0, P0 in zip(A, P)]        # Shape factor (Bi2016).
    rho = [helpers.poly_shape_factor(poly) for poly in vs] # Shape factor from tensor.
    return tissue.assign(vs=vs, A=A, P=P, p0=p0, rho=rho)

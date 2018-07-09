# Various useful but unrelated helper functions.

import contextlib
import os

import scipy as sp
import scipy.spatial
import shapely.geometry


@contextlib.contextmanager
def cd(newdir: str) -> None:
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def hull_points(hull: sp.spatial.qhull.ConvexHull, N: int) -> sp.ndarray:
    """ Evenly sample points from convex hull of set. """
    # Compute convex hull of set.
    points = hull.points

    # Perform linear spline interpolation of hull.
    xs, ys = points[hull.vertices, 0], points[hull.vertices, 1]
    xxs, yys = sp.r_[xs, xs[0]], sp.r_[ys, ys[0]]
    tck, _ = sp.interpolate.splprep((xxs, yys), s=0, k=1, per=True)
    # Evaluate interpolation at 1000 points.
    _xs, _ys = sp.interpolate.splev(sp.linspace(0, 1, 1000), tck)
    # Pick N points.
    xnth = int(len(_xs)/N)
    ynth = int(len(_ys)/N)

    return sp.c_[_xs[::xnth], _ys[::ynth]]


def connect_points(points: sp.ndarray) -> sp.ndarray:
    """ Compute connectivity of points using triangulation points. 

    Points must form a single convex curve.

    """
    tri = sp.spatial.Delaunay(points)
    dist = sp.spatial.distance.cdist(points, points)

    indices, indptr = tri.vertex_neighbor_vertices

    def closest_pair(idx):
        """ Pair of closest vertices. """
        nn = indptr[indices[idx]:indices[idx+1]]
        return tuple(nn[sp.argsort(dist[idx, nn])][:2])

    # Initial connectivity pair.
    con = [(0, closest_pair(0)[0])]
    while len(con) < len(points):
        pair = con[-1]
        newpair = closest_pair(pair[1])
        newnext = newpair[(newpair.index(pair[0])+1)%2]
        con = con + [(pair[1], newnext)]

    return sp.array(con)



def vor_vertices(tri_points: sp.ndarray) -> sp.ndarray:
    """ Compute vertices of Voronoi diagram for given triangulation. """
    vor = sp.spatial.Voronoi(tri_points)
    vs = [
        vor.vertices[vor.regions[vor.point_region[idx]]]
        for idx in range(len(tri_points))
    ]
    return vs


def poly_area(vs: sp.ndarray) -> sp.ndarray:
    """ Compute polygon area. """
    return shapely.geometry.Polygon(vs).area


def poly_perimeter(vs: sp.ndarray) -> sp.ndarray:
    """ Compute polygon perimeter. """
    return shapely.geometry.Polygon(vs).length

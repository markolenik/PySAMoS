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


def poly_shape_tensor(vs: sp.ndarray) -> sp.ndarray:
    """ Shape tensor of polygon. """
    try:
        rc = sp.mean(vs, axis=0)    # Center of mass.
        tensor = 0
        for v in vs:
            rbar = v-rc
            tensor += sp.array([[rbar[0]**2, -rbar[0]*rbar[1]],
                                [-rbar[0]*rbar[1], rbar[1]**2]])
        return tensor
    except:
        return None


def poly_shape_factor(vs: sp.ndarray) -> float:
    """ Shape factor from shape tensor. """
    tensor = poly_shape_tensor(vs)
    _w, _ = sp.linalg.eig(tensor)
    w = sp.real(_w)
    return abs((w[0]-w[1])/(w[0]+w[1]))


def circle_points(N, R, R_sigma=0, theta_sigma=0):
    """ Generate points on circle using Vogels method (sunflower seeds)."""
    radius = sp.sqrt(sp.arange(N)*pow(R, 2) / float(N))
    radius = radius + sp.randn(len(radius))*R_sigma

    golden_angle = sp.pi * (3 - sp.sqrt(5))
    theta = golden_angle * sp.arange(N)
    theta = theta + sp.randn(len(theta))*theta_sigma

    points = sp.zeros((N, 2))
    points[:,0] = sp.cos(theta)
    points[:,1] = sp.sin(theta)
    points *= radius.reshape((N, 1))
    return points


def circle_boundpoints(N, R):
    """ Return uniform circular boundary."""
    phis = sp.linspace(0, 2*sp.pi, N)[:-1] # Don't close the circle!
    z = R*sp.exp(1j*phis)
    return sp.vstack((sp.real(z), sp.imag(z))).T

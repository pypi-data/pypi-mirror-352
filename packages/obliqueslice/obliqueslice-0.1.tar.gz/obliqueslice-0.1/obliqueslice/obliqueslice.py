import numpy as np
import scipy.ndimage
def obliqueslice(V, point, normal, method='linear', threshold = 1e-6, fill_value=0, interp_order=None):
    """
    Extract an oblique slice from 3D image.

      - V is a 3D numpy array with shape (rows, cols, depths) indexed as (y, x, z).
      - World coordinates are defined as (x, y, z).

    """
    
    point = np.asarray(point).flatten()
    normal = np.asarray(normal).flatten()
    normal /= np.linalg.norm(normal)

    # create two orthonormal vectors for the plane.
    ref_vector = np.array([1, 0, 0]) if abs(normal[0]) < 0.9 else np.array([0, 1, 0])
    v1 = np.cross(normal, ref_vector)
    v1 /= np.linalg.norm(v1)
    v2 = np.cross(normal, v1)

    # projection: convert a world point to (u,v) coordinates on the plane.
    def project_to_slice(p):
        return np.array([np.dot(p - point, v1), np.dot(p - point, v2)])

    # volume dimensions (V is (y,x,z))
    dims = np.array(V.shape)
    y_max, x_max, z_max = dims[0]-1, dims[1]-1, dims[2]-1

    # define volume corners in world coordinates (x,y,z)
    volume_corners = np.array([
        [0,    0,    0],
        [x_max,0,    0],
        [0,    y_max,0],
        [0,    0,    z_max],
        [x_max,y_max,0],
        [x_max,0,    z_max],
        [0,    y_max,z_max],
        [x_max,y_max,z_max]
    ])

    # project corners to (u,v)
    corners_uv = np.array([project_to_slice(c) for c in volume_corners])

    # instead of using the min/max of the corners, we recenter the grid:
    # let (0,0) be the projection of `point`.
    # determine a symmetric extent that covers the projected corners.
    max_extent = np.max(np.abs(corners_uv), axis=0)

    grid_size = max_extent * 2  # full width and height

    # u and v values centered at 0.
    u_vals = np.arange(-grid_size[0] / 2, grid_size[0] / 2 + 1.0, 1.0)
    v_vals = np.arange(-grid_size[1] / 2, grid_size[1] / 2 + 1.0, 1.0)
    slice_u, slice_v = np.meshgrid(u_vals, v_vals)

    # 3D coordinates for every (u,v) in the slice
    coords_3D = point[:, None, None] + slice_u * v1[:, None, None] + slice_v * v2[:, None, None]
    x = coords_3D[0]
    y = coords_3D[1]
    z = coords_3D[2]

    valid_mask = (x >= 0) & (x <= x_max) & (y >= 0) & (y <= y_max) & (z >= 0) & (z <= z_max)

    x_clamped = np.clip(x, 0, x_max)
    y_clamped = np.clip(y, 0, y_max)
    z_clamped = np.clip(z, 0, z_max)


    # note: V is indexed as (y,x,z)
    coords_flat = np.vstack([y_clamped.ravel(), x_clamped.ravel(), z_clamped.ravel()])

    order = interp_order if interp_order is not None else (1 if method == 'linear' else 0)
    slice_img = scipy.ndimage.map_coordinates(V, coords_flat, order=order,
                                              mode='constant', cval=fill_value)
    slice_img = slice_img.reshape(slice_u.shape)
    slice_img[~valid_mask] = 0.0

    return slice_img, slice_u, slice_v, coords_3D

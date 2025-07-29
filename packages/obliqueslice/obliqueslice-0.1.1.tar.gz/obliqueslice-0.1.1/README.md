# obliqueslice

A Python package for slicing 3D numpy arrays along an oblique plane. Equivalent to obliqueslice in MATLAB.

## Installation

```bash
pip install obliqueslice
```

## Usage

```python
import numpy as np
from obliqueslice import obliqueslice

# Create a 3D volume
volume = np.random.rand(100, 100, 100)

# Define a point and normal vector for the slice
point = [50, 50, 50]  # Point on the plane (x, y, z)
normal = [1, 1, 1]    # Normal vector to the plane

# Extract the oblique slice
slice_img, slice_u, slice_v, coords_3D = obliqueslice(volume, point, normal)
```

## Parameters

- `V`: 3D numpy array with shape (rows, cols, depths) indexed as (y, x, z)
- `point`: Point on the plane in world coordinates (x, y, z)
- `normal`: Normal vector to the plane
- `method`: Interpolation method ('linear' or 'nearest', default: 'linear')
- `threshold`: Threshold for cropping out the 'black' parts of the plane
- `fill_value`: Value to use for points outside the volume (default: 0)
- `interp_order`: Interpolation order (default: None, auto-determined from method)

## Returns

- `slice_img`: The extracted 2D slice
- `slice_u`: U coordinates of the slice grid
- `slice_v`: V coordinates of the slice grid  
- `coords_3D`: 3D coordinates for every point in the slice

## Requirements

- numpy
- scipy

## License

MIT License

## Author

Juna Santos (junapsantos@tecnico.ulisboa.pt)
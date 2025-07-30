def calibrate(rotation_axis: float, pixel_size: float):
    import numpy as np

    # Additional data to compute camera length
    physical_pixel_size = 0.0550
    wavelength = 0.0251  # 200kV

    detector_distance = 1 / wavelength * (physical_pixel_size / pixel_size)
    print(f"DETECTOR_DISTANCE={detector_distance:.4f}")
    rot_x = np.cos(np.radians(rotation_axis))
    rot_y = -np.sin(np.radians(rotation_axis))
    print(f"ROTATION_AXIS={rot_x:.6f} {rot_y:.6f} 0.0")

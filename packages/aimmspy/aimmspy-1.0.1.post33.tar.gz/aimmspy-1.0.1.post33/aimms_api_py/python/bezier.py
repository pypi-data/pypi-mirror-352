import numpy as np

def bezier_curve(start, end, curve_point=0.5, num_points=100):
    """
    Calculate Bezier curve points given starting and ending coordinates.
    
    :param start: Tuple of (x, y) for the starting coordinate.
    :param end: Tuple of (x, y) for the ending coordinate.
    :param curve_point: Factor to control the curve direction.
    :param num_points: Number of points to generate along the curve.
    :return: List of (x, y) tuples representing the curve.
    """
    # Control points
    control_points = np.array([
        start, 
        [(start[0] + end[0]) / 2, start[1] + (end[1] - start[1]) * curve_point + 1],  # Adjust this point to control the curve direction
        end
    ])
    
    # Generate t values
    t_values = np.linspace(0, 1, num_points)
    
    # Calculate Bezier curve points
    curve_points = []
    for t in t_values:
        point = (1-t)**2 * control_points[0] + 2*(1-t) * t * control_points[1] + t**2 * control_points[2]
        curve_points.append(tuple(point))
    
    return curve_points
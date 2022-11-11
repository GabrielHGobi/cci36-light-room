import numpy as np

def saturate_color(color):
    """
    Saturate all color channels of a color to make them between 0.0 and 1.0.
    """
    return np.clip(color, a_min=0.0, a_max=1.0)

def apply_gama(color, gama_factor):
    """
    Apply a gama correction to change color luminance.
    """
    return np.power(color, gama_factor)
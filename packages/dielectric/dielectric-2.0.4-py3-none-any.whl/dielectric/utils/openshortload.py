import numpy as np


def openonly(Z_meas, Z_open):
    """Complex impedance correction using open circuit

    Args:
        Z_meas (ndarray):    measured raw complex impedance (uncorrected)
        Z_open (ndarray):    impedance measurement with open cell terminals

    Returns:
        Z_c (ndarray):       corrected complex impedance derived from Z_meas, Z_open
    """
    nom = Z_open
    denom = Z_open - Z_meas
    factor = Z_meas
    Z_c = nom / denom
    Z_c *= factor
    return Z_c


def openshort(Z_meas, Z_open, Z_short):
    """Complex impedance correction using open and short circuit

    Args:
        Z_meas (ndarray):     measured raw complex impedance (uncorrected)
        Z_open (ndarray):     impedance measurement with open cell terminals
        Z_short (ndarray):    impedance measurement with shorted terminals or cell

    Returns:
        Z_c (ndarray):        corrected complex impedance derived from Z_meas, Zopen, Z_short
    """
    nom = Z_open - Z_short
    denom = Z_open - Z_meas
    factor = Z_meas - Z_short
    Z_c = nom / denom
    Z_c *= factor
    return Z_c


def openshortload(Z_meas, Z_open, Z_short, Z_load):
    """Complex impedance correction using open, short circuit and reference load

    Args:
        Z_meas (ndarray):     measured raw complex impedance (uncorrected)
        Z_open (ndarray):     impedance measurement with open cell terminals
        Z_short (ndarray):    impedance measurement with shorted terminals or cell
        Z_load (ndarray):     measured complex impedance of reference load

    Returns:
        Z_c (ndarray):        corrected complex impedance derived from Z_meas, Z_open, Z_short, Z_load
    """
    nom1 = Z_open - Z_load
    denom1 = Z_open - Z_meas
    nom2 = Z_meas - Z_short
    denom2 = Z_load - Z_short
    Z_c = nom1 / denom1
    Z_c *= nom2 / denom2
    return Z_c


def loadshort(Z_meas, Z_short, Z_e, Z_me):
    """Complex impedance correction using short circuit and reference load (Alternative A)

    Args:
        Z_meas (ndarray):     measured raw complex impedance (uncorrected)
        Z_short (ndarray):    impedance measurement with shorted terminals or cell
        Z_e (ndarray):        theoretical complex impedance of reference load
        Z_me (ndarray):       measured complex impedance of reference load

    Returns:
        Z_c (ndarray):        corrected complex impedance derived from Z_meas, Z_short, Z_e, Z_me
    """
    factor1 = Z_short - Z_me
    factor2 = Z_meas - Z_short
    nom = Z_e * factor1 * factor2
    denom = (Z_e * factor1) - (Z_me - Z_short - Z_e) * factor2
    Z_c = nom / denom
    return Z_c


def loadload(Z_meas, Z_e1, Z_e2, Z_me1, Z_me2):
    """Complex impedance correction using two reference loads (Alternative B)

    Args:
        Z_meas (ndarray):      measured raw complex impedance 1 (uncorrected)
        Z_e1 (ndarray):        theoretical complex impedance of reference load 1
        Z_e2 (ndarray):        theoretical complex impedance of reference load 2
        Z_me1 (ndarray):       measured complex impedance of reference load 1
        Z_me2 (ndarray):       measured complex impedance of reference load 2

    Returns:
        Z_c (ndarray):        corrected complex impedance derived from Z_meas, Z_e1, Z_e2, Z_me
    """
    theta = 1 + 4 * Z_e1 * Z_e2 / ((Z_me1 - Z_me2) * (Z_e1 - Z_e2))
    factor1 = (Z_e1 + Z_e2) + (Z_e1 - Z_e2) * np.sqrt(theta)
    factor2 = 2 * ((Z_e1 - Z_e2) / (Z_me1 - Z_me2) - 1)
    Z_B = factor1 / factor2
    Z_A = Z_me1 - Z_e1 / (1 + Z_e1 / Z_B)
    nom = Z_B * (Z_meas - Z_A)
    denom = Z_A + Z_B - Z_meas
    Z_c = nom / denom
    return Z_c

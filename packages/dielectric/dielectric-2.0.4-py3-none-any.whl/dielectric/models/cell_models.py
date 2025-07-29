import numpy as np
from lmfit import Model


def model_ep(omega, Rb: float, Cb: float, Cep: float):
    """calculate impedance for conductivity cell equivalent circuit.
        Rb // Cb, in series with Cep

    Args:
        omega: array with angular velocities (2*pi*f)
        Rb:    resistance parallel to cell capacity (dominates intermediate frequency range)
        Cb:    cell capacity (smaller, determines HF behaviour)
        Cep:   capacity due to electrode polarization (larger, dominates at LF)

    Returns: array with cell impedance values at angular velocities in omega

    """
    Rb_array = Rb * np.ones_like(omega)
    z_recip = (1.0 / Rb_array) + 1j * omega * Cb
    zs = 1.0 / z_recip
    return zs + 1.0 / (1j * omega * Cep)


def model_Cep_Rs_Ls(omega, Rb: float, Cb: float, Cep: float, Ls: float, Rs: float):
    """calculate impedance for conductivity cell equivalent circuit.
        Rb // Cb, in series with Cep, Rlead and Llead

    Args:
        omega: array with angular velocities (2*pi*f)
        Rb:    resistance parallel to cell capacity (dominates intermediate frequency range)
        Cb:    cell capacity (smaller, determines HF behaviour)
        Cep:   capacity due to electrode polarization (larger, dominates at LF)
        Ls:
        Rs:

    Returns: array with cell impedance values at angular velocities in omega

    """
    Rb_array = Rb * np.ones_like(omega)
    z_recip = (1.0 / Rb_array) + 1j * omega * Cb
    zs = 1.0 / z_recip
    return zs + 1.0 / (1j * omega * Cep) + (1j * omega * Ls) + (Rs * np.ones_like(omega))


def model_Rep_Cep_Rs_Ls(omega, Rb: float, Cb: float,
                        Rep: float, Cep: float,
                        Ls: float, Rs: float):
    """calculate impedance for conductivity cell equivalent circuit.
        Rb // Cb, in series with Rep // Cep, Rs and Ls

    Args:
        omega: array with angular velocities (2*pi*f)
        Rb:    resistance parallel to cell capacity (dominates intermediate frequency range)
        Cb:    cell capacity (smaller, determines HF behaviour)
        Rep:   resistance at DC if electrode polarization is present
        Cep:   capacity due to electrode polarization (larger, dominates at LF)
        Ls:    series inductance (leads)
        Rs:    series resistance (leads)

    Returns: array with cell impedance values at angular velocities in omega

    """
    Rb_array = Rb * np.ones_like(omega)
    Rep_array = Rep * np.ones_like(omega)
    z_recip = (1.0 / Rb_array) + 1j * omega * Cb
    zs = 1.0 / z_recip
    z_recip_ep = (1.0 / Rep_array) + 1j * omega * Cep
    z_ep = 1.0 / z_recip_ep
    return zs + z_ep + (1j * omega * Ls) + (Rs * np.ones_like(omega))


def model_Rdc_Cep_Rs_Ls(omega, Rb: float, Cb: float,
                        Rdc: float, Cep: float,
                        Ls: float, Rs: float):
    """calculate impedance for conductivity cell equivalent circuit.
        Rb // Cb, in series with Cep, Rs and Ls
        Rdc // ( Rb // Cb, in series with Cep)

    Args:
        omega: array with angular velocities (2*pi*f)
        Rb:    resistance parallel to cell capacity (dominates intermediate frequency range)
        Cb:    cell capacity (smaller, determines HF behaviour)
        Rdc:   resistance at DC if electrode polarization is present
        Cep:   capacity due to electrode polarization (larger, dominates at LF)
        Ls:    series inductance (leads)
        Rs:    series resistance (leads)

    Returns: array with cell impedance values at angular velocities in omega

    """
    Rb_array = Rb * np.ones_like(omega)
    Rdc_array = Rdc * np.ones_like(omega)
    zb_recip = (1.0 / Rb_array) + 1j * omega * Cb  # Rb // Cb
    zb = 1.0 / zb_recip
    zep = zb + 1.0 / (1j * omega * Cep)  # (Rb // Cb) in series with Cep
    zdc_recip = (1.0 / zep) + (1.0 / Rdc_array)  # ((Rb // Cb) in series with Cep) // Rdc
    zdc = 1.0 / zdc_recip  # reciprocal
    return zdc + (1j * omega * Ls) + (Rs * np.ones_like(omega))


def model2_ep(omega, Rb: float, Cb: float, Cep: float):
    Rb_array = Rb * np.ones_like(omega)
    Cb_array = Cb * np.ones_like(omega)
    Cb_array += 1.0 / (np.square(omega) * np.square(Rb) * Cep)
    zc_recip = (1.0 / Rb_array) + 1j * omega * Cb_array
    return 1.0 / zc_recip


def model_real_capacitor(omega, C: float, L: float, R: float, R_leak: float):
    leak_array = R_leak * np.ones_like(omega)
    z_recip = (1.0 / leak_array) + 1j * omega * C
    zc = 1.0 / z_recip
    return zc + (1j * omega * L) + (R * np.ones_like(omega))


if __name__ == "__main__":
    cell_model = Model(model_Rep_Cep_Rs_Ls)
    print(f'parameter names: {cell_model.param_names}')
    print(f'independent variables: {cell_model.independent_vars}')

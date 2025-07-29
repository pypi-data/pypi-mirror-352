
from dielectric.constants import *
from dielectric.classes.cells import Cell, PlanarCell, CylindricalCell
from dielectric.classes.electrolytes import Electrolyte
from dielectric.classes.particles import SingleParticle


# https://stackoverflow.com/questions/16444719/python-numpy-complex-numbers-is-there-a-function-for-polar-to-rectangular-co


def R2P(z):
    """converts complex number to polar coordinates modulus and phase

    Args:
        z: complex number(s)

    Returns:
       (tuple): (modulus, phase) of input complex number(s)
    """
    return abs(z), np.angle(z)


def P2R(A, phi):
    """convert modulus and phase to complex number.
        uses A*exp(j*phi) or A*(cos(phi) + j*sin(phi))

    Args:
        A:    modulus of complex number(s)
        phi:  phase of complex number(s)

    Returns:
        complex number(s) with input modulus and phase

    """
    # return A * np.exp(1j*phi)
    return A * (np.cos(phi) + np.sin(phi) * 1j)


def find_lambdas(omega, e: Electrolyte):
    """calculate eigenvalues of Poisson equation for electrolyte

    Args:
        omega: angular velocity array of impedance measurement (rad/s)
        e:     instance of Electrolyte class

    Returns:
        (ndarray, ndarray) : eigenvalues and eigenvectors
    """
    factor = (np.square(E_CHARGE) * N_AVO) / (EPS_ZW * BOLTZ_T)
    A = np.zeros((2, 2), dtype=complex)
    s = e.salts[0]
    A[0, 0] = factor * s.conc * s.ions[0].nu * np.square(s.ions[0].z) + 1j * omega / s.ions[0].D
    A[1, 1] = factor * s.conc * s.ions[1].nu * np.square(s.ions[1].z) + 1j * omega / s.ions[1].D
    A[1, 0] = factor * s.conc * s.ions[1].nu * s.ions[1].z * s.ions[0].z
    A[0, 1] = factor * s.conc * s.ions[0].nu * s.ions[0].z * s.ions[1].z
    eigenvalues, eigenvectors = np.linalg.eig(A)
    return eigenvalues, eigenvectors


def complex_perm_below_omega_zero(omega, e: Electrolyte, c: Cell):
    """FULL THEORY, limited to omega << kappa^2 * D0
                    or to be used in the particular case
                    that D1 = D2 (then valid for all frequencies)

    Args:
        omega:    angular velocity array of impedance measurement (rad/s)
        e:        instance of Electrolyte class
        c:        instance of PlanarCell class or subclass

    Returns:
        K (array):       conductivity(omega)
        EPSreal (array): relative permittivity(omega)
    """
    lambda_c2 = e.kappa2 + 1j * omega / e.Dc  # Chassagne 2016 Eq. (24)
    lambda_n2 = 1j * omega / e.Dn
    e.lambda_c2 = lambda_c2
    e.lambda_n2 = lambda_n2

    # see (6.34 in thesis):
    if isinstance(c, PlanarCell):
        EPS = 1.0 - e.kappa2 / lambda_c2 * (1.0 - 2.0 / np.sqrt(lambda_c2 * np.square(c.dist)))
        EPS += 1j * omega / (e.kappa2 * e.Dt) * (1.0 - 2.0 / np.sqrt(lambda_n2 * np.square(c.dist)))
        EPS = EPS_WATER / EPS
    elif isinstance(c, CylindricalCell):
        EPS = 1j * omega / (e.kappa2 * e.D_zero) * c.log_ratio_radii
        EPS += (1.0 / np.sqrt(lambda_c2)) * (e.kappa2 / lambda_c2) * c.one_over_inner_plus_one_over_outer
        EPS -= (1.0 / np.sqrt(lambda_n2)) * (1j * omega / (e.kappa2 * e.Dt)) * c.one_over_inner_plus_one_over_outer
        EPS = EPS_WATER / EPS
        # Note: can be simplified even more if 1/Dt = 0, then third line can be commented out
    else:
        EPS = np.zeros_like(omega) + 1j * np.zeros_like(omega)  # complex zeros
        print("calculation of EPS not implemented for this type of cell")

    EPSreal = np.real(EPS)
    K = -np.imag(EPS) * omega * EPS_ZERO
    return K, EPSreal


def alternate(l):
    """calculates alternating sum of input list.

    See: https://stackoverflow.com/questions/41339744/
         writing-a-function-that-alternates-plus-and-minus-signs-between-list-indices
         https://www.geeksforgeeks.org/python-alternate-element-summation-in-list/
    """
    return sum(l[::2]) - sum(l[1::2])


def complex_perm_full(omega, e: Electrolyte, c: Cell):
    """# THEORY ANY FREQUENCY, not to be used when D1 = D2

    Args:
        omega:    angular velocity array of impedance measurement (rad/s)
        e:        instance of Electrolyte class
        c:        instance of Cell class or subclass

    Returns:
        K (array):       conductivity(omega)
        EPSreal (array): relative permittivity(omega)
    """
    ll = [ion.nu * np.square(ion.z) for salt in e.salts for ion in salt.ions]
    nom = alternate(ll)
    denom = np.sum(ll)
    help1 = nom/denom

    ll2 = [1.0/ion.D for salt in e.salts for ion in salt.ions]
    dpm = alternate(ll2)
    re_delta = 1.0 - np.square(omega) * np.square(dpm) / np.square(e.kappa2)
    im_delta = 2.0 * omega / e.kappa2 * help1 * dpm
    delta = np.sqrt(re_delta + 1j * im_delta)

    dpp = np.sum(ll2)
    lambda_n2 = e.kappa2 / 2.0 + 1j * omega / 2 * dpp - 0.5 * e.kappa2 * delta
    lambda_c2 = e.kappa2 / 2.0 + 1j * omega / 2 * dpp + 0.5 * e.kappa2 * delta
    lambda_c = np.sqrt(lambda_c2)
    lambda_n = np.sqrt(lambda_n2)

    e.lambda_c2 = lambda_c2
    e.lambda_n2 = lambda_n2

    if isinstance(c, PlanarCell):
        A1 = -(1 + 1j * omega / (e.kappa2 * e.Dc) - lambda_n2 / e.kappa2)
        A2 = (1 + 1j * omega / (e.kappa2 * e.Dc) - lambda_c2 / e.kappa2)
        B = A1 / lambda_c2 * (1.0 - 2.0 / (c.dist * lambda_c)) + A2 / lambda_n2 * (
                1.0 - 2.0 / (c.dist * lambda_n))
        EPS = EPS_WATER / (1.0 + np.square(e.kappa2) * B / (lambda_c2 - lambda_n2))
    elif isinstance(c, CylindricalCell):
        H1 = e.kappa2 / (lambda_c2 - lambda_n2) * c.one_over_inner_plus_one_over_outer
        H2 = (e.kappa2 - lambda_n2 + 1j * omega / e.Dc) / (lambda_c2 * lambda_c)
        H3 = (e.kappa2 - lambda_c2 + 1j * omega / e.Dc) / (lambda_n2 * lambda_n)
        EPS = (H1 * (H2 - H3) + (1.0 - e.kappa2 / lambda_c2 * 1j * omega / (lambda_n2 * e.Dn)) * c.log_ratio_radii)
        EPS = EPS_WATER / EPS

        # EPS2 = e.kappa2 / (lambda_c2*lambda_c) * c.one_over_inner_plus_one_over_outer + (1 - e.kappa2/lambda_c2 * 1j*omega/ (lambda_n2* Dn))
        # EPS2 *= c.log_ratio_radii
        # EPS2 = EPS_WATER / EPS2
    else:
        print("calculation of EPS not implemented for this type of cell")

    EPSreal = np.real(EPS)
    K = -np.imag(EPS) * omega * EPS_ZERO
    return K, EPSreal


def complex_perm_full_alt(omega, e: Electrolyte, c: Cell):
    """# THEORY ANY FREQUENCY, not to be used when D1 = D2

    Args:
        omega:    angular velocity array of impedance measurement (rad/s)
        e:        instance of Electrolyte class
        c:        instance of Cell class or subclass

    Returns:
        K (array):         conductivity(omega)
        EPSreal (array):   relative permittivity(omega)
    """
    ll = [ion.nu * np.square(ion.z) for salt in e.salts for ion in salt.ions]
    nom = alternate(ll)
    denom = np.sum(ll)
    help1 = nom/denom

    ll2 = [1.0/ion.D for salt in e.salts for ion in salt.ions]
    dpm = alternate(ll2)
    re_delta = 1.0 - np.square(omega) * np.square(dpm) / np.square(e.kappa2)
    im_delta = 2.0 * omega / e.kappa2 * help1 * dpm
    delta = np.sqrt(re_delta + 1j * im_delta)

    dpp = np.sum(ll2)
    lambda_n2 = e.kappa2 / 2.0 + 1j * omega / 2 * dpp - 0.5 * e.kappa2 * delta
    lambda_c2 = e.kappa2 / 2.0 + 1j * omega / 2 * dpp + 0.5 * e.kappa2 * delta
    lambda_c = np.sqrt(lambda_c2)
    lambda_n = np.sqrt(lambda_n2)

    e.lambda_c2 = lambda_c2
    e.lambda_n2 = lambda_n2

    C1 = e.kappa2 / lambda_c2 * 1j * omega / (lambda_n2 * e.Dn)
    # in line below, lambda_c2 is different from in original THEORY3.m ! ?
    CA1 = (e.kappa2 - lambda_n2) / (lambda_c2 - lambda_n2) + 1j * omega / ((lambda_c2 - lambda_n2) * e.Dc)

    if isinstance(c, PlanarCell):
        CA1 /= 1.0 + np.exp(-lambda_c * c.dist)
        CA1 *= 2.0 / (lambda_c * c.dist) * e.kappa2 / lambda_c2

        CA2 = (e.kappa2 - lambda_c2) / (lambda_c2 - lambda_n2) + 1j * omega / ((lambda_c2 - lambda_n2) * e.Dc)
        CA2 /= 1.0 + np.exp(-lambda_n * c.dist)
        CA2 *= 2.0 / (lambda_n * c.dist) * e.kappa2 / lambda_n2

        EPS = EPS_WATER / (1.0 - C1 + CA1 + CA2)
    else:
        print("calculation of EPS not implemented for this type of cell")

    EPSreal = np.real(EPS)
    K = -np.imag(EPS) * omega * EPS_ZERO
    return K, EPSreal


def dipole_coef(rzeta: float, ka: float, method='Chassagne'):
    """ dipole coefficient for a colloidal sphere (approx.)

    Args:
        rzeta:    zeta potential in kT/e units
        ka:       kappa * radius
        method:   currently "Chassagne"

    Returns:
        ic (array) : at infinity
        in (array) : at infinity

    """
    if method == 'Chassagne':
        if rzeta > 1.0:
            # HIGH ZETA POTENTIAL Chassagne 2008, Eq.(55)
            qadim = 2.0 * np.sinh(rzeta / 2.0)
            qadim += 4.0 / ka * np.tanh(rzeta / 4.0)
            qadim -= rzeta / ka
            # surf = (qadim-rzeta/ka) * epsilon_zero * epsilon_water * Boltz_T * np.sqrt(kappa2) / elem_charge
            ic_inf = qadim / ka
            in_inf = -np.abs(ic_inf)  # polydisperse.m
            # in_inf = -ic_inf + (1.0 + 2.0*ka) / 2.0 * np.square(ka) # article_2015.m
        else:
            # LOW ZETA POTENTIAL
            ic_inf = rzeta / ka
            in_inf = 0.0
    elif method == 'Ohshima':
        qOhshi = (2. * (np.cosh(rzeta) - 1.0 + 8.0 / ka * (
                np.cosh(rzeta / 2.0) - 1.0 + 2.0 / ka * np.log(np.cosh(rzeta / 4.0))))) ^ 0.5 - rzeta / ka
        IcinfOhshi = qOhshi / ka

    elif method == 'Turnhout':
        IcJan = (np.sqrt(2.0 * (ka) ** 2 * (np.cosh(rzeta) - 1.0) + (1.0 + 2.0 * ka) * rzeta ** 2) - rzeta) / (ka) ** 2
        yJan = (1.0 + 2.0 * ka - np.exp(-rzeta) * (ka * (rzeta + 2.0) + rzeta + 1.0)) / (2.0 * ka ** 2)
        yJan2 = (2.0 * ka + 1.0) * (1.0 - np.exp(-2.0 * ka * rzeta / (np.sqrt(np.exp(1) * (2.0 * ka + 1))))) / (
                2.0 * ka ** 2)

        IninfJan3 = -IcJan + yJan
        IninfJan4 = -IcJan + yJan2
        IninfJan = 0.2 * IninfJan3 + 0.8 * IninfJan4

    return ic_inf, in_inf


def cond_part(omega, e: Electrolyte, p: SingleParticle):
    """

    Args:
        omega:    angular velocity array of impedance measurement (rad/s)
        e:        instance of Electrolyte class
        p:        instance of Particles class

    Returns:
        K1tilde (array):
        beta (array):

    """
    kr = e.kappa * p.radius

    # dipole coefficient
    ic_inf, in_inf = dipole_coef(p.rel_zeta, kr)

    # conductivity
    K1_tilde = e.sigma + 1j * EPS_ZW * omega

    # conductivity interior particle
    K2_tilde = 1j * EPS_ZERO * p.eps * omega

    lambda_n = np.sqrt(e.lambda_n2)
    delta1 = 2.5 / (1.0 + 2.0 * np.exp(-kr))
    r1 = p.radius + delta1 / e.kappa
    delta0 = 1.0 + 3.0 / kr * np.exp(-p.rel_zeta / 2.0)
    r0 = p.radius + delta0 / e.kappa
    J1 = 1.0 + lambda_n * r0
    J2 = 2.0 + 2.0 * lambda_n * p.radius + e.lambda_n2 * np.square(p.radius)

    mobrien = 2.0 / 3.0 * (EPS_ZW * np.square(BOLTZ_T)) / (e.D_zero * ETA_VISC * np.square(E_CHARGE))
    Us = EPS_ZW * p.rel_zeta / ETA_VISC
    KU = -(e.sigma * mobrien * p.rel_zeta * ic_inf) * (
            J1 / (2.0 * J2 * (r0 / p.radius) ** 3 * np.exp(lambda_n * (r0 - p.radius))) - 1.0)
    Kper = (2.0 * J1 * e.sigma * in_inf) / (J2 * np.exp(lambda_n * (r0 - p.radius)) * (r0 / p.radius) ** 3)
    Kpar = -e.sigma * in_inf - (2.0 * J1 * e.sigma * (np.square(ic_inf) - np.square(in_inf))) / (
            J2 * np.exp(lambda_n * (r0 - p.radius)) * (r0 / p.radius) ** 3)

    beta = (K2_tilde - K1_tilde + 2.0 * (Kpar + KU) + Kper) / (K2_tilde + 2.0 * K1_tilde + 2.0 * (
            Kpar * (r0 / p.radius) ** 3 + KU * (r1 / p.radius) ** 3) - 2.0 * Kper)

    return K1_tilde, beta


"""
def cyl_cond(omega,  e:Electrolyte, c: CylindricalCell):
        FULL THEORY, limited to omega << kappa^2 * D0
        with 1/Dc = 1/D0 + 1/Dt replaced by 1/D0 (1/Dt = 0)
        and term with 1/Dt set to zero

    Args:
        omega:  angular velocity array of impedance measurement (rad/s)
        e:      instance of Electrolyte class
        c:      instance of CylindricalCell class

    Returns:
        K       (array):   conductivity(omega)
        EPSreal (array):   relative permittivity(omega)

    lambda_c2 = e.kappa2 + 1j*omega / e.D_zero
    lambda_c = np.sqrt(lambda_c2)
    EPS = 1j*omega/(e.kappa2*e.D_zero) * c.log_ratio_radii
    EPS += (1.0/lambda_c) * (e.kappa2/lambda_c2) * c.one_over_inner_plus_one_over_outer
    EPS = EPS_WATER / EPS

    EPSreal = np.real(EPS)
    K = -np.imag(EPS) * omega * EPS_ZERO
    return K, EPSreal
"""


if __name__ == "__main__":
    from pathlib import Path

    DATADIR = Path(__file__).parent.parent.parent.parent.absolute().joinpath("ImpedanceData")

    omega = np.logspace(1, 8, 100)

    e2 = Electrolyte.from_yaml(str(DATADIR / "Cell_1_KCl_1mM.yaml"))
    eigvals, eigvect = find_lambdas(omega[0], e2)
    for ev in eigvals:
        print(ev)

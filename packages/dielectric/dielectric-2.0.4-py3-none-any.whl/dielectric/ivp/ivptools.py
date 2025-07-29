
from dielectric.constants import *
from dielectric.classes.electrolytes import Electrolyte, Ion
import matplotlib
import matplotlib.pyplot as plt


matplotlib.use("QtAgg")


def calc_kappa_q(e: Electrolyte):
    sumD = 0.0
    kappa2q = 0.0
    for salt in e.salts:
        for ion in salt.ions:
            sumD += ion.D
    for salt in e.salts:
        for ion in salt.ions:
            factor = ion.D/sumD
            kappa2q += KAPPA2_ZERO * salt.conc * ion.nu * np.square(ion.z) * factor
    return np.sqrt(kappa2q)


def calc_Aij(e: Electrolyte, Gamma, sigma):
    Aij = 0.0
    pr = 1.0
    for salt in e.salts:
        for ion in salt.ions:
            pr *= ion.z*E_CHARGE
    denom = 4.0 * np.pi * EPS_ZW * BOLTZ_T * np.square(1.0 + Gamma * sigma)
    Aij = pr / denom
    return Aij


def calc_i0(arg):
    return np.sinh(arg) / arg


def calc_i1(arg):
    return (np.cosh(arg) / arg) - (np.sinh(arg) / np.square(arg))


def calc_alpha_k(e: Electrolyte, kappa_q, Gamma, sigma, Aij, i0, i1):
    pr = 1.0
    for salt in e.salts:
        for ion in salt.ions:
            pr *= ion.z*E_CHARGE
    factor = np.reciprocal(pr / (4.0*np.pi*EPS_ZW*BOLTZ_T))

    tempa = (np.square(kappa_q)/3.0) * (i0 - (factor * kappa_q * np.square(sigma) * i1))
    tempb = kappa_q * Aij * np.exp(-kappa_q * sigma)
    tempc = np.square(kappa_q) + 2.0*Gamma*kappa_q + 2.0*np.square(Gamma) * (1.0-np.exp(-kappa_q * sigma))
    return (tempa * tempb) / tempc


def calc_diff_new(ion: Ion, kap, Gamma, sigma, alpha_k):
    omega = (ion.D * (1.0 + alpha_k))
    omega -= ((BOLTZ_T * kap) / (6.0 * np.pi * ETA_VISC * np.square(1.0 + (Gamma * sigma))))
    return omega


def cap_dumb(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = np.pi * EPS_ZW * radius * length
    cap /= distance
    return cap


def cap_parallel_approx(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = np.pi * EPS_ZW * length
    arg = (distance-radius) / radius
    denom = np.log(arg)
    cap /= denom
    return cap


def cap_parallel_approx2(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = np.pi * EPS_ZW * length
    arg = distance / radius
    denom = np.log(arg)
    cap /= denom
    return cap


def cap_parallel_wires(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = np.pi * EPS_ZW * length
    arg = 0.5 * (distance / radius)
    # print(f"arg: {arg}")
    denom = arg + np.sqrt(np.square(arg) - 1)
    denom = np.log(denom)
    cap /= denom
    return cap


def cap_parallel_wires_acosh(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = np.pi * EPS_ZW * length
    arg = 0.5 * (distance / radius)
    # print(f"arg: {arg}")
    denom = np.arccosh(arg)
    cap /= denom
    return cap


def cap_wire_wall(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = 2.0 * np.pi * EPS_ZW * length
    arg = distance / radius
    # print(f"arg: {arg}")
    denom = arg + np.sqrt(np.square(arg) - 1)
    denom = np.log(denom)
    cap /= denom
    return cap


def cap_wire_wall2(distance=1e-3, radius=0.1e-3, length=1e-2):
    cap = 2.0 * np.pi * EPS_ZW * length
    arg = distance / radius
    cap /= np.arccosh(arg)
    return cap


def cap_single_wire(radius=0.1e-3, length=1e-2):
    LL = np.log(length/radius)
    factor = 1.0 - np.log(2)
    cap_zero = (2.0*np.pi*EPS_ZW*length) / LL
    cap = cap_zero * (1 + factor/LL + (1 + np.square(factor) - (np.square(np.pi)/12)) / np.square(LL))
    # print(f"single (zero): {cap_zero*1e12} pF")
    return cap


def calc_argument(distance=1e-3, radius=0.1e-3):
    distance = np.asarray(distance)
    radius = np.asarray(radius)
    scalar_input = False
    if distance.ndim == 0:
        distance = distance[np.newaxis]
        radius = radius[np.newaxis]
        scalar_input = True
    arg = 0.5 * (distance / radius)
    s = np.square(arg) - 1.0
    if scalar_input:
        print(f"arg: {arg.item()}")
        return arg.item(0)
    return s


if __name__ == "__main__":
    wire_radius = 25e-6
    wire_length = 8.0e-3
    wire_dist = 2.25e-3
    wall_dist = 20e-3
    C_ww = cap_parallel_wires(wire_dist, wire_radius, wire_length)
    # C_ww2 = cap_parallel_wires_acosh(wire_dist, wire_radius, wire_length)
    cc_ww = np.reciprocal(C_ww / EPS_ZW)
    C_w_wall = cap_wire_wall(wall_dist, wire_radius, wire_length)
    # C_approx = cap_parallel_approx2(2.25e-3, 0.25e-4, 0.008)
    # C_dumb = cap_dumb(2.25e-3, 0.25e-4, 0.008)
    C_single = cap_single_wire(wire_radius, wire_length)
    # C2 = cap_parallel_wires2(2.25e-3, 0.2e-3, 0.01)
    # C_w_wall2 = cap_wire_wall2(2.25e-3, 0.2e-3, 0.01)

    print(f"Capacity (parallel-wires): {C_ww*1e12:.4g} pF, cell constant: {cc_ww} m^-1")
    # print(f"Capacity (parallel-wires-acosh): {C_ww2*1e12:.4g} pF")
    print(f"Capacity (wire-wall): {C_w_wall*1e12:.5g} pF")
    print(f"Capacity (single-wire): {C_single*1e12:.5g} pF")

    """
    dista = np.linspace(0.1e-3, 2.5e-3, 25)
    rad = np.ones_like(dista) * wire_radius
    arg_s = calc_argument(dista, rad)
    print()

    fig, ax = plt.subplots()
    ax.plot(dista, arg_s)
    # ax.set_ylim(-100, 100)
    plt.show()
    """


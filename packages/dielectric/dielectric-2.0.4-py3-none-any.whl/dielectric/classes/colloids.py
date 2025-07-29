
from dielectric.constants import *  # imports numpy
from dielectric.classes.cells import (Cell, PlanarCell,
                                      CylindricalCell, ParallelWireCell)
from dielectric.classes.electrolytes import Electrolyte
from dielectric.poly.polyutils import complex_perm_full
# from dielectric.classes.particles import Particle, read_particles


class Colloid:
    """class for colloid with electrolyte and particles.

    Attributes:
        c (Cell): electrolysis or conductivity Cell object.
        e (Electrolyte): Electrolyte object with properties.
        part (list): list of SingleParticle species.
        Cpol (float): electrode polarization capacitance.
        C0 (float): cell capacitance.
        R0 (float): cell resistance.
        Rseries (float): series lead resistance.
        Lseries (float): series cell inductance.
        Z0 = None
        Zeq = None
        Keq = None
        EPSeq = None
        omega_p = None
        omega_c = None
        omega_zero = None
        omega_h = None
    """

    def __init__(self, c: Cell, e: Electrolyte, part: list = None):
        self.c = c
        self.e = e
        self.part = part
        self.Cpol = None
        self.C0 = None
        self.R0 = None
        self.Rseries = None
        self.Lseries = None
        self.Z0 = None
        self.Zeq = None
        self.Keq = None
        self.EPSeq = None
        self.omega_p = None
        self.omega_c = None
        self.omega_zero = None
        self.omega_h = None

    def calc_eq_circuit(self, Rseries=0.0, Lseries=0.0):
        """calculate equivalent circuit of conductance cell.

        Args:
            Rseries (float): series lead resistance
            Lseries: (float) series lead and cell inductance
        """
        if isinstance(self.c, PlanarCell):
            self.Cpol = EPS_ZW * self.e.kappa * (self.c.dist / 2.0)
            self.Cpol /= self.c.cell_constant
            # self.C0 = EPS_ZW
            self.C0 = self.c.cap
            # self.R0 = np.reciprocal(self.e.sigma)
            self.R0 = self.c.cell_constant
            self.R0 /= self.e.sigma

        elif isinstance(self.c, CylindricalCell):
            self.Cpol = 2.0 * np.pi * self.c.height * EPS_ZW * self.e.kappa
            self.Cpol /= self.c.one_over_inner_plus_one_over_outer
            self.C0 = 2.0 * np.pi * self.c.height * EPS_ZW
            self.C0 /= self.c.log_ratio_radii
            self.R0 = np.reciprocal(2.0 * np.pi * self.c.height)
            self.R0 *= self.c.log_ratio_radii
            self.R0 /= self.e.sigma

        elif isinstance(self.c, ParallelWireCell):
            self.Cpol = 1.0  # F
            self.C0 = self.c.cap
            self.R0 = self.c.cell_constant
            self.R0 /= self.e.sigma

        else:
            print("calculation of Cpol, C) and R0 not implemented for this type of cell")
        self.Rseries = Rseries  # Ohm
        self.Lseries = Lseries  # nH

        print(f"C_p = {self.Cpol * 1e6:.4g} microF")
        print(f"C_0 = {self.C0 * 1e12:.4g} pF")
        print(f"R_0 = {self.R0 / 1e3:.4g} kOhm ({np.reciprocal(self.R0)*1.0e6:.4g} uS)")
        print(f"L_series = {self.Lseries * 1e9:.4g} nH")
        print(f"R_series = {self.Rseries:.4g} Ohm")

    def calc_eq_circuit2(self, Rseries=0.0, Lseries=0.0):
        """calculate equivalent circuit of conductance cell.

        Args:
            Rseries (float): series lead resistance
            Lseries: (float) series lead and cell inductance
        """
        if isinstance(self.c, PlanarCell):
            self.Cpol = self.c.cap * self.e.kappa * (self.c.dist / 2.0)
            self.C0 = self.c.cap
            self.R0 = np.reciprocal(self.e.sigma)
            self.R0 *= self.c.cell_constant

        elif isinstance(self.c, CylindricalCell):
            self.Cpol = 2.0 * np.pi * self.c.height * EPS_ZW * self.e.kappa
            self.Cpol /= self.c.one_over_inner_plus_one_over_outer
            self.C0 = self.c.cap
            self.R0 = np.reciprocal(self.e.sigma)
            self.R0 *= self.c.cell_constant

        elif isinstance(self.c, ParallelWireCell):
            self.Cpol = 1.0  # F
            self.C0 = self.c.cap
            self.R0 = np.reciprocal(self.e.sigma)
            self.R0 *= self.c.cell_constant
        else:
            print("calculation of Cpol, C) and R0 not implemented for this type of cell")
        self.Rseries = Rseries  # Ohm
        self.Lseries = Lseries  # nH

        print(f"C_p = {self.Cpol * 1e6:.4g} microF")
        print(f"C_0 = {self.C0 * 1e12:.4g} pF")
        print(f"R_0 = {self.R0 / 1e3:.4g} kOhm ({np.reciprocal(self.R0)*1.0e6:.4g} uS)")
        print(f"L_series = {self.Lseries * 1e9:.4g} nH")
        print(f"R_series = {self.Rseries:.4g} Ohm")

    def calc_impedance_from_eq_circuit(self, omega):
        """calculate impedance Zeq of equivalent circuit of conductance cell.

        Args:
            omega (array): frequency range for impedance.
        """
        if self.C0 is not None:
            self.Z0 = np.reciprocal(1.0 / self.R0 + 1j*self.C0*omega)  # adapt
            self.Zeq = self.Z0 + 1.0 / (1j*self.Cpol*omega)
            # multiply eq circuit with cell constant
            self.Zeq = self.Zeq * self.c.cell_constant
            # add Rseries and Lseries (they do not depend on cell constant!)
            self.Zeq += 1j * self.Lseries * omega + self.Rseries
            self.Keq = np.real(1.0 / self.Zeq)
            self.EPSeq = np.imag(1.0 / self.Zeq) / (EPS_ZERO * omega)

    def calc_omegas(self):
        """calculation of omega_p and omega_zero.
        """
        if isinstance(self.c, PlanarCell):
            self.omega_p = 2.0 * self.e.D_zero * self.e.kappa / self.c.dist  # ang. vel. (rad/s) associated to cell
            print(f"omega_p = 2*kappa*D/L for omega = {self.omega_p:.3g} rad/s ({self.omega_p / (2 * np.pi):.3g} Hz)")
        elif isinstance(self.c, CylindricalCell):
            self.omega_c = self.e.D_zero * self.e.kappa
            self.omega_c *= self.c.one_over_inner_plus_one_over_outer  # ang. vel. (rad/s) associated to cyl. cell
            print(f"omega_c = {self.omega_c:.3g} rad/s ({self.omega_c / (2 * np.pi):.3g} Hz)")
            self.omega_h = self.e.kappa**3 * self.e.D_zero * self.c.one_over_inner_plus_one_over_outer
            print(f"omega_h = {self.omega_h:.3g} rad/s ({self.omega_h / (2 * np.pi):.3g} Hz)")
        else:
            print("calculation of omega_p not implemented for this type of cell")

        self.omega_zero = self.e.kappa2 * self.e.D_zero  # ang. vel. (rad/s) associated to Debye relaxation
        print(f"omega_0 = kappa^2 * D for omega = {self.omega_zero:.3g} rad/s ({self.omega_zero / (2 * np.pi):.3g} Hz)")


if __name__ == "__main__":
    from pathlib import Path

    DATADIR = Path(__file__).parent.parent.parent.parent.absolute().joinpath("ImpedanceData")

    Cell_1 = PlanarCell.from_yaml(str(DATADIR / "Cell_1_KCl_1mM.yaml"))
    Cell_1.cell_constant = 1.0
    el = Electrolyte.from_yaml(str(DATADIR / "Cell_1_KCl_1mM.yaml"))
    # print(f"kappa^2: {e.kappa2}")
    system = Colloid(Cell_1, el)
    system.calc_omegas()
    system.calc_eq_circuit()

    w = np.logspace(1, 9, 500)
    freq = w / TWOPI
    system.calc_impedance_from_eq_circuit(w)

    # theoretical calculation for Z_e
    K_e, EPS_e = complex_perm_full(w, el, Cell_1)

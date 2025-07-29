
import copy
from collections import OrderedDict
from dielectric.constants import *  # imports numpy as np
from dielectric.utils.file_utils import load_config

import logging

# logging.basicConfig(level="DEBUG")
logging.basicConfig(level="INFO")
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)


class Ion:
    """class for single or unique ionic species.

    Attributes:
        name (str): ion identifier e.g. K+, Cl-.
        mass (float): bare ionic mass in amu.
        radius (float): hydrodynamic radius of ion.
        Lambda (float): limiting molar conductivity of ion.
        D (float): diffusion constant.
        z (float): ionic charge.
        nu (float): stoichiometry of ion in salt.

    Note: either Lambda or D is required.
    """
    def __init__(self, name, mass, radius, z, nu, Lambda=None, D=None):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.Lambda = Lambda
        self.D = D
        self.z = z
        self.nu = nu

        self.unidx = None
        self.conc = None
        self.number_density = None
        self.charge = None
        self.fric = None                         # xi (Gourdin)
        self.ionic_mass = None  # in kg          # mint (Gourdin)
        self.molar_volume = None  # in m^3/mol
        self.ionic_volume = None  # in m^3        # V (Gourdin)
        self.effective_ionic_mass = None  # in kg # mr (Gourdin)
        self.t = None

    @classmethod
    def from_dict(cls, d):
        """ classmethod to enable constructing an instance from configuration file.

        Args:
            d (dict): dictionary with fields from init.

        Returns:
            instance of Ion class.
        """
        ion = cls(name=d.get("name"), mass=d.get("mass"), radius=d.get("radius"),
                  z=d.get("z"), nu=d.get("nu"))
        # for optional parameters, use dict.get method with default value if key does not exist
        ion.Lambda = d.get("Lambda")
        ion.D = d.get("D")           # default value of get method is None by default
        ion.update()
        return ion

    def __deepcopy__(self, memo):
        """create deep copy of Ion object. Set attribute "nu" to None

        Args:
            memo: intermediary dictionary used in deep copying process

        Returns:
            deep, fully recursive copy of Ion object, with attribute "nu" set to None.
        See Also:
            # https: // stackoverflow.com / questions / 68054075 / how - to - deepcopy - python - object - skipping - one - or -more - attributes
            # https://www.adventuresinmachinelearning.com/mastering-object-copying-in-python-with-the-copy-module
            # https://powerfulpython.com/blog/copying-collections-conveniently/
            # https://pymotw.com/2/copy/
            # https://pythonforthelab.com/blog/deep-and-shallow-copies-of-objects/
        """
        cls = self.__class__
        new_obj = cls.__new__(cls)
        memo[id(self)] = new_obj
        for k, v in self.__dict__.items():
            setattr(new_obj, k, copy.deepcopy(v, memo))
            new_obj.__dict__['nu'] = None
        # new_obj.personalization = copy.deepcopy(self.personalization, memo)
        return new_obj

    def D_from_Lambda(self):
        factor = N_AVO*E_CHARGE*E_CHARGE / BOLTZ_T
        if self.Lambda is not None and self.D is None:
            self.D = self.Lambda / (np.abs(self.z) * factor)

    def Lambda_from_D(self):
        factor = N_AVO*E_CHARGE*E_CHARGE / BOLTZ_T
        if self.Lambda is None and self.D is not None:
            self.Lambda = np.abs(self.z) * self.D * factor

    def radius_from_D(self):
        """ calculate hydrodynamic radius from diffusion constant
            with Stokes-Einstein relation"""
        if self.D is not None:
            self.radius = BOLTZ_T / (6*np.pi*ETA_VISC*self.D)

    def D_from_radius(self):
        """ calculate diffusion constant from hydrodynamic radius
            with Stokes-Einstein relation"""
        if self.radius is not None:
            self.D = BOLTZ_T / (6*np.pi*ETA_VISC*self.radius)

    def charge_from_z(self):
        self.charge = self.z *E_CHARGE

    def fric_from_D(self):
        self.fric = BOLTZ_T / self.D

    def ionic_mass_from_molar_mass(self):
        """calculate absolute ionic mass in kg/ion from (relative) molar mass in g/mol
        """
        self.ionic_mass = self.mass / (N_AVO * 1000)

    def calc_molar_volume(self):
        """ calculate molar volume in m^3/mol
        """
        self.molar_volume = (4/3) * np.pi * self.radius**3 * N_AVO
        logging.info(f" molar volume ion '{self.name}' estimation is {self.molar_volume:.4g} m^3/mol "
                     f"({self.molar_volume*1.0e6:.4g} cm^3/mol)")

    def calc_effective_ionic_mass(self):
        """absolute ionic mass in kg/ ion corrected for buoyancy (affects negative ions with large radii)
        """
        self.effective_ionic_mass = self.ionic_mass - (RHO_W * self.ionic_volume)

    def update(self):
        """update the diffusion constant or the limiting molar conductivity.

        Returns:
           ion: an instance of the Electrolyte class
        """
        if self.Lambda is None and self.D is not None:
            self.Lambda_from_D()
        elif self.Lambda is not None and self.D is None:
            self.D_from_Lambda()


class Salt:
    """class for single salt, made up of ions.

    Attributes:
        name (str): salt identifier e.g. KCl.
        conc (float): concentration in mmol/l mol/m^3.
        ions (float): list of Ion objects.
    """
    def __init__(self, name="AxBy", conc=1.0):
        self.name = name
        self.conc = conc
        self.ions = []

# https://www.programiz.com/python-programming/property
    def set_conc_mM(self, new_conc):
        self.conc = new_conc


class Electrolyte:
    """class for electrolyte consisting of single or multiple salts.

    Attributes:
        config_file (str): configuration file name (``*``.yaml).
        num_salts (int): numer of salts in electrolyte.
        salts (list): list of Salt objects in electrolyte.
        kappa2 (float): inverse of Debye length squared
        kappa (float): inverse of Debye length.
        Debye_length (float): Debye length.
        D_zero (float): average diffusion constant for Salt.
        Dc (float):
        Dn (float):
        Dt (float):
        sigma (float):
        lambda_c2 (float):
        lambda_n2 (float):
    """
    def __init__(self):
        # basic attributes
        self.config_file = None
        self.num_salts = None
        self.salts = []
        # calculated attributes
        self.kappa2 = None
        self.kappa = None
        self.Debye_length = None
        self.D_zero = None         # D_zero of electrolyte: sum over salts
        self.Dc = None
        self.Dn = None
        self.Dt = None             # used for omega << k^2*Dzero
        self.sigma = None          # conductivity: was K1
        self.lambda_c2 = None
        self.lambda_n2 = None

    @classmethod
    def from_yaml(cls, config_yaml: str):
        """ classmethod to enable constructing an instance from configuration file.

        Args:
            config_yaml (str): configuration file name.

        Returns:
            Electrolyte class instance.
        """
        el = cls()
        el.config_file = config_yaml
        d = load_config(el.config_file)
        el.num_salts = len(d.get("electrolyte"))
        for n in range(el.num_salts):
            ed = d.get("electrolyte")[n]
            salt = Salt(name=ed.get("name"), conc=ed.get("conc"))
            salt.name = ed.get('name')
            salt.conc = ed.get("conc")
            num_ions = len(ed.get("ions"))
            for i in range(num_ions):
                idict = ed.get("ions")[i]
                ion = Ion.from_dict(idict)
                # append by reference, therefore new Ion object in each iteration
                salt.ions.append(ion)
            # append by reference, therefore new Salt object in each iteration
            el.salts.append(salt)
            logging.info(f" salt '{salt.name}' appended to electrolyte")

        el.update()
        return el

    def update(self):
        self.calc_kappa()
        self.calc_D_zero()
        self.calc_Dc()
        self.calc_Dn_binary()
        self.calc_Dt_binary()
        self.calc_sigma()  # limiting conductivity value

    def calc_kappa(self):
        """calculation of kappa^2, kappa (inverse of Debije length) and Debye length.
        """
        self.kappa2 = 0.0
        factor = (np.square(E_CHARGE) * N_AVO) / (EPS_ZW * BOLTZ_T)

        for salt in self.salts:
            for ion in salt.ions:
                self.kappa2 += factor * salt.conc * ion.nu * np.square(ion.z)

        self.kappa = np.sqrt(self.kappa2)  # inverse of the Debije length
        self.Debye_length = np.reciprocal(self.kappa)
        # logging.info(f" kappa2: {self.kappa2} kappa: '{self.kappa} Debye_length: {self.Debye_length}")

    def calc_D_zero(self):
        """ calculates D_zero as sum over ions: ``|z_i|*D_i over |z_i|``.
        """
        if self.salts:
            nominator = sum(np.abs(ion.z) * ion.D for salt in self.salts for ion in salt.ions)
            denominator = sum(np.abs(ion.z) for salt in self.salts for ion in salt.ions)
            self.D_zero = nominator/denominator

    def calc_sigma(self):
        """calculates limiting conductivity value of electrolyte at infinite dilution.
        """
        if self.kappa2 and self.D_zero:
            self.sigma = EPS_ZW * self.kappa2 * self.D_zero  # limiting conductivity value

    def calc_Dc(self):
        """calculates Dc as sum over ions:  ``|z_i| over |z_i|/D_i/``.
        """
        if self.salts:
            denominator = sum(np.abs(ion.z) / ion.D for salt in self.salts for ion in salt.ions)
            nominator = sum(np.abs(ion.z) for salt in self.salts for ion in salt.ions)
            self.Dc = nominator/denominator

    def calc_Dn_binary(self):
        """calculates Dn as sum over ions:  ``|z_i| over |z_i|/D_j.ne.i``.

        See: https://www.geeksforgeeks.org/python-multiply-all-cross-list-element-pairs/
             https://www.geeksforgeeks.org/python-multiply-numbers-list-3-different-ways/
             https://stackoverflow.com/questions/2853212/all-possible-permutations-of-a-set-of-lists-in-python
             https://numpy.org/doc/stable/reference/generated/numpy.outer.html
             https://numpy.org/doc/stable/reference/generated/numpy.einsum.html
        """
        if self.salts:
            z_list = [np.abs(ion.z) for salt in self.salts for ion in salt.ions]
            one_over_D_list = [1.0/ion.D for salt in self.salts for ion in salt.ions]
            out_mat = np.outer(z_list, one_over_D_list)
            np.fill_diagonal(out_mat, 0.0)
            denominator = np.sum(out_mat)
            nominator = np.sum(z_list)
            self.Dn = nominator/denominator

    def calc_Dt_binary(self):
        """calculates Dt as sum over ions:  ``|z_i| over |z_i|/D_j.ne.i``.

        """
        if self.salts:
            z_list = [ion.z for salt in self.salts for ion in salt.ions]
            z_abs_list = [np.abs(ion.z) for salt in self.salts for ion in salt.ions]
            one_over_D_list = [1.0/ion.D for salt in self.salts for ion in salt.ions]

            dpm = sum(one_over_D_list[::2]) - sum(one_over_D_list[1::2])
            nominator = np.prod(z_list) * np.square(dpm)

            out_mat = np.outer(z_abs_list, one_over_D_list)
            np.fill_diagonal(out_mat, 0.0)
            denominator = np.sum(z_abs_list) * np.sum(out_mat)
            self.Dt = nominator/denominator
            self.Dt = np.reciprocal(self.Dt)


class ElectrolyteIVP:
    """class for electrolyte consisting of multiple salts.

    Attributes:
        config_file (str): configuration file name (``*``.yaml).
        num_salts (int): numer of salts in electrolyte.
        salts (list): list of Salt objects in electrolyte.
        kappa2 (float): inverse of Debye length squared
        kappa (float): inverse of Debye length.
        Debye_length (float): Debye length.
        D_zero (float): average diffusion constant for Salt.
        Dc (float):
        Dn (float):
        Dt (float):
        sigma (float):
        lambda_c2 (float):
        lambda_n2 (float):
    """
    def __init__(self):
        # basic attributes
        self.config_file = None
        self.num_salts = 0
        self.salts = []

        self.num_unique_ions = 0
        self.unique_ion_map = None
        self.unique_ion_names = []
        self.unique_ions = []

        # calculated attributes
        self.kappa2 = None
        self.kappa = None
        self.Debye_length = None
        self.D_zero = None         # D_zero of electrolyte: sum over salts
        self.Dc = None
        self.Dn = None
        self.Dt = None             # used for omega << k^2*Dzero
        self.sigma = None          # conductivity: was K1
        self.lambda_c2 = None
        self.lambda_n2 = None

        # calculated IVP attributes
        self.min_dist = None    # matrix with minimal distances between unique ions
        self.B_mat = None        # matrix with sum of diffusion constants for unique ion pairs, divided by kT
        self.NZ_mat = None       # matrix from outer product of number density and charge^2 for unique ion pairs
    @classmethod
    def from_yaml(cls, config_yaml: str):
        """ classmethod to enable constructing an instance from configuration file.

        Args:
            config_yaml (str): configuration file name.

        Returns:
            Electrolyte class instance.
        """
        el = cls()
        el.config_file = config_yaml
        d = load_config(el.config_file)
        el.num_salts = len(d.get("salts"))
        for n in range(el.num_salts):
            ed = d.get("salts")[n]
            salt = Salt(name=ed.get("name"), conc=ed.get("conc"))
            # salt.name = ed.get('name')
            # salt.conc = ed.get("conc")
            num_ions = len(ed.get("ions"))
            for i in range(num_ions):
                idict = ed.get("ions")[i]
                ion = Ion.from_dict(idict)
                # append by reference, therefore new Ion object in each iteration
                salt.ions.append(ion)
            # append by reference, therefore new Salt object in each iteration
            el.salts.append(salt)
            logging.info(f" salt '{salt.name}' appended to electrolyte")

        # el.update()
        return el

    def find_unique_ions(self):
        self.unique_ion_names.clear()
        for salt in self.salts:
            for ion in salt.ions:
                if ion.name not in self.unique_ion_names:
                    self.unique_ion_names.append(ion.name)
        self.num_unique_ions = len(self.unique_ion_names)
        print(f"{self.unique_ion_names}")

        self.unique_ion_map = {key: [] for key in self.unique_ion_names}

        for name in self.unique_ion_names:
            for i in range(len(self.salts)):
                for j in range(len(self.salts[i].ions)):
                    if self.salts[i].ions[j].name == name:
                        self.unique_ion_map[name].append(tuple((i, j)))

        for key, value in self.unique_ion_map.items():
            print(f"{key},   {value}")

    def assert_unique_ions(self, ion: Ion):
        """check if an ion is unique.

        Args:
            ion: instance of Ion object
        """
        assert ion.mass is not None, f"ionic mass expected, got: {ion.mass}"
        assert ion.radius is not None, f"ionic radius in pm expected, got: {ion.radius}"
        assert ion.z is not None, f"ionic charge expected, got: {ion.z}"
        assert ion.D is not None or ion.Lambda is not None, \
               f" D or Lambda expected, got: {ion.D} / {ion.Lambda}"
        assert ion.nu is None, f"nu expected to be unused (None), got: {ion.nu}"

    def fill_unique_ions(self):
        """make list of unique Ion objects from list of Salt objects.

          set  stoichiometry attribute "nu" to None
        """
        for name in self.unique_ion_map.keys():
            keyidx = list(self.unique_ion_map.keys()).index(name)
            for idx in self.unique_ion_map[name]:
                salt_idx = idx[0]
                ion_idx = idx[1]
                new_ion = copy.deepcopy(self.salts[salt_idx].ions[ion_idx])
                if new_ion.mass is not None:
                    new_ion.unidx = keyidx
                    new_ion.nu = None
                    self.unique_ions.append(new_ion)
                    logging.info(f"Ion {name} copied to list of unique ions with index {keyidx}")

    def update(self):
        self.calc_kappa()
        self.calc_D_zero()
        self.calc_Dc()
        self.calc_Dn_binary()
        self.calc_Dt_binary()
        self.calc_sigma()  # limiting conductivity value

    def calc_kappa(self):
        """calculation of kappa^2, kappa (inverse of Debije length) and Debye length.
        """
        self.kappa2 = 0.0
        factor = 1.0 / (EPS_ZW * BOLTZ_T)

        for ion in self.unique_ions:
            self.kappa2 += factor * ion.number_density * np.square(ion.z*E_CHARGE)

        self.kappa = np.sqrt(self.kappa2)  # inverse of the Debije length
        self.Debye_length = np.reciprocal(self.kappa)
        # logging.info(f" kappa2: {self.kappa2} kappa: '{self.kappa} Debye_length: {self.Debye_length}")

    def calc_D_zero(self):
        """ calculates D_zero as sum over ions: ``|z_i|*D_i over |z_i|``.
        """
        if self.salts:
            nominator = sum(np.abs(ion.z) * ion.D for salt in self.salts for ion in salt.ions)
            denominator = sum(np.abs(ion.z) for salt in self.salts for ion in salt.ions)
            self.D_zero = nominator/denominator

    def calc_sigma(self):
        """calculates limiting conductivity value of electrolyte at infinite dilution.
        """
        if self.kappa2 and self.D_zero:
            self.sigma = EPS_ZW * self.kappa2 * self.D_zero  # limiting conductivity value

    def calc_Dc(self):
        """calculates Dc as sum over ions:  ``|z_i| over |z_i|/D_i/``.
        """
        if self.salts:
            denominator = sum(np.abs(ion.z) / ion.D for salt in self.salts for ion in salt.ions)
            nominator = sum(np.abs(ion.z) for salt in self.salts for ion in salt.ions)
            self.Dc = nominator/denominator

    def calc_Dn_binary(self):
        """calculates Dn as sum over ions:  ``|z_i| over |z_i|/D_j.ne.i``.

        See: https://www.geeksforgeeks.org/python-multiply-all-cross-list-element-pairs/
             https://www.geeksforgeeks.org/python-multiply-numbers-list-3-different-ways/
             https://stackoverflow.com/questions/2853212/all-possible-permutations-of-a-set-of-lists-in-python
             https://numpy.org/doc/stable/reference/generated/numpy.outer.html
             https://numpy.org/doc/stable/reference/generated/numpy.einsum.html
        """
        if self.salts:
            z_list = [np.abs(ion.z) for salt in self.salts for ion in salt.ions]
            one_over_D_list = [1.0/ion.D for salt in self.salts for ion in salt.ions]
            out_mat = np.outer(z_list, one_over_D_list)
            np.fill_diagonal(out_mat, 0.0)
            denominator = np.sum(out_mat)
            nominator = np.sum(z_list)
            self.Dn = nominator/denominator

    def calc_Dt_binary(self):
        """calculates Dt as sum over ions:  ``|z_i| over |z_i|/D_j.ne.i``.

        """
        if self.salts:
            z_list = [ion.z for salt in self.salts for ion in salt.ions]
            z_abs_list = [np.abs(ion.z) for salt in self.salts for ion in salt.ions]
            one_over_D_list = [1.0/ion.D for salt in self.salts for ion in salt.ions]

            dpm = sum(one_over_D_list[::2]) - sum(one_over_D_list[1::2])
            nominator = np.prod(z_list) * np.square(dpm)

            out_mat = np.outer(z_abs_list, one_over_D_list)
            np.fill_diagonal(out_mat, 0.0)
            denominator = np.sum(z_abs_list) * np.sum(out_mat)
            self.Dt = nominator/denominator
            self.Dt = np.reciprocal(self.Dt)

    def calc_min_dist(self):
        if (self.min_dist is None) and (self.num_unique_ions > 0):
            self.min_dist = np.zeros((self.num_unique_ions, self.num_unique_ions))
            for first in self.unique_ions:
                for second in self.unique_ions:
                    i = first.unidx
                    j = second.unidx
                    self.min_dist[i, j] = first.radius + second.radius
        logging.info(f"matrix with minimal distances: \n{self.min_dist}")

    def calc_B_mat(self):
        if (self.B_mat is None) and (self.num_unique_ions > 0):
            self.B_mat = np.zeros((self.num_unique_ions, self.num_unique_ions))
            for first in self.unique_ions:
                for second in self.unique_ions:
                    i = first.unidx
                    j = second.unidx
                    self.B_mat[i, j] = np.reciprocal(first.fric) + np.reciprocal(second.fric)
                    # self.B_mat[i, j] = (first.D + second.D) / BOLTZ_T

    def calc_NZ_mat(self):
        if self.unique_ions[0].number_density is None:
            return None
        else:
            nda = np.array([ion.number_density for ion in self.unique_ions])
            if self.unique_ions[0].charge is None:
                return None
            else:
                cha = np.array([ion.charge for ion in self.unique_ions])
                self.NZ_mat = np.outer(nda, cha)


if __name__ == "__main__":
    from pathlib import Path
    DATADIR = Path(__file__).parent.parent.parent.parent.absolute().joinpath("ImpedanceData")
    e = Electrolyte.from_yaml(str(DATADIR / "Cell_1_KCl_1mM.yaml"))
    print(f"kappa^2: {e.kappa2} [m^2]")

    IVPDIR = Path(__file__).parent.parent.parent.parent.absolute().joinpath("ImpedanceData")
    e2 = Electrolyte.from_yaml(str(IVPDIR / "BaCl2.yaml"))
    for salt in e2.salts:
        print(f"{salt.name}")
    print(f"kappa^2: {e2.kappa2} [m^2]")

    e3 = Electrolyte.from_yaml(str(DATADIR / "NaCl_1mM.yaml"))
    for salt in e3.salts:
        print(f"{salt.name}")
    print(f"kappa^2: {e3.kappa2} [m^2]")

    """
    try:
        value = my_dict['key1']
        print("Key exists in the dictionary.")
    except KeyError:
        print("Key does not exist in the dictionary.")
    """


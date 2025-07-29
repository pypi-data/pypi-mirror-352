
from abc import ABC
from dielectric.constants import *  # imports numpy as np
from dielectric.utils.file_utils import load_config
import logging
logging.basicConfig(level="INFO")


class Cell(ABC):
    """abstract class for general electrolysis cell.

    Attributes:
        cap (float): cell capacitance
        cell constant (float): cell constant K [m^{-1}]
    """
    def __init__(self):
        self.cap = None
        self.cell_constant = None


class PlanarCell(Cell):
    """class for electrolysis cell with planar electrodes.

    Attributes:
        dist (float): electrode distance
        surface (float): electrode surface
    """
    def __init__(self, dist, surface):
        super().__init__()
        self.dist = dist
        self.surface = surface

    @classmethod
    def from_yaml(cls, config_yaml: str):
        """class method to enable constructing an instance from configuration file.

        Args:
            config_yaml (str): configuration file name.

        Returns:
            cell (Planar Cell): class instance.
        """
        d = load_config(config_yaml)
        d_cell = d.get("cell")
        cell = cls(dist=d_cell.get("dist"), surface=d_cell.get("surface"))
        cell.update()
        logging.info(f" Planar cell object created.")
        return cell

    def update(self):
        self.cap_planar()
        self.cc_planar()

    def cap_planar(self):
        """calculate planar cell capacitance = surface/dist * EPS_ZW.
        """
        if self.surface and self.dist:
            cap = (self.surface/self.dist) * EPS_ZW
            self.cap = cap

    def cc_planar(self):
        """calculate cell constant K = EPS_ZW / cap.
        """
        if self.cap:
            self.cell_constant = np.reciprocal(self.cap/EPS_ZW)


class CylindricalCell(Cell):
    """class for electrolysis cell with cylindrical electrodes.

    Attributes:
        inner_radius (float): radius of inner cell wall.
        outer_radius (float): radius of outer cell wall.
        height (float): if mounted vertically (length if horizontal)
        volume (float): volume of cell.
        surf_o (float): surface of ring-shaped bottom area of cell.
        log_ratio_radii (float): ln(outer_radius/inner_radius)
        one_over_inner_plus_one_over_outer (float): 1/R1 + 1/R2
    """
    def __init__(self, inner_radius, outer_radius, *, height=None, volume=None):
        super().__init__()
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.surf_o = self.set_surf_o()
        self.log_ratio_radii = self.set_log_ratio_radii()
        self.one_over_inner_plus_one_over_outer = self.set_sum_recipr_radii()

        self.height = height
        self.volume = volume
        self.update()

    @classmethod
    def from_yaml(cls, config_yaml: str):
        """class method to enable constructing an instance from configuration file.

        Args:
            config_yaml (str): configuration file name.

        Returns:
            cell (Cylindrical Cell): class instance.
        """
        d = load_config(config_yaml)
        d_cell = d.get("cell")
        # default value for dict.get() is None by default
        cell = cls(inner_radius=d_cell.get("inner"), outer_radius=d_cell.get("outer"),
                   height=d_cell.get("height"), volume=d_cell.get("volume"))
        # if "height" in d_cell:
        #    cell.height = d_cell.get("height")      # default value is None by default
        # if "volume" in d_cell:
        #    cell.height = d_cell.get("volume")      # default value is None by default
        # cell.update()
        logging.info(f" Cylindrical cell object created.")
        return cell

    def update(self):
        """update volume, capacitance and cell constant if cell height is known.
        """
        if not self.height and not self.volume:
            logging.warning(" Cell height and volume not specified. "
                            "Cell capacitance and cell constant will not be calculated.")
            return None
        elif self.height and not self.volume:
            self.set_volume_from_height()
            logging.info(" Cell volume will be calculated from cell height.")
        elif self.volume and not self.height:
            self.set_height_from_volume()
            logging.info(" Cell height will be calculated from cell volume.")
        elif self.height and self.volume:
            logging.warning(" Both cell height and volume specified. Volume will be used.")
            self.set_height_from_volume()

        self.set_cap_cylindrical()
        self.set_cc_cylindrical()
        return None

    def __repr__(self):
        return f"CylindricalCell(inner_radius={self.inner_radius*1e3:.3f} mm, outer_radius={self.outer_radius*1e3:.3f} mm, " \
               f"height={self.height*1e3:.3f} mm, volume={self.volume*1e6:.3f} ml, " \
               f"cc={self.cell_constant:.3f} /m, cap={self.cap*1e12:.3f} pF)"

    def set_surf_o(self):
        """calculate surface of ring-shaped bottom area of cylindrical cell.
        """
        if self.outer_radius and self.inner_radius:
            return np.pi * (np.square(self.outer_radius) - np.square(self.inner_radius))
        return None

    def set_log_ratio_radii(self):
        """calculate natural logarithm of ratio of outer and inner radius
            of cylindrical cell.

            Note: ratio always > 1, logarithm is positive.
        """
        if self.outer_radius and self.inner_radius:
            return np.log(self.outer_radius / self.inner_radius)
        return None

    def set_sum_recipr_radii(self):
        """calculate sum of reciprocals of outer and inner radius
            of cylindrical cell.
        """
        if self.outer_radius and self.inner_radius:
            return np.reciprocal(self.inner_radius) + np.reciprocal(self.outer_radius)
        return None

    def set_volume_from_height(self):
        """calculate cell volume if cell height is known.
        """
        if self.height and self.surf_o:
            self.volume = self.height * self.surf_o

    def set_height_from_volume(self):
        """calculate cell height if cell volume is known.
        """
        if self.volume and self.surf_o:
            self.height = self.volume / self.surf_o

    def set_cap_cylindrical(self):
        """calculate cylindrical cell capacitance if cell height is known.
        """
        if self.height:
            cap = 2.0 * np.pi * self.height * EPS_ZW
            cap /= self.log_ratio_radii
            self.cap = cap

    def set_cc_cylindrical(self):
        """calculate cell constant K = EPS_ZW / cap if capacitance is known.
        """
        if self.cap:
            self.cell_constant = np.reciprocal(self.cap/EPS_ZW)


class ParallelWireCell(Cell):
    """class for parallel wire electrodes as use in electro-acoustics.

    Attributes:
        dist (float): electrode distance
        radius (float): electrode wire radius
        length (float): length if mounted horizontally (height if vertical)
    """
    def __init__(self, dist, radius, length=10.0e-3):
        super().__init__()
        self.dist = dist
        self.radius = radius
        self.length = length

    @classmethod
    def from_yaml(cls, config_yaml: str):
        """class method to enable constructing an instance from configuration file.

        Args:
            config_yaml (str): configuration file name.

        Returns:
            cell (Cylindrical Cell): class instance.
        """
        d = load_config(config_yaml)
        d_cell = d.get("cell")
        cell = cls(dist=d_cell.get("dist"), radius=d_cell.get("radius"))
        if "length" in d_cell:
            cell.length = d_cell.get("length")  # default value is None by default
        cell.update()
        logging.info(f" Parallel-wire cell object created.")
        return cell

    def update(self):
        self.cap_parallel_wires()
        self.cc_parallel_wires()

    def cap_parallel_wires(self):
        """calculate parallel-wire cell capacitance.
        """
        if self.dist and self.radius and self.length:
            cap = np.pi * EPS_ZW * self.length
            arg = 0.5 * (self.dist / self.radius)
            # print(f"arg: {arg}")
            denom = arg + np.sqrt(np.square(arg) - 1)
            denom = np.log(denom)
            cap /= denom
            self.cap = cap

    def cc_parallel_wires(self):
        """calculate cell constant K = EPS_ZW / cap.
        """
        if self.cap:
            self.cell_constant = np.reciprocal(self.cap/EPS_ZW)

    def cap_parallel_wires2(self):
        """calculate parallel-wire cell capacitance (alternative formula).
        """
        cap = np.pi * EPS_ZW * self.length
        arg = 0.5 * (self.dist / self.radius)
        denom = np.arccosh(arg)
        cap /= denom
        self.cap = cap


if __name__ == "__main__":
    Cell_1 = PlanarCell(dist=1.0e-3, surface=1.0e-3)

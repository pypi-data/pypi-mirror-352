
# from dielectric.constants import *  # imports numpy as np
from dielectric.utils.file_utils import load_config


class SingleParticle:
    """class for single type of particle.

    Attributes:
            radius (float): radius of the colloidal particle (m).
            rel_zeta (float): zeta potential in kT/e units (i.e. zeta = 25 * rel_zeta mV).
            eps (float): permittivity latex.
            fi (float):  volume fraction of particles.
            hamaker (float): Hamaker constant.
            beta (array): beta value for each value of omega.
    """
    def __init__(self, radius, rel_zeta, eps, fraction=None, hamaker=None):
        self.radius = radius
        self.rel_zeta = rel_zeta
        self.eps = eps
        self.fi = fraction
        self.hamaker = hamaker
        self.beta = None

    @classmethod
    def from_dict(cls, d):
        """ classmethod to enable constructing an instance from a dictionary.
        """
        return cls(radius=d["radius"], rel_zeta=d["rel_zeta"], eps=d["eps"],
                   fraction=d["fraction"], hamaker=d.get('Hamaker', 0.0))

    def update(self):
        pass


def read_particles(config_yaml: str):
    """read information about particle species in colloid from configuration file.

    Args:
        config_yaml: configuration file with section "particles".

    Returns:
        (list): list of SingleParticle objects.
    """
    expc = load_config(config_yaml)
    part = expc['particles']        # list of dictionaries

    num_particles = len(part)
    print(f"Number of particle types: {num_particles}")
    assert(num_particles > 0)

    # make list of particles in colloid
    p_in_c = []
    [p_in_c.append(SingleParticle(p['radius'], p['rel_zeta'], p['eps'], p['fraction']))
     for p in part]

    return p_in_c


def read_particles2(config_yaml: str):
    """read information about particle species in colloid from configuration file.

    Args:
        config_yaml: configuration file with section "particles".

    Returns:
        (list): list of SingleParticle objects.
    """
    d = load_config(config_yaml)
    pdict = d.get('particles')        # list of dictionaries

    num_particles = len(pdict)
    print(f"Number of particle types: {num_particles}")
    assert(num_particles > 0)

    # make list of particles in colloid
    p_in_c = []
    [p_in_c.append(SingleParticle.from_dict(spd)) for spd in pdict]

    return p_in_c


if __name__ == "__main__":
    from pathlib import Path
    DATADIR = Path(__file__).parent.parent.parent.parent.absolute().joinpath("ImpedanceData")
    ps = read_particles(str(DATADIR / "poly.yaml"))
    print(ps[0])

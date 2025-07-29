from pathlib import Path

import polars as pl

from orca_studio.parse.charge import charge
from orca_studio.parse.enthalpy import enthalpy_eh
from orca_studio.parse.entropy_correction import entropy_correction_eh
from orca_studio.parse.fspe import fspe_eh
from orca_studio.parse.gibbs_correction import gibbs_correction_eh
from orca_studio.parse.gibbs_free_energy import gibbs_free_energy_eh
from orca_studio.parse.hessian import hessian
from orca_studio.parse.mult import mult
from orca_studio.parse.normal_modes import normal_modes
from orca_studio.parse.run_time import run_time_h
from orca_studio.parse.tda import tda
from orca_studio.parse.thermal_correction import thermal_correction_eh
from orca_studio.parse.xyz import xyz
from orca_studio.parse.zero_point_energy import zero_point_energy_eh


class OrcaOutput:
    def __init__(self, output_file: Path | str) -> None:
        self.output_file = Path(output_file)

        if not self.output_file.is_file():
            raise FileNotFoundError(
                f"ORCA output file '{self.output_file.resolve()}' not found"
            )

        self._lines = None

    @property
    def lines(self) -> list[str]:
        """Cache lines in memory"""
        if not self._lines:
            self._lines = self.output_file.read_text().splitlines()
        return self._lines

    @property
    def xyz(self) -> str:
        """Last cartesian coordinates as an XYZ string."""
        return xyz(self.lines)

    @property
    def charge(self) -> int:
        """Total charge"""
        return charge(self.lines)

    @property
    def mult(self) -> int:
        """Multiplicity"""
        return mult(self.lines)

    @property
    def tda(self) -> bool:
        """Tamm-Dancoff approximation"""
        return tda(self.lines)

    @property
    def run_time_h(self) -> float:
        """Total run time in hours"""
        return run_time_h(self.lines)

    @property
    def enthalpy_eh(self) -> float:
        """Total Enthalpy in Hartree"""
        return enthalpy_eh(self.lines)

    @property
    def entropy_correction_eh(self) -> float:
        """Entropy correction in Hartree"""
        return entropy_correction_eh(self.lines)

    @property
    def fspe_eh(self) -> float:
        """Final single point energy in Hartree"""
        return fspe_eh(self.lines)

    @property
    def gibbs_correction_eh(self) -> float:
        """Gibbs free energy minus the electronic energy in Hartree"""
        return gibbs_correction_eh(self.lines)

    @property
    def gibbs_free_energy_eh(self) -> float:
        """Gibbs free energy in Hartree"""
        return gibbs_free_energy_eh(self.lines)

    @property
    def thermal_correction_eh(self) -> float:
        """Thermal correction in Hartree"""
        return thermal_correction_eh(self.lines)

    @property
    def zero_point_energy_eh(self) -> float:
        """Zero-point energy in Hartree"""
        return zero_point_energy_eh(self.lines)

    @staticmethod
    def get_hessian(hess_file: Path | str) -> pl.DataFrame:
        lines = Path(hess_file).read_text().splitlines()
        return hessian(lines)

    @property
    def hessian(self) -> pl.DataFrame:
        """Hessian from the associated .hess file"""
        hess_file = self.output_file.with_suffix(".hess")
        if not hess_file.is_file():
            raise FileNotFoundError(f"Hessian file '{hess_file.resolve()}' not found")
        return self.get_hessian(hess_file)

    @staticmethod
    def get_normal_modes(hess_file: Path | str) -> pl.DataFrame:
        lines = Path(hess_file).read_text().splitlines()
        return normal_modes(lines)

    @property
    def normal_modes(self) -> pl.DataFrame:
        """Normal modes from the associated .hess file"""
        hess_file = self.output_file.with_suffix(".hess")
        if not hess_file.is_file():
            raise FileNotFoundError(f"Hessian file '{hess_file.resolve()}' not found")
        return self.get_normal_modes(hess_file)

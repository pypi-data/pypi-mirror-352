from xtl.chemistry2 import ureg
from xtl.chemistry2 import Q_ as Quantity
from xtl.exceptions import InvalidArgument, MissingArgument

from chempy import Substance


class Compound:

    def __init__(self, name, formula=None, type=None, **kwargs):

        self.name = name
        self.formula = formula
        self.type = type

        if self.formula:
            try:
                from pyparsing import ParseException  # installed with ChemPy
                self.chempy = Substance.from_formula(self.formula)
            except ParseException:
                self.chempy = None
        else:
            self.chempy = None

        if 'molar_mass' in kwargs:
            # Prefer user-provided value over ChemPy value
            molar_mass = kwargs['molar_mass']
            if not isinstance(molar_mass, Quantity):
                molar_mass = ureg(molar_mass)
            if molar_mass.dimensionality != '[mass] / [substance]':
                raise InvalidArgument(raiser='molar_mass', message='Dimensions must be [mass]/[substance]')
            self.molar_mass = molar_mass
        elif self.chempy:
            self.molar_mass = self.chempy.mass * ureg('g/mol')
        else:
            raise MissingArgument(arg='molar_mass', message='Either provide the molar mass or a valid formula')

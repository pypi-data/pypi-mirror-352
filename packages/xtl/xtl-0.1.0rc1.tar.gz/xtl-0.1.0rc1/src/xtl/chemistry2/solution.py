from xtl.chemistry2 import ureg
from xtl.chemistry2 import Q_ as Quantity
from xtl.chemistry2.compound import Compound
from xtl.exceptions import InvalidArgument


class Solution:

    def __init__(self, compound=None, volume='1 L', **kwargs):
        """
        :param Compound compound:
        :param str or Quantity volume:
        :param kwargs: ``amount`` or ``concentration``
        """
        self.volume = volume
        if not isinstance(self.volume, Quantity):
            self.volume = ureg(self.volume)
        self.components = {}
        if compound:
            self.add_compound(compound, **kwargs)

    def add_compound(self, compound, **kwargs):
        if not isinstance(compound, Compound):
            raise InvalidArgument(raiser='compound', message="Must be 'Compound' instance")

        concentration = kwargs.pop('concentration', None)
        amount = kwargs.pop('amount', None)

        previous_moles = ureg('0 mol')
        if compound.name in self.components:
            previous_moles = self.components[compound.name]['moles']
        self.components[compound.name] = {
            'Compound': compound
        }

        moles = ureg('0 mol')
        if concentration and amount:
            raise InvalidArgument(raiser='add_compound', message="Method can be called with either 'concentration' or "
                                                                 "'amount', but not both")
        elif concentration:
            if not isinstance(concentration, Quantity):
                concentration = ureg(concentration)

            if concentration.dimensionality == '[substance] / [length]**3':  # mol/L
                moles = (concentration * self.volume).to(ureg.mole)
            elif concentration.units == 'weight_to_volume':  # %w/v
                wt = concentration
                moles = (wt * self.volume / compound.molar_mass).to(ureg.mole)
            elif concentration.dimensionality == '[mass] / [length]**3':  # mg/mL
                moles = (concentration * self.volume / compound.molar_mass).to(ureg.mole)
            else:
                raise

        elif amount:
            if not isinstance(amount, Quantity):
                amount = ureg(amount)

            if amount.dimensionality == '[substance]':  # mol
                moles = amount.to(ureg.mole)
            elif amount.dimensionality == '[mass]':
                m = amount
                moles = (m / compound.molar_mass).to(ureg.mole)
            else:
                raise InvalidArgument(raiser='amount', message='Dimensions must be [substance] or [mass]')

        if moles.magnitude:  # moles != 0
            self.components[compound.name]['moles'] = previous_moles + moles

    def _calculate_concentrations(self):
        for name in self.components:
            component = self.components[name]
            compound = component['Compound']
            c_type = compound.type
            moles = component['moles']
            concentration = (moles / self.volume).to(ureg.molar)
            component['concentration'] = concentration

            if c_type == 'protein':  # mg/mL
                component['concentration_pretty'] = (concentration * compound.molar_mass)\
                    .to(ureg.milligram / ureg.milliliter)
            elif c_type == 'wv':  # %w/v
                component['concentration_pretty'] = (concentration * compound.molar_mass).to(ureg('weight_to_volume'))
            else:  # molar
                component['concentration_pretty'] = concentration
                if concentration < ureg('0.1 M'):
                    component['concentration_pretty'] = concentration.to(ureg.millimolar)
                if concentration < ureg('0.1 mM'):
                    component['concentration_pretty'] = concentration.to(ureg.micromolar)

    def print_composition(self, pretty=True):
        self._calculate_concentrations()
        for name in self.components:
            component = self.components[name]
            if pretty:
                concentration = component['concentration_pretty']
                print(f'{name}: {round(concentration, 3):~P}')
            else:
                concentration = component['concentration']
                print(f'{name}: {concentration}')

    def __add__(self, other):
        if not isinstance(other, Solution):
            raise TypeError(f"Cannot add instance '{type(other)}' to instance 'Solution'")

        s0, s1 = self, other
        s2 = Solution(volume=s0.volume + s1.volume)
        for s in [s0, s1]:
            for name in s.components:
                component = s.components[name]
                compound = component['Compound']
                moles = component['moles']
                s2.add_compound(compound, amount=moles)
        return s2

    def __mul__(self, v1):
        if isinstance(v1, Quantity):
            if v1.dimensionality == '[length]**3' and v1.magnitude > 0:
                # solution 0: initial
                # solution 1: portion of s0: c0=c1
                # solution 2: new solution: n2=n1 (here also v2=v1 and c2=c1)
                #  v2 is altered by addition of other solutions
                v0 = self.volume
                v2 = v1
                s2 = Solution(volume=v2)
                for name in self.components:
                    component = self.components[name]
                    n0 = component['moles']
                    n1 = n0 * v1 / v0
                    n2 = n1
                    s2.add_compound(component['Compound'], amount=n2)
                return s2
            raise TypeError()
        else:
            raise TypeError(f"Can only multiply 'Solution' with number.")

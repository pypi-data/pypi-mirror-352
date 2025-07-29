from xtl.chemistry import Q_, smart_units
from xtl.chemistry.compound import Solute
from xtl.exceptions import InvalidArgument, DimensionalityError


class Solution:

    def __init__(self, name, solutes=(), volume='1 l'):

        self.name = name.title()
        self._volume = smart_units(volume, Q_('l'))
        self._used_volume = Q_('0 l')

        self.contents = {}
        # self.contents = {
        #     'solute.id': {
        #         'concentration': <Quantity(magnitude, units)>,
        #         'moles': <Quantity (xxx, 'mole')>,
        #         'obj': <Solute (name, molar_mass)>
        #     }
        # }

        for solute, dic in solutes:
            self.add_solute(solute=solute, **dic)
        self._calculate_concentrations()

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, new_volume):
        new_volume = smart_units(new_volume, Q_('l'))
        if new_volume <= 0:
            raise InvalidArgument(raiser='volume', message=f'{new_volume}. Cannot be negative.')
        self._volume = new_volume
        self._calculate_concentrations()

    def add_solute(self, solute, amount='0 g', concentration='0 mol/l'):
        if not isinstance(solute, Solute):
            raise

        amount = Q_(amount)  # g or mol
        concentration = Q_(concentration)  # mol/l or g/l
        if amount and concentration:
            raise

        # Get the moles of the solute already present in the solution
        previous_moles = Q_('0 mol')
        if solute.id in self.contents:
            previous_moles = self.contents[solute.id]['moles']
        else:
            self.contents[solute.id] = {
                'obj': solute,
                'moles': '',
                'concentration': ''
            }

        # Calculate the moles to be added
        if amount:
            if amount.check('[substance]'):
                moles = amount
            elif amount.check('[mass]'):
                # n = m / Mr
                mass = amount
                moles = (mass / solute.molar_mass).to('mol')
            else:
                raise DimensionalityError(raiser='amount', src_units=amount.units, dst_units=Q_('mol').units)
        elif concentration:
            if concentration.check('[substance] / [length] ** 3'):  # mol/l
                # n = C * V
                moles = (concentration * self.volume).to('mol')
            elif concentration.check('[mass] / [length] ** 3'):  # g/l or %(w/v)
                # C = n / V = m / (Mr * V) => n / V = (m/V) / Mr => n = (m/V) * V / Mr
                m_over_v = concentration
                moles = (m_over_v * self.volume / solute.molar_mass).to('mol')
            else:
                raise DimensionalityError(raiser='concentration', src_units=concentration.units,
                                          dst_units=Q_('mol').units)
        else:
            raise

        # Store value
        if moles > 0:
            new_moles = moles + previous_moles
            solubility = solute.solubility
            new_concentration = (new_moles / self.volume).to(solubility.units)
            if solubility:
                if solubility < new_concentration:
                    print('Warning: Insoluble!')

            self.contents[solute.id]['moles'] = new_moles

    def add_solution(self, solute, volume, concentration):
        self.add_solute(solute=solute, concentration=concentration)
        self.volume = self.volume + smart_units(volume, Q_('l'))

    def _calculate_concentrations(self):
        for solute_id, dic in self.contents.items():
            solute = dic['obj']
            moles = dic['moles']
            compound_type = solute.type

            if compound_type is None:
                dic['concentration'] = smart_units(moles / self.volume, Q_('M'), pretty=True)
            elif compound_type == 'wv':
                dic['concentration'] = smart_units(moles * solute.molar_mass / self.volume, Q_('wv'))
            elif compound_type == 'protein':
                dic['concentration'] = smart_units(moles * solute.molar_mass / self.volume, Q_('mg / ml'))
            else:
                raise

    def get_composition(self, as_='concentration'):
        # [(Solute, concentration/moles/mass), ]
        as_types = ['concentration', 'moles', 'mass']
        if as_ not in as_types:
            raise InvalidArgument(raiser='as_', message=f'{as_}. Must be one of: {", ".join(as_types)}')

        composition = []
        for solute_id, dic in self.contents.items():
            solute = dic['obj']
            quantity = ''

            if as_ == 'concentration':
                quantity = dic['concentration']
            elif as_ == 'moles':
                quantity = dic['moles']
            elif as_ == 'mass':
                quantity = solute.get_mass(dic['moles'])

            component = (solute, quantity)
            composition.append(component)

        return composition

    def use(self, volume, strict=False):
        # Reduce the volume. Don't recalculate concentrations. Return self.
        used_volume = smart_units(volume, Q_('l'))
        if strict and used_volume > self.volume:
            raise
        self._volume -= used_volume
        self._used_volume += used_volume
        return self  # Idea: Return a solution with volume=used_volume

    @property
    def used_volume(self):
        return self._used_volume

    def dilute(self, ratio):
        # dilute 3:1 or 50%
        pass

    def __add__(self, other):
        # Idea: Instead of returning a new Solution object, consider return a MixtureSolution(Solution) object which
        #  tracks the Solutions it was created from and updates their respective self.used_volumes upon invocation of
        #  self.use(). Or maybe the Solution class could have a self.parents attribute, storing each of its ancestors
        #  and then iteratively update all of them upon self.use().

        if not isinstance(other, Solution):
            raise

        # Create new solution from the sum of the individual volumes
        s = Solution(f'{self.name} + {other.name}', solutes=(), volume=(self.volume + other.volume))

        # Add all solutes in the new solution
        for solution in [self, other]:
            for solute, moles in solution.get_composition(as_='moles'):
                s.add_solute(solute=solute, amount=moles)
        s._calculate_concentrations()

        return s

    def __iadd__(self, other):
        return self + other

    def __mul__(self, other):
        # Multiply number/Quantity with Solution to change the volume (???)
        pass

    def __imul__(self, other):
        pass

    __rmul__ = __mul__

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} ({self.name}, {self.volume:.2f}, ' \
               f'solutes: {len(self.contents)})>'


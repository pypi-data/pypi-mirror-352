from xtl import cfg
from xtl.chemistry2 import ureg, Compound, Solution
from xtl.chemistry2 import Q_ as Quantity
from xtl.exceptions import InvalidArgument


class StockSolution(Solution):

    def __init__(self, compound, solubility=None, *args, **kwargs):
        if not isinstance(compound, Compound):
            raise InvalidArgument

        self.compound = compound
        self.solubility = solubility
        self.volume_used = ureg('0 L')

        super().__init__(compound, *args, **kwargs)

        self._calculate_concentrations()

        self.concentration = self.components[self.compound.name]['concentration_pretty']

    def _is_in_mixture(self, mixture):
        if not isinstance(mixture, Solution):
            raise InvalidArgument
        if self.compound.name not in mixture.components:
            raise InvalidArgument

    def required_moles_for_mixture(self, mixture):
        self._is_in_mixture(mixture)
        return mixture.components[self.compound.name]['moles']

    def required_volume_for_mixture(self, mixture):
        self._is_in_mixture(mixture)
        moles = self.required_moles_for_mixture(mixture)
        return (moles / self.components[self.compound.name]['concentration']).to(ureg.microliter)





# class Cocktail:  # what's inside the reservoir
#
#     def __init__(self, id):
#         self.id = str(id)
#
#     def __repr__(self):
#         return f"<Cocktail('{self.id}')>"
#
#
# class Condition:  # What's inside the drop
#
#     def __init__(self):
#         pass
#
#
# class Well:
#
#     def __init__(self, id, drops, ratios=((1, 1), )):
#         self.id = str(id)
#         self._drops_no = int(drops)
#
#         # Create drops
#         drops_dict = {}
#         for i in range(0, self._drops_no):
#             drops_dict[i] = Drop(id=f'{self.id}_{i}')
#         self.drops = drops_dict
#
#         # Create cocktail
#         self.cocktail = Cocktail
#
#     def __getitem__(self, item):
#         return getattr(self, item)
#
#     def __repr__(self):
#         return f'<Well object {self.id}>'
#
#
# class Drop:
#
#     def __init__(self, id):
#         self.id = str(id)
#
#     def __repr__(self):
#         return f'<Drop object {self.id}>'
#
#
# plates = {
#     '24': {
#         'y': ['A', 'B', 'C', 'D'],
#         'x': [1, 2, 3, 4, 5, 6]
#     },
#     '48': {
#         'y': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
#         'x': [1, 2, 3, 4, 5, 6]
#     },
#     '96': {
#         'y': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
#         'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#     }
# }
#
#
# class Plate:
#
#     def __init__(self, id, wells=24, drops_per_well=1, volume=80, drop_ratio=((1, 1), ), temperature=None):
#
#         self.id = str(id)
#
#         if str(wells) not in plates:
#             raise InvalidArgument(raiser='wells', message=f'{wells}. Must be one from '
#                                                           f'{[key for key in plates]}')
#         self._wells_no = wells
#         self._wells_along_x = plates[str(self._wells_no)]['x']
#         self._wells_along_y = plates[str(self._wells_no)]['y']
#
#         if not isinstance(drops_per_well, int) or drops_per_well < 1:
#             raise InvalidArgument(raiser='wells_per_reservoir', message=f'{drops_per_well}. Must be a non-zero '
#                                                                         f'positive integer.')
#         self._drops_no = drops_per_well
#
#         if len(drop_ratio) != drops_per_well:
#             raise InvalidArgument(raiser='drop_ratio', message=f'{drop_ratio}. Must be equal to drops_per_well.')
#         for ratio in drop_ratio:
#             if not isinstance(ratio, (tuple, list)) or len(ratio) != 2:
#                 raise InvalidArgument(raiser='drop_ratio', message=f'{drop_ratio}. Must contain iterables of length 2')
#         self.drop_ratio = tuple(drop_ratio)
#
#         # Create wells
#         wells_list = []
#         for y in self._wells_along_y:
#             for x in self._wells_along_x:
#                 well = Well(id=f'{self.id}_{y}{x}', drops=self._drops_no)
#                 self.__setattr__(f'{y}{x}', well)
#                 wells_list += [well]
#         self.wells = tuple(wells_list)
#
#         # Temperature
#         temp_units = cfg['units']['temperature'].value
#         default_temp = None
#         ureg_temp_units = None
#         if temp_units == 'C':
#             default_temp = 25
#             ureg_temp_units = ureg.degC
#         elif temp_units == 'K':
#             default_temp = 298
#             ureg_temp_units = ureg.degK
#         elif temp_units == 'F':
#             default_temp = 77
#             ureg_temp_units = ureg.degF
#
#         if not temperature:
#             self.temperature = Q_(default_temp, ureg_temp_units)
#         else:
#             self.temperature = Q_(temperature, ureg_temp_units)
#
#     def __getitem__(self, item):
#         return getattr(self, item)


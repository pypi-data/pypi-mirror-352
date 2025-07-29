from xtl.chemistry import Q_, smart_units
from xtl.exceptions import InvalidArgument
from xtl.exceptions.warnings import ObjectInstantiationWarning

# from pyEQL import *
from hashlib import md5
import pubchempy as pcp
from chempy import Substance


class Compound:

    def __init__(self, name: str, molar_mass=0, formula=None, type=None, *args, **kwargs):
        self.name = name
        self.id = md5(bytes(self.name.lower(), 'utf-8')).hexdigest()
        self.formula = formula
        self._molar_mass = smart_units(molar_mass, Q_('g/mol'))

        if type in ['protein', 'wv', None]:
            self.type = type
        else:
            raise InvalidArgument

        # Calculate molar mass from formula
        if self.formula and not self._molar_mass:
            cp = Substance.from_formula(formula)
            self._molar_mass = smart_units(cp.molar_mass(), Q_('g/mol'))

        # Initialize optional attributes
        self.iupac_name = kwargs.get('iupac_name', None)
        self.cid = kwargs.get('cid', None)
        self.inchi = kwargs.get('inchi', None)
        self.inchikey = kwargs.get('inchikey', None)

    @property
    def molar_mass(self):
        return self._molar_mass

    @molar_mass.setter
    def molar_mass(self, new_mass):
        self._molar_mass = smart_units(new_mass, Q_('g/mol'))

    def get_mass(self, moles):
        moles = smart_units(moles, Q_('mol'))
        # n = m / Mr => m = n * Mr
        return moles * self.molar_mass

    @classmethod
    def from_pubchem(cls, name, cid=None, smiles=None, inchi=None, inchikey=None, **kwargs):

        # Get a list of the unique values provided (value = None if not provided)
        ids = {
            'cid': cid,
            'smiles': smiles,
            'inchi': inchi,
            'inchikey': inchikey
        }
        unique_ids = set(ids.values())

        # Get a list of the provided keys
        keys = [k for k, v in ids.items() if v in unique_ids and v is not None]

        # Search PubChem for a compound with each key, stop when a compound is found
        pcp_ = None
        for key in keys:
            try:
                pcp_ = pcp.get_compounds(ids[key], namespace=key, listkey_count=1)[0]
                break
            except pcp.BadRequestError:
                continue

        if not pcp_:
            raise

        properties = {
            'iupac_name': pcp_.iupac_name,
            'formula': pcp_.molecular_formula,
            'molar_mass': pcp_.molecular_weight,
            'cid': pcp_.cid,
            'smiles': pcp_.canonical_smiles,
            'inchi': pcp_.inchi,
            'inchikey': pcp_.inchikey
        }

        for k in kwargs.keys():
            if k in properties:
                properties.pop(k)

        return cls(name, **properties, **kwargs)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} ({self.name}, {self.molar_mass:0.2f})>'


class Solute(Compound):

    def __init__(self, name, molar_mass=0, formula=None, solubility=0, *args, **kwargs):

        # Bug: Setter cannot deal with other units. Try solubility='1 g/l'
        self._solubility = smart_units(solubility, Q_('mol/l'))
        super().__init__(name, molar_mass=molar_mass, formula=formula, *args, **kwargs)

    @property
    def solubility(self):
        return self._solubility

    @solubility.setter
    def solubility(self, new_solubility):
        self._solubility = smart_units(new_solubility, Q_('mol/l'))

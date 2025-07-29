from xtl.crystallization.components import Plate


class Condition:
    # Combine Well and Drop to generate the actual condition in the drop
    pass


class ReagentApplier:
    # Apply a reagent following a set of rules, e.g. increase in x direction
    pass


class Experiment:

    def __init__(self, id, plate_id):
        pass

    @classmethod
    def from_screen(cls, screen_name):
        pass
    
    @property
    def conditions(self):
        return [Condition()]

    def make_worksheet(self):
        pass

    def make_scoring_sheet(self):
        pass

    def save(self):
        # Pickle?
        pass

    def load(self):
        pass

    def export_conditions(self):
        pass

    def export_scores(self):
        # Tabular format that is used by PhaseDiagram
        pass



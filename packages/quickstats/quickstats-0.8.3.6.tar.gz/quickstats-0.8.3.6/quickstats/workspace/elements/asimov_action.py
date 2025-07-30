from typing import Optional, List, Literal

from pydantic import Field

from quickstats.workspace.settings import (
    ASIMOV_ALGO_ROOSTATS,
    ASIMOV_ALGO_QUICKSTATS
)
from .base_element import BaseElement

DESCRIPTIONS = {
    'name': 'Name for the Asimov dataset if it is to be created (otherwise it does not affect anything in the workspace and is only used for bookkeeping).',
    'setup': 'Initial configurations for any parameters in the workspace.',
    'action': \
"""A set of actions to be executed sequentially, separated by colons.
fit : Performing a maximum likelihood fit
reset : Reset all parameters to the states (initial values, ranges, and whether it is floating) before any actions in the current list are taken
raw : Reset all parameters to the states before any actions (including those in previous lines) are taken
fixsyst : Fix all the NPs corresponding to constraint pdfs (e.g. NPs for systematic uncertainties) to current values. Unconstrained NPs are not affected
fixall : Fix all the NPs
float : Float all the NPs that have been fixed either in "Setup" or by "fixsyst" keyword. POIs that have been fixed are not affected
genasimov : Generating Asimov dataset using the name provided with "Name" attribute. N.B. this keyword can only appear once in each action list
matchglob : Matching the global observable values to the corresponding NP ones. N.B. this keyword should always be accompanied by "reset" at the end of action list
savesnapshot : Saving a snapshot, with names provided by the "SnapshotNuis" (for nuisance parameters), "SnapshotGlob" (for global observables), "SnapshotPOI" (for POIs), and/or "SnapshotAll" (for POIs, NPs, and global observables) attributes. N.B. this keyword can only appear once in each action list
(snapshot name) : Load the snapshot with given name
""",
    'snapshot_nuis': 'Name of the nuisance parameter snapshot to be saved.',
    'snapshot_glob': 'Name of the global observable snapshot to be saved.',
    'snapshot_poi': 'Name of the POIs snapshot to be saved.',
    'snapshot_all': 'Name of the all variable snapshot to be saved.',
    'data': 'Profile to data with the given name. Use main dataset if not specified.',
    'algorithm': 'Algorithm used to generate the asimov. Choose between "RooStats" and "QuickStats".'
}

class AsimovAction(BaseElement):
    name : str = Field(alias='Name', description=DESCRIPTIONS['name'])
    setup : str = Field(default='', alias='Setup', description=DESCRIPTIONS['setup'])
    action : str = Field(default='', alias='Action', description=DESCRIPTIONS['action'])
    snapshot_nuis : Optional[str] = Field(default=None, alias='SnapshotNuis', description=DESCRIPTIONS['snapshot_nuis'])
    snapshot_glob : Optional[str] = Field(default=None, alias='SnapshotGlob', description=DESCRIPTIONS['snapshot_glob'])
    snapshot_poi : Optional[str] = Field(default=None, alias='SnapshotPOI', description=DESCRIPTIONS['snapshot_poi'])
    snapshot_all : Optional[str] = Field(default=None, alias='SnapshotAll', description=DESCRIPTIONS['snapshot_all'])
    data : Optional[str] = Field(default=None, alias='Data', description=DESCRIPTIONS['data'])
    algorithm : Literal[ASIMOV_ALGO_ROOSTATS, ASIMOV_ALGO_QUICKSTATS] = Field(default=ASIMOV_ALGO_ROOSTATS, alias='Data',
                                                                              description=DESCRIPTIONS['algorithm'])

    def compile(self):
        if not self.attached:
            raise RuntimeError(f'Asimov action (name = {self.name}, action = {self.action}) '
                               f'not attached to a workspace.')
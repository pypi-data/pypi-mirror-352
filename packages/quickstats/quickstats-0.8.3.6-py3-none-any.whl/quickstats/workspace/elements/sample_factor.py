from pydantic import Field

from .base_element import BaseElement

DESCRIPTIONS = {
    'name': 'Workspace declaration (usually in the form Name[Value]) of the factor.',
    'correlate': 'Whether to correlate this factor across categories.'
}

class SampleFactor(BaseElement):

    def compile(self):
        if not self.attached:
            raise RuntimeError(f'Sample factor "{self.name}" is not attached to a workspace.')

class NormFactor(BaseElement):
    name : str = Field(alias='Name', deescription=DESCRIPTIONS['name'])
    correlate : bool = Field(default=False, alias='Correlate', description=DESCRIPTIONS['correlate'])

    def compile(self):
        if not self.attached:
            raise RuntimeError(f'Norm factor "{self.name}" is not attached to a sample.')

class ShapeFactor(BaseElement):
    name : str = Field(alias='Name', deescription=DESCRIPTIONS['name'])
    correlate : bool = Field(default=False, alias='Correlate', description=DESCRIPTIONS['correlate'])

    def compile(self):
        if not self.attached:
            raise RuntimeError(f'Shape factor "{self.name}" is not attached to a sample.')
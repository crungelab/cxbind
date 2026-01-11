from .renderer import Renderer
from ..node import StructureType, RecordMember

class StructureTypeRenderer(Renderer[StructureType]):
    pass
    '''
    def exclude_member(self, member: RecordMember) -> bool:
        return super().exclude_node(member)
    '''
from _typeshed import Incomplete
from tqml.tqnet._base import CertainLayer as CertainLayer

class DHN(CertainLayer):
    from_classic: Incomplete
    q_part: Incomplete
    cl_part: Incomplete
    def __init__(self, in_features: int, q_part: CertainLayer, hidden_dim: list[int], from_classic) -> None: ...
    def draw_circuit(self) -> None: ...
    def forward(self, x): ...

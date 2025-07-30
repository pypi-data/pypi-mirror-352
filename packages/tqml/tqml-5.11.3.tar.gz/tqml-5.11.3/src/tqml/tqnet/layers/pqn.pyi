from _typeshed import Incomplete
from tqml.tqnet._base import QuantumLayer as QuantumLayer
from tqml.tqnet._jax_torch import JaxModule as JaxModule
from tqml.tqnet.exceptions import DimensionException as DimensionException

class PQN(QuantumLayer):
    q_layers: Incomplete
    interface_unit: Incomplete
    interface: str
    unit: Incomplete
    qnode: Incomplete
    circuit_jax: Incomplete
    weights: Incomplete
    trainable_frequency: Incomplete
    def __init__(self, in_features, n_qubits, depth, measurement_mode: str = 'None', rotation: str = 'X', entangling: str = 'strong', measure: str = 'Y', diff_method: Incomplete | None = None, qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    def extra_repr(self) -> str: ...
    def circuit(self, weights, x, measurement_basis: Incomplete | None = None): ...
    def forward(self, x): ...
    def draw_circuit(self) -> None: ...
    def get_quantum_tape(self, x, weights: Incomplete | None = None): ...

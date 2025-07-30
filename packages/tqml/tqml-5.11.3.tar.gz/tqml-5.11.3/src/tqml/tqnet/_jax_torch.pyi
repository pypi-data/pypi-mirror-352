from _typeshed import Incomplete
from torch import nn
from torch.autograd import Function

class JaxFunction(Function):
    @staticmethod
    def forward(ctx, weights, inputs, jax_function, *jax_function_args): ...
    @staticmethod
    def backward(ctx, grad_output): ...

class JaxModule(nn.Module):
    jax_function: Incomplete
    weights: Incomplete
    def __init__(self, circuit_jax, weights) -> None: ...
    def forward(self, x): ...

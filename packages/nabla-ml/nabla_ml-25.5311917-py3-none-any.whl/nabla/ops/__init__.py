# ===----------------------------------------------------------------------=== #
# Nabla 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===----------------------------------------------------------------------=== #

"""Operations module for Nabla framework."""

# Import all operations for easy access
from .binary import add, div, greater_equal, mul, power, sub
from .creation import arange, randn
from .linalg import matmul
from .reduce import reduce_sum
from .unary import (
    cast,
    cos,
    decr_batch_dim_ctr,
    incr_batch_dim_ctr,
    log,
    negate,
    relu,
    sin,
)
from .view import (
    broadcast_batch_dims,
    broadcast_to,
    reshape,
    squeeze,
    transpose,
    unsqueeze,
)

__all__ = [
    "arange",
    "randn",
    "sin",
    "cos",
    "negate",
    "cast",
    "incr_batch_dim_ctr",
    "decr_batch_dim_ctr",
    "relu",
    "log",
    "add",
    "mul",
    "sub",
    "div",
    "greater_equal",
    "power",
    "matmul",
    "transpose",
    "reshape",
    "broadcast_to",
    "squeeze",
    "unsqueeze",
    "broadcast_batch_dims",
    "reduce_sum",
]

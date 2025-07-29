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

"""Core transformations for automatic differentiation and tracing."""

from __future__ import annotations

from collections.abc import Callable

from .array import Array


class Trace:
    """A simple trace container that holds the computation graph."""

    def __init__(self, inputs: list[Array], outputs: list[Array] | None = None) -> None:
        self.inputs = inputs
        self.outputs = outputs if outputs is not None else []
        self.trace: list[Array] = []
        self._computed = False

        # Mark all inputs as traced for autodiff so the computation graph gets captured
        for inp in inputs:
            inp.traced = True

    @classmethod
    def trace_function(
        cls, fn: Callable[[list[Array]], list[Array]], inputs: list[Array]
    ) -> Trace:
        """
        Create a trace by executing a function with tracing enabled.

        This is the recommended way to create traces as it ensures proper
        tracing setup before function execution.
        """
        # Create trace instance (this marks inputs as traced)
        trace = cls(inputs)

        for inp in inputs:
            # Mark input arrays as traced
            inp.traced = True

        # Execute function with tracing enabled
        outputs = fn(inputs)
        trace.outputs = outputs if isinstance(outputs, list) else [outputs]

        for out in trace.outputs:
            # Mark output arrays as traced
            out.traced = True

        # trace.trace = trace.get_traced_nodes()

        for inp in inputs:
            # Reset traced flag for inputs after execution
            inp.traced = False

        for out in trace.outputs:
            # Mark output arrays as traced
            out.traced = False

        return trace

    def get_traced_nodes(self) -> list[Array]:
        """Get all nodes that belong to this trace in topological order."""
        if not self._computed:
            self._compute_trace()
        return self.trace

    def _compute_trace(self) -> None:
        """Compute the topological ordering of traced nodes."""
        visited: set[Array] = set()
        self.trace = []

        for output in self.outputs:
            self._dfs_visit(output, visited)

        self._computed = True

    def _dfs_visit(self, node: Array, visited: set[Array]) -> None:
        """DFS traversal to build topological ordering."""
        if node in visited:
            return

        # Visit children first (post-order)
        for arg in node.args:
            self._dfs_visit(arg, visited)

        # Add current node after visiting children
        visited.add(node)
        self.trace.append(node)

    def __str__(self) -> str:
        """Return a JAX-like string representation of the trace."""
        if not self._computed:
            self._compute_trace()

        from ..utils.formatting import format_shape_and_dtype

        # Build variable name mapping
        var_names = {}
        var_counter = 0

        # Assign names to inputs first with type annotations
        input_vars = []
        for inp in self.inputs:
            var_name = chr(ord("a") + var_counter)
            var_names[id(inp)] = var_name
            type_annotation = format_shape_and_dtype(inp)
            input_vars.append(f"{var_name}:{type_annotation}")
            var_counter += 1

        # Build the equation lines
        equations = []
        for node in self.trace:
            node_id = id(node)

            # Skip if this is an input (already named)
            if node_id in var_names:
                continue

            # Assign a variable name to this node
            var_name = chr(ord("a") + var_counter)
            var_names[node_id] = var_name
            var_counter += 1

            # Build the operation description
            if node.args:
                # Get argument variable names
                arg_vars = []
                for arg in node.args:
                    arg_id = id(arg)
                    if arg_id in var_names:
                        arg_vars.append(var_names[arg_id])
                    else:
                        # Array from external context - assign a const name
                        temp_name = f"const{len([v for v in var_names.values() if v.startswith('const')])}"
                        var_names[arg_id] = temp_name
                        arg_vars.append(temp_name)

                # Format the equation with type annotation
                op_name = node.name or "unknown"
                type_annotation = format_shape_and_dtype(node)

                if len(arg_vars) == 1:
                    equation = (
                        f"    {var_name}:{type_annotation} = {op_name} {arg_vars[0]}"
                    )
                else:
                    args_joined = " ".join(arg_vars)
                    fmt_str = f"    {var_name}:{type_annotation} = {op_name}"
                    equation = f"{fmt_str} {args_joined}"

                equations.append(equation)

        # Get output variable names
        output_vars = []
        for out in self.outputs:
            out_id = id(out)
            if out_id in var_names:
                output_vars.append(var_names[out_id])
            else:
                output_vars.append("?")

        # Format the final representation
        input_sig = f"({', '.join(input_vars)})"
        output_sig = (
            f"({', '.join(output_vars)})" if len(output_vars) > 1 else output_vars[0]
        )

        result = f"{{ lambda {input_sig} ;\n"
        result += "  let\n"
        for eq in equations:
            result += f"{eq}\n"
        result += f"  in {output_sig} }}"

        return result

    def print_trace(self) -> None:
        """Print the trace in a nice format."""
        print(self)


def pullback(
    inputs: list[Array],
    outputs: list[Array],
    cotangents: list[Array],
) -> list[Array]:
    """Compute vector-Jacobian product (reverse-mode autodiff)."""
    if len(cotangents) != len(outputs):
        raise ValueError(
            f"Cotangents length {len(cotangents)} != outputs length {len(outputs)}"
        )

    # Use provided trace or compute new one (for backward compatibility)
    trace = Trace(inputs, outputs)
    traced_nodes = trace.get_traced_nodes()

    # Step 1: Initialize cotangents for output nodes
    for output, cotangent in zip(outputs, cotangents, strict=False):
        output.cotangent = cotangent

    try:
        # Step 2: Traverse nodes in reverse topological order
        for node in reversed(traced_nodes):
            # Skip nodes without cotangents (shouldn't happen in well-formed graphs)
            if node.cotangent is None:
                continue

            # Skip input nodes (they don't have VJP rules to apply)
            if not node.args or node.vjp_rule is None:
                continue

            # Step 3: Apply VJP rule to get cotangents for arguments
            try:
                arg_cotangents = node.vjp_rule(node.args, node.cotangent, node)

                # Step 4: Accumulate cotangents for each argument
                for arg, arg_cotangent in zip(node.args, arg_cotangents, strict=False):
                    if arg.cotangent is not None:
                        # Accumulate: add new cotangent to existing one
                        from ..ops.binary import add

                        arg.cotangent = add(arg.cotangent, arg_cotangent)
                    else:
                        # First cotangent for this argument
                        arg.cotangent = arg_cotangent

                # Step 5: Clean up this node's gradient immediately after processing
                # (unless it's an input node - we need those gradients at the end)
                if node not in inputs:
                    node.cotangent = None

            except Exception as e:
                raise RuntimeError(
                    f"VJP rule failed for operation '{node.name}': {e}"
                ) from e

        # Step 5: Collect gradients for input nodes
        input_gradients = []
        for inp in inputs:
            if inp.cotangent is not None:
                input_gradients.append(inp.cotangent)
            else:
                # Input has no gradient (not used in computation)
                from ..ops.creation import zeros

                input_gradients.append(zeros(inp.shape, dtype=inp.dtype))

        return input_gradients

    finally:
        # Step 6: Cleanup - only need to clean input gradients now
        # (intermediate gradients were cleaned during processing)
        for inp in inputs:
            inp.cotangent = None


def pushfwd(
    inputs: list[Array],
    outputs: list[Array],
    tangents: list[Array],
    trace: Trace | None = None,
) -> list[Array]:
    """Compute Jacobian-vector product (forward-mode autodiff)."""
    if len(tangents) != len(inputs):
        raise ValueError(
            f"Tangents length {len(tangents)} != inputs length {len(inputs)}"
        )

    # Use provided trace or compute new one (for backward compatibility)
    if trace is None:
        trace = Trace(inputs, outputs)

    traced_nodes = trace.get_traced_nodes()

    # Step 1: Initialize tangents for input nodes
    for input_node, tangent in zip(inputs, tangents, strict=False):
        input_node.tangent = tangent

    try:
        # Step 2: Traverse nodes in forward topological order
        for node in traced_nodes:
            # Skip nodes that are inputs (they already have tangents)
            if node in inputs:
                continue

            # Skip nodes without arguments (shouldn't happen in well-formed graphs)
            if not node.args or node.jvp_rule is None:
                continue

            # Step 3: Collect tangents from arguments
            arg_tangents = []
            for arg in node.args:
                if arg.tangent is not None:
                    arg_tangents.append(arg.tangent)
                else:
                    # If an argument doesn't have a tangent, use zeros
                    from ..ops.creation import zeros

                    arg_tangents.append(
                        zeros(arg.shape, dtype=arg.dtype, device=arg.device)
                    )

            # Step 4: Apply JVP rule to get tangent for this node
            try:
                node.tangent = node.jvp_rule(node.args, arg_tangents, node)
            except Exception as e:
                raise RuntimeError(
                    f"JVP rule failed for operation '{node.name}': {e}"
                ) from e

        # Step 5: Collect tangents for output nodes
        output_tangents = []
        for out in outputs:
            if out.tangent is not None:
                output_tangents.append(out.tangent)
            else:
                # Output has no tangent (shouldn't happen in well-formed graphs)
                from ..ops.creation import zeros

                output_tangents.append(
                    zeros(out.shape, dtype=out.dtype, device=out.device)
                )

        return output_tangents

    finally:
        # Step 6: Cleanup tangents for all nodes
        # (inputs, outputs, and any intermediate nodes)
        for node in traced_nodes:
            node.tangent = None

        # Only reset traced flags if we're not in a higher-order derivative computation
        # Check if any input still needs to be traced (indicating higher-order derivatives)
        # set traced flag of inputs and outputs to false again
        for inp in inputs:
            inp.traced = False
        for out in outputs:
            out.traced = False


def xpr(
    fn: Callable[[list[Array]], list[Array]],
    args: list[Array],
) -> str:
    """
    Get a JAX-like string representation of the function's computation graph.

    Args:
        fn: Function to trace
        args: List of input Arrays to the function
    Returns:
        str: JAX-like string representation of the computation graph
    """
    try:
        # for inp in args:
        #     # Mark input arrays as traced
        #     inp.traced = True

        # Use the trace_function class method for proper tracing
        trace = Trace.trace_function(fn, args)

        # Return the string representation of the trace
        str_repr = str(trace)

        for inp in args:
            inp.traced = False
        for out in trace.outputs:
            out.traced = False

        return str_repr
    finally:
        # Clean up: reset traced flags after tracing
        pass


def detach(outputs: list[Array]) -> list[Array]:
    """
    Detach outputs from their computation graph by clearing dependencies.
    """
    for out in outputs:
        out.traced = False
        out.stage_realization = False  # Disable staged execution

    return outputs


def vjp(
    func: Callable[[list[Array]], list[Array]], inputs: list[Array]
) -> tuple[list[Array], Callable[[list[Array]], list[Array]]]:
    # Mark inputs for tracing
    for inp in inputs:
        inp.traced = True

    # Compute outputs once and create trace
    outputs = func(inputs)
    if not isinstance(outputs, list):
        outputs = [outputs]

    def vjp_fn(cotangents: list[Array]) -> list[Array]:
        if len(cotangents) != len(outputs):
            raise ValueError(
                f"Cotangents length {len(cotangents)} != outputs length {len(outputs)}"
            )

        for inp in inputs:
            # Mark input arrays as traced
            inp.traced = True

        for out in outputs:
            # Mark output arrays as traced
            out.traced = True

        gradients = pullback(inputs, outputs, cotangents)

        detach(inputs)
        detach(gradients)
        detach(outputs)

        return gradients

    for inp in inputs:
        inp.traced = False

    for out in outputs:
        out.traced = False

    return outputs, vjp_fn


def jvp(
    func: Callable[[list[Array]], list[Array]],
    inputs: list[Array],
    tangents: list[Array],
) -> tuple[list[Array], list[Array]]:
    """
    Compute Jacobian-vector product (forward-mode autodiff).

    Args:
        func: Function to differentiate
        inputs: Input arrays to the function
        tangents: Tangent vectors (directional derivatives)

    Returns:
        tuple: (outputs, output_tangents) where output_tangents are the JVP results
    """
    if len(tangents) != len(inputs):
        raise ValueError(
            f"Tangents length {len(tangents)} != inputs length {len(inputs)}"
        )

    # Mark inputs for tracing
    for inp in inputs:
        inp.traced = True

    # Compute outputs and their tangents using pushfwd
    outputs = func(inputs)

    if not isinstance(outputs, list):
        outputs = [outputs]

    # Use pushfwd to compute the output tangents
    output_tangents = pushfwd(inputs, outputs, tangents)

    detach(inputs)  # Detach inputs after computation
    detach(outputs)  # Detach outputs after computation
    detach(output_tangents)  # Detach output tangents

    return outputs, output_tangents


def vmap(
    func: Callable[[list[Array]], list[Array]],
    in_axes: list[int] | None = None,
    out_axes: list[int] | None = None,
) -> Callable[[list[Array]], list[Array]]:
    """
    Vectorize a function over its inputs.
    Args:
        func: Function to vectorize
        adapted_in_axes: Input axes to vectorize over (default: all inputs)
        adapted_out_axes: Output axes to vectorize over (default: all outputs)

    Returns:
        Callable: Vectorized function that can handle batched inputs
    """

    def vectorized_func(inputs: list[Array]) -> list[Array]:
        for inp in inputs:
            inp.traced = True

        adapted_in_axes = in_axes if in_axes is not None else [0] * len(inputs)

        if len(adapted_in_axes) != len(inputs):
            raise ValueError(
                f"Length of adapted_in_axes {len(adapted_in_axes)} does not match number of inputs {len(inputs)}"
            )

        batched_inputs = []

        for i, inp in enumerate(inputs):
            if adapted_in_axes[i] is None:
                from ..ops.view import unsqueeze

                batched_inp = unsqueeze(inp, [0])

            else:
                axis = adapted_in_axes[i]
                batched_inp = inp
                if axis != 0:
                    from ..ops.view import transpose

                    batched_inp = transpose(inp, axis, 0)

            from ..ops.unary import incr_batch_dim_ctr

            batched_inp = incr_batch_dim_ctr(batched_inp)
            batched_inputs.append(batched_inp)

        # Call the original function with batched inputs
        outputs = func(batched_inputs)

        # Ensure outputs are batched according to adapted_out_axes
        if not isinstance(outputs, list):
            outputs = [outputs]

        for out in outputs:
            # Mark output arrays as traced
            out.traced = True

        adapted_out_axes = out_axes if out_axes is not None else [0] * len(outputs)

        if len(adapted_out_axes) != len(outputs):
            raise ValueError(
                f"Length of adapted_out_axes {len(adapted_out_axes)} does not match number of inputs {len(outputs)}"
            )

        unbatched_outputs = []

        # # cleanup inputs, i.e. call decr_batch_dim_ctr on inputs that were incremented
        for i, out in enumerate(outputs):
            from ..ops.unary import decr_batch_dim_ctr

            unbatched_output = decr_batch_dim_ctr(out)
            if adapted_out_axes[i] is None:
                from ..ops.view import squeeze

                unbatched_output = squeeze(unbatched_output, [0])
            else:
                axis = adapted_out_axes[i]
                if axis != 0:
                    # Move axis 0 back to the original position
                    from ..ops.view import transpose

                    unbatched_output = transpose(unbatched_output, 0, axis)

            unbatched_outputs.append(unbatched_output)

        detach(inputs)
        detach(unbatched_outputs)

        return unbatched_outputs

    return vectorized_func


def jit(
    func: Callable[[list[Array]], list[Array]],
) -> Callable[[list[Array]], list[Array]]:
    """
    Just-in-time compile a function for performance optimization.

    Args:
        func: Function to JIT compile
    Returns:
        Callable: JIT-compiled function
    """

    def jit_func(inputs: list[Array]) -> list[Array]:
        # Mark inputs for tracing
        for inp in inputs:
            inp.traced = True
            inp.stage_realization = True  # Enable staged execution

        # Call the original function
        outputs = func(inputs)

        # Realize the outputs to compute their values
        from .graph_execution import realize_

        realize_(outputs)

        # Ensure outputs are a list
        if not isinstance(outputs, list):
            outputs = [outputs]

        # Detach inputs and outputs from the computation graph
        detach(inputs)
        detach(outputs)

        return outputs

    return jit_func

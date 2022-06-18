"""Shared helpers for different experiment flavours."""

from typing import Mapping, Sequence, Optional
from acme import types
from acme.tf import networks
from acme.tf import utils as tf2_utils
import numpy as np
import sonnet as snt


def make_policy_network(
        action_spec,
        policy_layer_sizes: Sequence[int] = (128, 128, 128),
    ) -> types.TensorTransformation:
        """Creates the networks used by the agent."""

        # Get total number of action dimensions from action spec.
        num_dimensions = np.prod(action_spec.shape, dtype=int)

        # Create the policy network.
        policy_network = snt.Sequential([
            networks.LayerNormMLP(policy_layer_sizes, activate_final=True),
            networks.NearZeroInitializedLinear(num_dimensions),
            networks.TanhToSpec(action_spec),
        ])

        return policy_network


def make_default_MAD3PGNetworks(
    action_spec: Optional[None] = None,
    policy_layer_sizes: Sequence[int] = (128, 128, 128),
    critic_layer_sizes: Sequence[int] = (256, 256, 128),
    vmin: float = -150.,
    vmax: float = 150.,
    num_atoms: int = 51,
    edge_number: int = 9,
):
    from Agents.MAD4PG.agent import MAD3PGNetworks

    # Get total number of action dimensions from action spec.
    num_dimensions = np.prod(action_spec.shape, dtype=int)

    # Create the shared observation network; here simply a state-less operation.
    observation_network = tf2_utils.batch_concat

    # Create the policy network.
    policy_network = snt.Sequential([
        networks.LayerNormMLP(policy_layer_sizes, activate_final=True),
        networks.NearZeroInitializedLinear(num_dimensions),
        networks.TanhToSpec(action_spec),
    ])

    # Create the critic network.
    critic_network = snt.Sequential([
        # The multiplexer concatenates the observations/actions.
        networks.CriticMultiplexer(),
        networks.LayerNormMLP(critic_layer_sizes, activate_final=True),
        networks.DiscreteValuedHead(vmin, vmax, num_atoms),
    ])

    return MAD3PGNetworks(
        policy_networks=[policy_network for _ in range(edge_number)],
        critic_networks=[critic_network for _ in range(edge_number)],
        observation_networks=[observation_network for _ in range(edge_number)],
    )
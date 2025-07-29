# tests/test_activations_torch.py
import pytest
import torch
import torch.nn as nn
import numpy as np
# Import specific activation classes directly from the module for testing
from rune.activations_torch import (
    OptimATorch, ParametricPolyTanhTorch, # ... and all other Torch classes
    SinhGateTorch, SoftRBFTorch # ... and all static Torch classes
)
from rune import get_activation # For testing the getter

ALL_TORCH_ACTIVATION_CLASSES = [
    OptimATorch, ParametricPolyTanhTorch, AdaptiveRationalSoftsignTorch, OptimXTemporalTorch,
    ParametricGaussianActivationTorch, LearnableFourierActivationTorch, A_ELuCTorch,
    ParametricSmoothStepTorch, AdaptiveBiHyperbolicTorch, ParametricLogishTorch, AdaptSigmoidReLUTorch,
    SinhGateTorch, SoftRBFTorch, ATanSigmoidTorch, ExpoSoftTorch, HarmonicTanhTorch, RationalSoftplusTorch,
    UnifiedSineExpTorch, SigmoidErfTorch, LogCoshGateTorch, TanhArcTorch
]

@pytest.mark.skipif(not torch_available, reason="PyTorch not installed") # Use your _TORCH_AVAILABLE flag
@pytest.mark.parametrize("activation_class", ALL_TORCH_ACTIVATION_CLASSES)
def test_torch_activation_output_properties(activation_class):
    """Tests that the PyTorch activation returns a tensor of correct shape and dtype."""
    module = activation_class()
    test_input = torch.randn(10, 5, dtype=torch.float32)
    
    try:
        output = module(test_input)
        assert output.shape == test_input.shape, f"{activation_class.__name__} changed input shape."
        assert output.dtype == test_input.dtype, f"{activation_class.__name__} changed data type."
        assert not torch.isnan(output).any(), f"{activation_class.__name__} produced NaN output."
    except Exception as e:
        pytest.fail(f"Test for {activation_class.__name__} failed during forward pass: {e}")

# Add more tests: in_model, get_activation, boundary values, gradients

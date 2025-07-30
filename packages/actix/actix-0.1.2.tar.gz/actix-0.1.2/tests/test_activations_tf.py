# tests/test_activations_tf.py
import pytest
import tensorflow as tf
import numpy as np
# Import specific activation classes directly from the module for testing
from actix.activations_tf import (
    OptimA, ParametricPolyTanh, # ... and all other TF classes
    SinhGate, SoftRBF # ... and all static TF classes
)
from actix import get_activation # For testing the getter

ALL_TF_ACTIVATION_CLASSES = [
    OptimA, ParametricPolyTanh, AdaptiveRationalSoftsign, OptimXTemporal,
    ParametricGaussianActivation, LearnableFourierActivation, A_ELuC,
    ParametricSmoothStep, AdaptiveBiHyperbolic, ParametricLogish, AdaptSigmoidReLU,
    SinhGate, SoftRBF, ATanSigmoid, ExpoSoft, HarmonicTanh, RationalSoftplus,
    UnifiedSineExp, SigmoidErf, LogCoshGate, TanhArc
]

@pytest.mark.skipif(not tf_available, reason="TensorFlow not installed") # Use your _TF_AVAILABLE flag
@pytest.mark.parametrize("activation_class", ALL_TF_ACTIVATION_CLASSES)
def test_tf_activation_output_properties(activation_class):
    """Tests that the TF activation returns a tensor of correct shape and dtype."""
    layer = activation_class()
    test_input_np = np.random.rand(10, 5).astype(np.float32)
    test_input_tf = tf.constant(test_input_np)
    
    try:
        output = layer(test_input_tf)
        assert output.shape == test_input_tf.shape, f"{activation_class.__name__} changed input shape."
        assert output.dtype == test_input_tf.dtype, f"{activation_class.__name__} changed data type."
        assert not tf.reduce_any(tf.math.is_nan(output)).numpy(), f"{activation_class.__name__} produced NaN output."
    except Exception as e:
        pytest.fail(f"Test for {activation_class.__name__} failed during forward pass: {e}")

# Add more tests: in_model, get_activation, boundary values, gradients, save/load

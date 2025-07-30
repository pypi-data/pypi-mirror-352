# actix/activations_tf.py
import tensorflow as tf
from tensorflow.keras.layers import Layer
from tensorflow.keras import activations as keras_standard_activations # For standard Keras activations like ELU

# --- Parametric Activation Functions (Keras Layers) ---

class OptimA(Layer):
    """
    OptimA: An 'Optimal Activation' function with trainable parameters.
    f(x) = alpha * tanh(beta * x) + gamma * softplus(delta * x) * sigmoid(lambda_ * x)
    """
    def __init__(self, **kwargs):
        super(OptimA, self).__init__(**kwargs)

    def build(self, input_shape):
        """Defines the trainable weights (parameters) of the activation function."""
        self.alpha = self.add_weight(name='alpha', shape=(), initializer='ones', trainable=True)
        self.beta = self.add_weight(name='beta', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.gamma = self.add_weight(name='gamma', shape=(), initializer='ones', trainable=True)
        self.delta = self.add_weight(name='delta', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.lambda_ = self.add_weight(name='lambda_param', shape=(), initializer='ones', trainable=True) # Renamed from lambda
        super(OptimA, self).build(input_shape)

    def call(self, x):
        """Defines the forward pass of the activation function."""
        term1 = self.alpha * tf.math.tanh(self.beta * x)
        term2 = self.gamma * tf.math.softplus(self.delta * x) * tf.math.sigmoid(self.lambda_ * x)
        return term1 + term2

    def get_config(self):
        """Ensures the layer can be saved and loaded."""
        config = super(OptimA, self).get_config()
        return config

class ParametricPolyTanh(Layer):
    """f(x) = alpha * tanh(beta * x^2 + gamma_ppt * x + delta_ppt)"""
    def __init__(self, **kwargs):
        super(ParametricPolyTanh, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_ppt = self.add_weight(name='alpha_ppt', shape=(), initializer='ones', trainable=True)
        self.beta_ppt = self.add_weight(name='beta_ppt', shape=(), initializer='ones', trainable=True)
        self.gamma_ppt = self.add_weight(name='gamma_ppt', shape=(), initializer='zeros', trainable=True)
        self.delta_ppt = self.add_weight(name='delta_ppt', shape=(), initializer='zeros', trainable=True)
        super(ParametricPolyTanh, self).build(input_shape)
    def call(self, x):
        return self.alpha_ppt * tf.math.tanh(self.beta_ppt * tf.square(x) + self.gamma_ppt * x + self.delta_ppt)
    def get_config(self): return super(ParametricPolyTanh, self).get_config()

class AdaptiveRationalSoftsign(Layer):
    """f(x) = (alpha * x) / (1 + |beta * x|^gamma)"""
    def __init__(self, **kwargs):
        super(AdaptiveRationalSoftsign, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_ars = self.add_weight(name='alpha_ars', shape=(), initializer='ones', trainable=True)
        self.beta_ars = self.add_weight(name='beta_ars', shape=(), initializer='ones', trainable=True)
        self.gamma_ars = self.add_weight(name='gamma_ars', shape=(), initializer=tf.keras.initializers.Constant(2.0), trainable=True)
        super(AdaptiveRationalSoftsign, self).build(input_shape)
    def call(self, x):
        return (self.alpha_ars * x) / (tf.constant(1.0, dtype=x.dtype) + tf.math.pow(tf.abs(self.beta_ars * x), self.gamma_ars))
    def get_config(self): return super(AdaptiveRationalSoftsign, self).get_config()

class OptimXTemporal(Layer):
    """f(x) = alpha * tanh(beta * x) + gamma * sigmoid(delta * x)"""
    def __init__(self, **kwargs):
        super(OptimXTemporal, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_oxt = self.add_weight(name='alpha_oxt', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.beta_oxt = self.add_weight(name='beta_oxt', shape=(), initializer='ones', trainable=True)
        self.gamma_oxt = self.add_weight(name='gamma_oxt', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.delta_oxt = self.add_weight(name='delta_oxt', shape=(), initializer='ones', trainable=True)
        super(OptimXTemporal, self).build(input_shape)
    def call(self, x):
        return self.alpha_oxt * tf.math.tanh(self.beta_oxt * x) + self.gamma_oxt * tf.math.sigmoid(self.delta_oxt * x)
    def get_config(self): return super(OptimXTemporal, self).get_config()

class ParametricGaussianActivation(Layer):
    """f(x) = alpha * x * exp(-beta * x^2)"""
    def __init__(self, **kwargs):
        super(ParametricGaussianActivation, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_pga = self.add_weight(name='alpha_pga', shape=(), initializer='ones', trainable=True)
        self.beta_pga = self.add_weight(name='beta_pga', shape=(), initializer='ones', trainable=True)
        super(ParametricGaussianActivation, self).build(input_shape)
    def call(self, x):
        return self.alpha_pga * x * tf.math.exp(-self.beta_pga * tf.square(x))
    def get_config(self): return super(ParametricGaussianActivation, self).get_config()

class LearnableFourierActivation(Layer):
    """f(x) = alpha * sin(beta * x + gamma_shift) + delta * cos(lambda_param * x + phi)"""
    def __init__(self, **kwargs):
        super(LearnableFourierActivation, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_lfa = self.add_weight(name='alpha_lfa', shape=(), initializer='ones', trainable=True)
        self.beta_lfa = self.add_weight(name='beta_lfa', shape=(), initializer='ones', trainable=True)
        self.gamma_shift_lfa = self.add_weight(name='gamma_shift_lfa', shape=(), initializer='zeros', trainable=True)
        self.delta_lfa = self.add_weight(name='delta_lfa', shape=(), initializer='ones', trainable=True)
        self.lambda_param_lfa = self.add_weight(name='lambda_param_lfa', shape=(), initializer='ones', trainable=True)
        self.phi_lfa = self.add_weight(name='phi_lfa', shape=(), initializer='zeros', trainable=True)
        super(LearnableFourierActivation, self).build(input_shape)
    def call(self, x):
        term1 = self.alpha_lfa * tf.math.sin(self.beta_lfa * x + self.gamma_shift_lfa)
        term2 = self.delta_lfa * tf.math.cos(self.lambda_param_lfa * x + self.phi_lfa)
        return term1 + term2
    def get_config(self): return super(LearnableFourierActivation, self).get_config()

class A_ELuC(Layer):
    """f(x) = alpha * ELU(beta * x) + gamma * x * sigmoid(delta * x)"""
    def __init__(self, **kwargs):
        super(A_ELuC, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_aeluc = self.add_weight(name='alpha_aeluc', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.beta_aeluc = self.add_weight(name='beta_aeluc', shape=(), initializer='ones', trainable=True)
        self.gamma_aeluc = self.add_weight(name='gamma_aeluc', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.delta_aeluc = self.add_weight(name='delta_aeluc', shape=(), initializer='ones', trainable=True)
        super(A_ELuC, self).build(input_shape)
    def call(self, x):
        term1 = self.alpha_aeluc * keras_standard_activations.elu(self.beta_aeluc * x)
        term2 = self.gamma_aeluc * x * tf.math.sigmoid(self.delta_aeluc * x)
        return term1 + term2
    def get_config(self): return super(A_ELuC, self).get_config()

class ParametricSmoothStep(Layer):
    """f(x) = alpha * sigmoid(beta_slope*(x - gamma_shift)) - alpha * sigmoid(delta_slope*(x + mu_shift))"""
    def __init__(self, **kwargs):
        super(ParametricSmoothStep, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_pss = self.add_weight(name='alpha_pss', shape=(), initializer='ones', trainable=True)
        self.beta_slope_pss = self.add_weight(name='beta_slope_pss', shape=(), initializer='ones', trainable=True)
        self.gamma_shift_pss = self.add_weight(name='gamma_shift_pss', shape=(), initializer='zeros', trainable=True)
        self.delta_slope_pss = self.add_weight(name='delta_slope_pss', shape=(), initializer='ones', trainable=True)
        self.mu_shift_pss = self.add_weight(name='mu_shift_pss', shape=(), initializer='zeros', trainable=True)
        super(ParametricSmoothStep, self).build(input_shape)
    def call(self, x):
        term1 = self.alpha_pss * tf.math.sigmoid(self.beta_slope_pss * (x - self.gamma_shift_pss))
        term2 = self.alpha_pss * tf.math.sigmoid(self.delta_slope_pss * (x + self.mu_shift_pss))
        return term1 - term2
    def get_config(self): return super(ParametricSmoothStep, self).get_config()

class AdaptiveBiHyperbolic(Layer):
    """f(x) = alpha * tanh(beta * x) + (1-alpha) * tanh^3(gamma_param * x)"""
    def __init__(self, **kwargs):
        super(AdaptiveBiHyperbolic, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_abh = self.add_weight(name='alpha_abh', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.beta_abh = self.add_weight(name='beta_abh', shape=(), initializer='ones', trainable=True)
        self.gamma_param_abh = self.add_weight(name='gamma_param_abh', shape=(), initializer='ones', trainable=True)
        super(AdaptiveBiHyperbolic, self).build(input_shape)
    def call(self, x):
        term1 = self.alpha_abh * tf.math.tanh(self.beta_abh * x)
        term2 = (tf.constant(1.0, dtype=x.dtype) - self.alpha_abh) * tf.math.pow(tf.math.tanh(self.gamma_param_abh * x), 3)
        return term1 + term2
    def get_config(self): return super(AdaptiveBiHyperbolic, self).get_config()

class ParametricLogish(Layer):
    """f(x) = alpha * x * sigmoid(beta * x)"""
    def __init__(self, **kwargs):
        super(ParametricLogish, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_pl = self.add_weight(name='alpha_pl', shape=(), initializer='ones', trainable=True)
        self.beta_pl = self.add_weight(name='beta_pl', shape=(), initializer='ones', trainable=True)
        super(ParametricLogish, self).build(input_shape)
    def call(self, x):
        return self.alpha_pl * x * tf.math.sigmoid(self.beta_pl * x)
    def get_config(self): return super(ParametricLogish, self).get_config()

class AdaptSigmoidReLU(Layer):
    """f(x) = alpha * x * sigmoid(beta * x) + gamma_param * ReLU(delta * x)"""
    def __init__(self, **kwargs):
        super(AdaptSigmoidReLU, self).__init__(**kwargs)
    def build(self, input_shape):
        self.alpha_asr = self.add_weight(name='alpha_asr', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.beta_asr = self.add_weight(name='beta_asr', shape=(), initializer='ones', trainable=True)
        self.gamma_param_asr = self.add_weight(name='gamma_param_asr', shape=(), initializer=tf.keras.initializers.Constant(0.5), trainable=True)
        self.delta_asr = self.add_weight(name='delta_asr', shape=(), initializer='ones', trainable=True)
        super(AdaptSigmoidReLU, self).build(input_shape)
    def call(self, x):
        term1 = self.alpha_asr * x * tf.math.sigmoid(self.beta_asr * x)
        term2 = self.gamma_param_asr * keras_standard_activations.relu(self.delta_asr * x)
        return term1 + term2
    def get_config(self): return super(AdaptSigmoidReLU, self).get_config()

# --- Static Activation Functions (Keras Layers for consistency) ---
# These do not have trainable parameters but are wrapped as Layers for uniform usage.

class SinhGate(Layer):
    """f(x) = x * sinh(x)"""
    def __init__(self, **kwargs): super(SinhGate, self).__init__(**kwargs)
    def call(self, x): return x * tf.math.sinh(x)
    def get_config(self): return super(SinhGate, self).get_config()

class SoftRBF(Layer):
    """f(x) = x * exp(-x^2)"""
    def __init__(self, **kwargs): super(SoftRBF, self).__init__(**kwargs)
    def call(self, x): return x * tf.math.exp(-tf.square(x))
    def get_config(self): return super(SoftRBF, self).get_config()

class ATanSigmoid(Layer):
    """f(x) = arctan(x) * sigmoid(x)"""
    def __init__(self, **kwargs): super(ATanSigmoid, self).__init__(**kwargs)
    def call(self, x): return tf.math.atan(x) * tf.math.sigmoid(x)
    def get_config(self): return super(ATanSigmoid, self).get_config()

class ExpoSoft(Layer):
    """f(x) = softsign(x) * exp(-|x|)"""
    def __init__(self, **kwargs): super(ExpoSoft, self).__init__(**kwargs)
    def call(self, x): return keras_standard_activations.softsign(x) * tf.math.exp(-tf.abs(x))
    def get_config(self): return super(ExpoSoft, self).get_config()

class HarmonicTanh(Layer):
    """f(x) = tanh(x) + sin(x)"""
    def __init__(self, **kwargs): super(HarmonicTanh, self).__init__(**kwargs)
    def call(self, x): return tf.math.tanh(x) + tf.math.sin(x)
    def get_config(self): return super(HarmonicTanh, self).get_config()

class RationalSoftplus(Layer):
    """f(x) = (x * sigmoid(x)) / (0.5 + x * sigmoid(x))"""
    def __init__(self, **kwargs): super(RationalSoftplus, self).__init__(**kwargs)
    def call(self, x):
        swish_x = x * tf.math.sigmoid(x)
        # Add epsilon for numerical stability, especially if the denominator can be close to zero.
        return swish_x / (tf.constant(0.5, dtype=x.dtype) + swish_x + tf.keras.backend.epsilon())
    def get_config(self): return super(RationalSoftplus, self).get_config()

class UnifiedSineExp(Layer):
    """f(x) = x * sin(exp(-x^2))"""
    def __init__(self, **kwargs): super(UnifiedSineExp, self).__init__(**kwargs)
    def call(self, x): return x * tf.math.sin(tf.math.exp(-tf.square(x)))
    def get_config(self): return super(UnifiedSineExp, self).get_config()

class SigmoidErf(Layer):
    """f(x) = sigmoid(x) * erf(x)"""
    def __init__(self, **kwargs): super(SigmoidErf, self).__init__(**kwargs)
    def call(self, x): return tf.math.sigmoid(x) * tf.math.erf(x)
    def get_config(self): return super(SigmoidErf, self).get_config()

class LogCoshGate(Layer):
    """f(x) = x * log(cosh(x))"""
    def __init__(self, **kwargs): super(LogCoshGate, self).__init__(**kwargs)
    def call(self, x):
        # log(cosh(x)) is also known as the logcosh loss function base. Add epsilon for stability.
        return x * tf.math.log(tf.math.cosh(x) + tf.keras.backend.epsilon())
    def get_config(self): return super(LogCoshGate, self).get_config()

class TanhArc(Layer):
    """f(x) = tanh(x) * arctan(x)"""
    def __init__(self, **kwargs): super(TanhArc, self).__init__(**kwargs)
    def call(self, x): return tf.math.tanh(x) * tf.math.atan(x)
    def get_config(self): return super(TanhArc, self).get_config()

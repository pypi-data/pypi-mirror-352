# actix/activations_torch.py
import torch
import torch.nn as nn
import torch.nn.functional as F

# --- Parametric Activation Functions (PyTorch Modules) ---

class OptimATorch(nn.Module):
    """
    OptimA: An 'Optimal Activation' function with trainable parameters for PyTorch.
    f(x) = alpha * tanh(beta * x) + gamma * softplus(delta * x) * sigmoid(lambda_ * x)
    """
    def __init__(self):
        super(OptimATorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.full((1,), 0.5))
        self.gamma_param = nn.Parameter(torch.ones(1)) # Renamed to avoid confusion with other gamma
        self.delta = nn.Parameter(torch.full((1,), 0.5))
        self.lambda_param = nn.Parameter(torch.ones(1)) # lambda is a keyword

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        term1 = self.alpha * torch.tanh(self.beta * x)
        term2 = self.gamma_param * F.softplus(self.delta * x) * torch.sigmoid(self.lambda_param * x)
        return term1 + term2

class ParametricPolyTanhTorch(nn.Module):
    """f(x) = alpha * tanh(beta * x^2 + gamma * x + delta)"""
    def __init__(self):
        super(ParametricPolyTanhTorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma = nn.Parameter(torch.zeros(1))
        self.delta_param = nn.Parameter(torch.zeros(1)) # Renamed to avoid confusion
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.alpha * torch.tanh(self.beta * torch.square(x) + self.gamma * x + self.delta_param)

class AdaptiveRationalSoftsignTorch(nn.Module):
    """f(x) = (alpha * x) / (1 + |beta * x|^gamma)"""
    def __init__(self):
        super(AdaptiveRationalSoftsignTorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma_param = nn.Parameter(torch.full((1,), 2.0)) # Renamed
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return (self.alpha * x) / (1.0 + torch.pow(torch.abs(self.beta * x), self.gamma_param))

class OptimXTemporalTorch(nn.Module):
    """f(x) = alpha * tanh(beta * x) + gamma * sigmoid(delta * x)"""
    def __init__(self):
        super(OptimXTemporalTorch, self).__init__()
        self.alpha = nn.Parameter(torch.full((1,), 0.5))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma_param = nn.Parameter(torch.full((1,), 0.5)) # Renamed
        self.delta = nn.Parameter(torch.ones(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.alpha * torch.tanh(self.beta * x) + self.gamma_param * torch.sigmoid(self.delta * x)

class ParametricGaussianActivationTorch(nn.Module):
    """f(x) = alpha * x * exp(-beta * x^2)"""
    def __init__(self):
        super(ParametricGaussianActivationTorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.ones(1)) # Beta should be > 0; consider constraints if necessary
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.alpha * x * torch.exp(-self.beta * torch.square(x))

class LearnableFourierActivationTorch(nn.Module):
    """f(x) = alpha * sin(beta * x + gamma_shift) + delta * cos(lambda_param * x + phi)"""
    def __init__(self):
        super(LearnableFourierActivationTorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma_shift = nn.Parameter(torch.zeros(1))
        self.delta_param = nn.Parameter(torch.ones(1)) # Renamed
        self.lambda_param = nn.Parameter(torch.ones(1))
        self.phi = nn.Parameter(torch.zeros(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        term1 = self.alpha * torch.sin(self.beta * x + self.gamma_shift)
        term2 = self.delta_param * torch.cos(self.lambda_param * x + self.phi)
        return term1 + term2

class A_ELuCTorch(nn.Module):
    """f(x) = alpha * ELU(beta * x) + gamma * x * sigmoid(delta * x)"""
    def __init__(self):
        super(A_ELuCTorch, self).__init__()
        self.alpha = nn.Parameter(torch.full((1,), 0.5))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma_param = nn.Parameter(torch.full((1,), 0.5)) # Renamed
        self.delta = nn.Parameter(torch.ones(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        term1 = self.alpha * F.elu(self.beta * x)
        term2 = self.gamma_param * x * torch.sigmoid(self.delta * x)
        return term1 + term2

class ParametricSmoothStepTorch(nn.Module):
    """f(x) = alpha * sigmoid(beta_slope*(x - gamma_shift)) - alpha * sigmoid(delta_slope_param*(x + mu_shift))"""
    def __init__(self):
        super(ParametricSmoothStepTorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta_slope = nn.Parameter(torch.ones(1))
        self.gamma_shift = nn.Parameter(torch.zeros(1))
        self.delta_slope_param = nn.Parameter(torch.ones(1))
        self.mu_shift = nn.Parameter(torch.zeros(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        term1 = self.alpha * torch.sigmoid(self.beta_slope * (x - self.gamma_shift))
        term2 = self.alpha * torch.sigmoid(self.delta_slope_param * (x + self.mu_shift))
        return term1 - term2

class AdaptiveBiHyperbolicTorch(nn.Module):
    """f(x) = alpha * tanh(beta * x) + (1-alpha) * tanh^3(gamma_param * x)"""
    def __init__(self):
        super(AdaptiveBiHyperbolicTorch, self).__init__()
        self.alpha = nn.Parameter(torch.full((1,), 0.5))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma_param = nn.Parameter(torch.ones(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        term1 = self.alpha * torch.tanh(self.beta * x)
        term2 = (1.0 - self.alpha) * torch.pow(torch.tanh(self.gamma_param * x), 3)
        return term1 + term2

class ParametricLogishTorch(nn.Module):
    """f(x) = alpha * x * sigmoid(beta * x)"""
    def __init__(self):
        super(ParametricLogishTorch, self).__init__()
        self.alpha = nn.Parameter(torch.ones(1))
        self.beta = nn.Parameter(torch.ones(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.alpha * x * torch.sigmoid(self.beta * x)

class AdaptSigmoidReLUTorch(nn.Module):
    """f(x) = alpha * x * sigmoid(beta * x) + gamma_param * ReLU(delta * x)"""
    def __init__(self):
        super(AdaptSigmoidReLUTorch, self).__init__()
        self.alpha = nn.Parameter(torch.full((1,), 0.5))
        self.beta = nn.Parameter(torch.ones(1))
        self.gamma_param = nn.Parameter(torch.full((1,), 0.5))
        self.delta = nn.Parameter(torch.ones(1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        term1 = self.alpha * x * torch.sigmoid(self.beta * x)
        term2 = self.gamma_param * F.relu(self.delta * x)
        return term1 + term2


# --- Static Activation Functions (PyTorch Modules for consistency) ---

class SinhGateTorch(nn.Module):
    """f(x) = x * sinh(x)"""
    def __init__(self): super(SinhGateTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return x * torch.sinh(x)

class SoftRBFTorch(nn.Module):
    """f(x) = x * exp(-x^2)"""
    def __init__(self): super(SoftRBFTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return x * torch.exp(-torch.square(x))

class ATanSigmoidTorch(nn.Module):
    """f(x) = arctan(x) * sigmoid(x)"""
    def __init__(self): super(ATanSigmoidTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return torch.atan(x) * torch.sigmoid(x)

class ExpoSoftTorch(nn.Module):
    """f(x) = softsign(x) * exp(-|x|)"""
    def __init__(self): super(ExpoSoftTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return F.softsign(x) * torch.exp(-torch.abs(x))

class HarmonicTanhTorch(nn.Module):
    """f(x) = tanh(x) + sin(x)"""
    def __init__(self): super(HarmonicTanhTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return torch.tanh(x) + torch.sin(x)

class RationalSoftplusTorch(nn.Module):
    """f(x) = (x * sigmoid(x)) / (0.5 + x * sigmoid(x))"""
    def __init__(self): super(RationalSoftplusTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        swish_x = x * torch.sigmoid(x)
        return swish_x / (0.5 + swish_x + 1e-7) # Added epsilon for numerical stability

class UnifiedSineExpTorch(nn.Module):
    """f(x) = x * sin(exp(-x^2))"""
    def __init__(self): super(UnifiedSineExpTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return x * torch.sin(torch.exp(-torch.square(x)))

class SigmoidErfTorch(nn.Module):
    """f(x) = sigmoid(x) * erf(x)"""
    def __init__(self): super(SigmoidErfTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return torch.sigmoid(x) * torch.erf(x)

class LogCoshGateTorch(nn.Module):
    """f(x) = x * log(cosh(x))"""
    def __init__(self): super(LogCoshGateTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Add epsilon for numerical stability as log(1) (cosh(0)) is 0, and log can be sensitive near 0.
        return x * torch.log(torch.cosh(x) + 1e-7)

class TanhArcTorch(nn.Module):
    """f(x) = tanh(x) * arctan(x)"""
    def __init__(self): super(TanhArcTorch, self).__init__()
    def forward(self, x: torch.Tensor) -> torch.Tensor: return torch.tanh(x) * torch.atan(x)

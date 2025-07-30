# Actix Functions

[![PyPI version](https://badge.fury.io/py/actix.svg)](https://badge.fury.io/py/actix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other badges if needed (CI/CD, test coverage, etc.) -->

`actix` is a Python package providing a collection of novel and experimental activation functions for deep learning models, implemented for both TensorFlow/Keras and PyTorch. Many of these are custom-designed and aim to offer improved performance or interesting properties compared to standard activations.

## Features

*   **Dual Framework Support:** Seamless integration with TensorFlow (Keras) and PyTorch.
*   **Parametric Activations:** Functions with trainable parameters that adapt during training.
*   **Static Activations:** Novel non-parametric functions.
*   **Easy to Use:** Simple API to get and use activation functions.
*   **Growing Collection:** We plan to continuously add and evaluate new activation functions.

## Implemented Activation Functions

Below is a list of some of the activation functions included in this package. For the full list and their mathematical formulas, please refer to the source code or future documentation.

**Parametric:**
*   `OptimA`
*   `ParametricPolyTanh`
*   `AdaptiveRationalSoftsign`
*   `OptimXTemporal`
*   `ParametricGaussianActivation`
*   `LearnableFourierActivation`
*   `A_ELuC` (Adaptive Exponential Linear Combination)
*   `ParametricSmoothStep`
*   `AdaptiveBiHyperbolic`
*   `ParametricLogish` (Parametric Swish/SiLU)
*   `AdaptSigmoidReLU`

**Static:**
*   `SinhGate`
*   `SoftRBF`
*   `ATanSigmoid`
*   `ExpoSoft`
*   `HarmonicTanh`
*   `RationalSoftplus`
*   `UnifiedSineExp`
*   `SigmoidErf`
*   `LogCoshGate`
*   `TanhArc`

## Performance Highlights

The `actix` activation functions have been benchmarked on standard datasets against common activations. Below are some highlights. Note that performance can vary based on model architecture, hyperparameters, and random seeds. These results are intended to showcase the potential of `actix` functions.

The benchmarks were run using a standard CNN architecture for CIFAR-10 and a simple MLP for California Housing, each for 5 different random seeds.

**Key:**
*   **Acc (↑):** Accuracy (higher is better)
*   **MSE (↓):** Mean Squared Error (lower is better)

| Dataset            | Metric    | LR   | Top `actix` Activation(s) | `actix` Mean Score | Best Standard Activation | Standard Mean Score |
| :----------------- | :-------- | :--- | :------------------------ | :----------------- | :----------------------- | :------------------ |
| **CIFAR-10**       | Acc (↑)   | 1e-3 | `ParametricLogish`        | 0.7848             | `gelu` / `swish`         | 0.7852              |
|                    |           |      | `A_ELuC`                  | 0.7842             |                          |                     |
|                    |           |      | `OptimA`                  | 0.7816             |                          |                     |
| **CIFAR-10**       | Acc (↑)   | 1e-2 | `OptimA`                  | 0.7668             | `swish`                  | 0.7632              |
|                    |           |      | `A_ELuC`                  | 0.7641             | `gelu`                   | 0.7618              |
| **California Housing** | MSE (↓)   | 1e-3 | `ParametricSmoothStep`    | 0.3043             | `mish`                   | 0.4121              |
|                    |           |      | `OptimXTemporal`          | 0.3172             | `relu`                   | 0.5056              |
| **California Housing** | MSE (↓)   | 1e-2 | `OptimXTemporal`          | 0.3019             | `relu`                   | 0.3919              |
|                    |           |      | `ATanSigmoid`             | 0.3044             | `mish`                   | 0.4074              |

**Observations:**

*   On **CIFAR-10 (LR 1e-3)**, several `actix` functions (`ParametricLogish`, `A_ELuC`, `OptimA`) performed competitively with top standard activations like `gelu` and `swish`.
*   On **CIFAR-10 (LR 1e-2)**, `OptimA` and `A_ELuC` slightly outperformed standard activations, though overall accuracy was lower for all functions compared to LR 1e-3, suggesting 1e-2 might be too high for this task/architecture.
*   On **California Housing (LR 1e-3)**, `ParametricSmoothStep` and `OptimXTemporal` showed significantly better (lower) MSE compared to standard activations.
*   On **California Housing (LR 1e-2)**, `OptimXTemporal` and `ATanSigmoid` also demonstrated superior performance over standard activations, with `OptimXTemporal` achieving the best MSE across both LRs for this dataset.

It's important to note that some `actix` functions (e.g., `ParametricPolyTanh`, `SinhGate`, `LogCoshGate` on CIFAR-10, or `SinhGate`, `LogCoshGate` on Housing) did not converge well or resulted in errors (NaNs for Housing) under these specific test conditions. This highlights the experimental nature of some activations and the importance of hyperparameter tuning (especially the learning rate) when trying new activation functions.

For more detailed results, please refer to the [full benchmark logs/data (link to be added if you host them)].

## Installation

You can install `actix` via pip:

```bash
pip install actix
```

The package will automatically detect if TensorFlow or PyTorch (or both) are installed. The corresponding activation functions will be made available. To install with specific framework support:
```bash
pip install actix[tf]    # For TensorFlow only
pip install actix[torch] # For PyTorch only
pip install actix[tf,torch] # For both
```


## Usage

### TensorFlow / Keras

```python
import tensorflow as tf
# Import directly (recommended for custom layers)
from actix import OptimA, ATanSigmoid
# Or use the getter function
from actix import get_activation

# Option 1: Direct class instantiation
model_tf_direct = tf.keras.Sequential([
    tf.keras.layers.Dense(128, input_shape=(784,)),
    OptimA(), # Custom Keras Layer
    tf.keras.layers.Dense(64),
    ATanSigmoid(), # Custom Keras Layer for static activation
    tf.keras.layers.Dense(10, activation='softmax')
])
model_tf_direct.summary()

# Option 2: Using the get_activation function
optima_layer_tf = get_activation('OptimA', framework='tensorflow')
atan_sigmoid_layer_tf = get_activation('ATanSigmoid', framework='tf')
# For standard Keras activations through the getter:
# relu_tf = get_activation('relu', framework='tf')

model_tf_getter = tf.keras.Sequential([
    tf.keras.layers.Dense(128, input_shape=(784,)),
    optima_layer_tf,
    tf.keras.layers.Dense(64),
    atan_sigmoid_layer_tf,
    tf.keras.layers.Dense(10, activation='softmax')
])
model_tf_getter.summary()

# Compile and train (example)
# (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
# x_train = x_train.reshape(-1, 784).astype('float32') / 255.0
# y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
# model_tf_direct.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
# model_tf_direct.fit(x_train[:100], y_train[:100], epochs=1)
```

### PyTorch

```python
import torch
import torch.nn as nn
# Import directly (recommended for custom modules)
# Note: PyTorch versions might have 'Torch' suffix if TensorFlow version with same name exists
from actix import OptimATorch, ATanSigmoidTorch
# Or use the getter function
from actix import get_activation

# Option 1: Direct class instantiation
class MyModelTorchDirect(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.act1 = OptimATorch() # Custom nn.Module
        self.fc2 = nn.Linear(128, 64)
        self.act2 = ATanSigmoidTorch() # Custom nn.Module for static activation
        self.fc3 = nn.Linear(64, 10)
    def forward(self, x):
        x = self.act1(self.fc1(x.view(-1, 784)))
        x = self.act2(self.fc2(x))
        return self.fc3(x)

model_torch_direct = MyModelTorchDirect()
print(model_torch_direct)

# Option 2: Using the get_activation function
optima_module_torch = get_activation('OptimA', framework='pytorch')
atan_sigmoid_module_torch = get_activation('ATanSigmoid', framework='torch')
# For standard PyTorch activations through the getter:
# relu_torch = get_activation('ReLU', framework='pytorch') # or 'relu'

class MyModelTorchGetter(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.act1 = optima_module_torch
        self.fc2 = nn.Linear(128, 64)
        self.act2 = atan_sigmoid_module_torch
        self.fc3 = nn.Linear(64, 10)
    def forward(self, x):
        x = self.act1(self.fc1(x.view(-1, 784)))
        x = self.act2(self.fc2(x))
        return self.fc3(x)

model_torch_getter = MyModelTorchGetter()
print(model_torch_getter)

# Compile and train (example)
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model_torch_direct.parameters())
# dummy_input = torch.randn(2, 784)
# labels = torch.randint(0, 10, (2,))
# output = model_torch_direct(dummy_input)
# loss = criterion(output, labels)
# loss.backward()
# optimizer.step()
```

## Dependencies
*   Python 3.7+
*   NumPy (>=1.19)
*   TensorFlow (>=2.4, optional, for TF activations)
*   PyTorch (>=1.8, optional, for PyTorch activations)

## Contributing
Contributions are welcome! If you have an idea for a new activation function, find a bug, or want to improve documentation, please feel free to:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Add tests for your changes.
5.  Ensure all tests pass (`pytest`).
6.  Commit your changes (`git commit -m 'Add some feature'`).
7.  Push to the branch (`git push origin feature/your-feature-name`).
8.  Open a Pull Request.

Please ensure your code adheres to common Python coding standards (e.g., PEP8/Black, Flake8).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
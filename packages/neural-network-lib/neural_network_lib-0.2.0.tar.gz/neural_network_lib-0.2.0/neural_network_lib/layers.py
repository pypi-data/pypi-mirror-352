import cupy as cp
from cupy.lib.stride_tricks import as_strided

from neural_network_lib.activations import Softmax


class LayerWithParameters:
    def __init__(self, weights_shape, biases_shape, decay_rate=0.9, epsilon=1e-8):
        self.decay_rate = decay_rate
        self.epsilon = epsilon
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.weights = None
        self.biases = None
        self.squared_grad_weights = cp.zeros(weights_shape)
        self.squared_grad_biases = cp.zeros(biases_shape)
        self.m_weights = cp.zeros(weights_shape)
        self.v_weights = cp.zeros(weights_shape)
        self.m_biases = cp.zeros(biases_shape)
        self.v_biases = cp.zeros(biases_shape)
        self.grad_weights = None
        self.grad_biases = None
        self.t = 1

    def update_weights(self, learning_rate=0.001, optimizer="Adam", weight_decay=0.0001):
        clip_value = 5
        norm_weights = cp.sqrt(cp.sum(self.grad_weights ** 2))
        norm_biases = cp.sqrt(cp.sum(self.grad_biases ** 2))
        if norm_weights > clip_value:
            self.grad_weights = self.grad_weights * clip_value / norm_weights
        if norm_biases > clip_value:
            self.grad_biases = self.grad_biases * clip_value / norm_biases
        if optimizer == "RMSProp":
            self.squared_grad_weights = self.decay_rate * self.squared_grad_weights + (1 - self.decay_rate) * (
                    self.grad_weights ** 2)
            self.squared_grad_biases = self.decay_rate * self.squared_grad_biases + (1 - self.decay_rate) * (
                    self.grad_biases ** 2)
            self.weights -= learning_rate * self.grad_weights / (cp.sqrt(self.squared_grad_weights) + self.epsilon)
            self.biases -= learning_rate * self.grad_biases / (cp.sqrt(self.squared_grad_biases) + self.epsilon)
        elif optimizer == "AdaGrad":
            self.squared_grad_weights += self.grad_weights ** 2
            self.squared_grad_biases += self.grad_biases ** 2
            self.weights -= learning_rate * self.grad_weights / (cp.sqrt(self.squared_grad_weights) + self.epsilon)
            self.biases -= learning_rate * self.grad_biases / (cp.sqrt(self.squared_grad_biases) + self.epsilon)
        elif optimizer == "Adam":
            self.grad_weights = self.grad_weights + weight_decay * self.weights
            self.grad_biases = self.grad_biases + weight_decay * self.biases
            self.m_weights = self.beta1 * self.m_weights + (1 - self.beta1) * self.grad_weights
            self.v_weights = self.beta2 * self.v_weights + (1 - self.beta2) * (self.grad_weights ** 2)
            self.m_biases = self.beta1 * self.m_biases + (1 - self.beta1) * self.grad_biases
            self.v_biases = self.beta2 * self.v_biases + (1 - self.beta2) * (self.grad_biases ** 2)
            m_weights_hat = self.m_weights / (1 - self.beta1 ** self.t)
            v_weights_hat = self.v_weights / (1 - self.beta2 ** self.t)
            m_biases_hat = self.m_biases / (1 - self.beta1 ** self.t)
            v_biases_hat = self.v_biases / (1 - self.beta2 ** self.t)
            self.weights -= learning_rate * m_weights_hat / (cp.sqrt(v_weights_hat) + self.epsilon)
            self.biases -= learning_rate * m_biases_hat / (cp.sqrt(v_biases_hat) + self.epsilon)
            self.t += 1
        elif optimizer == "AdaDelta":
            self.squared_grad_weights = self.decay_rate * self.squared_grad_weights + (1 - self.decay_rate) * (
                    self.grad_weights ** 2)
            self.squared_grad_biases = self.decay_rate * self.squared_grad_biases + (1 - self.decay_rate) * (
                    self.grad_biases ** 2)
            update_weights = -self.grad_weights * (
                    cp.sqrt(self.m_weights + self.epsilon) / cp.sqrt(self.squared_grad_weights + self.epsilon))
            update_biases = -self.grad_biases * (
                    cp.sqrt(self.m_biases + self.epsilon) / cp.sqrt(self.squared_grad_biases + self.epsilon))
            self.m_weights = self.decay_rate * self.m_weights + (1 - self.decay_rate) * (update_weights ** 2)
            self.m_biases = self.decay_rate * self.m_biases + (1 - self.decay_rate) * (update_biases ** 2)
            self.weights += update_weights
            self.biases += update_biases
        elif optimizer == "SGD":
            self.weights -= learning_rate * self.grad_weights
            self.biases -= learning_rate * self.grad_biases
        self.grad_weights = None
        self.grad_biases = None


class DenseLayer(LayerWithParameters):
    def __init__(self, input_size, output_size, activation_func, weights_initializer='he',
                 biases_initializer='uniform', learning_rate=0.001, decay_rate=0.9, epsilon=1e-8):
        super().__init__(weights_shape=(input_size, output_size), biases_shape=(1, output_size),
                         decay_rate=decay_rate, epsilon=epsilon)
        self.activation_func = activation_func
        self.learning_rate = learning_rate
        if weights_initializer == 'random':
            self.weights = cp.random.randn(input_size, output_size) * 0.01
        elif weights_initializer == 'xavier':
            self.weights = cp.random.randn(input_size, output_size) * cp.sqrt(1 / input_size)
        elif weights_initializer == 'he':
            self.weights = cp.random.randn(input_size, output_size) * cp.sqrt(2 / input_size)
        elif weights_initializer == 'normal':
            self.weights = cp.random.normal(0, 1, (input_size, output_size))
        else:
            raise ValueError(f"Unknown weights initializer: {weights_initializer}")
        if biases_initializer == 'zeros':
            self.biases = cp.zeros((1, output_size))
        elif biases_initializer == 'ones':
            self.biases = cp.ones((1, output_size))
        elif biases_initializer == 'normal':
            self.biases = cp.random.normal(0, 1, (1, output_size))
        elif biases_initializer == 'uniform':
            limit = cp.sqrt(6.0 / input_size)
            self.biases = cp.random.uniform(-limit, limit, (1, output_size))
        else:
            raise ValueError(f"Unknown biases initializer: {biases_initializer}")

    def forward(self, inputs):
        self.inputs = inputs
        self.z = cp.dot(inputs, self.weights) + self.biases
        if self.activation_func is not None:
            self.a = self.activation_func(self.z)
            return self.a
        return self.z

    def backward(self, grad_output):
        if isinstance(self.activation_func, Softmax):
            grad_input = cp.dot(grad_output, self.weights.T)
            self.grad_weights = cp.dot(self.inputs.T, grad_output)
            self.grad_biases = cp.sum(grad_output, axis=0, keepdims=True)
        else:
            grad_activation = 1.0 if self.activation_func is None else self.activation_func.derivative(self.z)
            grad_output = grad_output * grad_activation
            grad_input = cp.dot(grad_output, self.weights.T)
            self.grad_weights = cp.dot(self.inputs.T, grad_output)
            self.grad_biases = cp.sum(grad_output, axis=0, keepdims=True)
        return grad_input


class Conv2D(LayerWithParameters):
    def __init__(self, num_filters, kernel_size, stride=1, padding=0, in_channels=1,
                 weights_initializer='he', biases_initializer='uniform', activation_func=None):
        self.params = {
            'num_filters': num_filters,
            'kernel_size': kernel_size,
            'stride': stride,
            'padding': padding,
            'in_channels': in_channels,
        }

        super().__init__(weights_shape=(num_filters, kernel_size, kernel_size, in_channels),
                         biases_shape=(num_filters,), decay_rate=0.9, epsilon=1e-8)
        k = kernel_size
        fan_in = in_channels * k * k
        fan_out = num_filters * k * k
        if weights_initializer == 'he':
            std = cp.sqrt(2.0 / fan_in)
            self.weights = cp.random.randn(num_filters, k, k, in_channels) * std
        elif weights_initializer == 'xavier':
            std = cp.sqrt(2.0 / (fan_in + fan_out))
            self.weights = cp.random.randn(num_filters, k, k, in_channels) * std
        elif weights_initializer == 'random':
            self.weights = cp.random.randn(num_filters, k, k, in_channels) * 0.01
        elif weights_initializer == 'uniform':
            limit = cp.sqrt(6.0 / fan_in)
            self.weights = cp.random.uniform(-limit, limit, (num_filters, k, k, in_channels))
        else:
            raise ValueError(f"Unknown weights initializer: {weights_initializer}")
        if biases_initializer == 'zeros':
            self.biases = cp.zeros((num_filters,))
        elif biases_initializer == 'ones':
            self.biases = cp.ones((num_filters,))
        elif biases_initializer == 'normal':
            self.biases = cp.random.normal(0, 1, (num_filters,))
        elif biases_initializer == 'uniform':
            limit = cp.sqrt(6.0 / fan_in)
            self.biases = cp.random.uniform(-limit, limit, (num_filters,))
        else:
            raise ValueError(f"Unknown biases initializer: {biases_initializer}")
        self.activation_func = activation_func

    def im2col(self, inputs):
        p, s, k = self.params['padding'], self.params['stride'], self.params['kernel_size']
        inputs = cp.asarray(inputs)
        if p > 0:
            inputs = cp.pad(inputs, ((0, 0), (p, p), (p, p), (0, 0)), mode='constant', constant_values=0)
        batch_size, height, width, in_channels = inputs.shape
        out_h = (height - k) // s + 1
        out_w = (width - k) // s + 1
        # Формируем strided массив для NHWC
        strides = (inputs.strides[0], s * inputs.strides[1], s * inputs.strides[2],
                   inputs.strides[1], inputs.strides[2], inputs.strides[3])
        strided = cp.lib.stride_tricks.as_strided(inputs,
                                                  shape=(batch_size, out_h, out_w, k, k, in_channels),
                                                  strides=strides)

        col = strided.reshape(batch_size * out_h * out_w, k * k * in_channels)
        return col, out_h, out_w

    def forward(self, inputs):
        self.inputs = inputs
        batch_size, height, width, in_channels = inputs.shape
        assert in_channels == self.params[
            'in_channels'], f"Несоответствие входных каналов: ожидается {self.params['in_channels']}, получено {in_channels}"

        im2col_matrix, out_h, out_w = self.im2col(inputs)

        weights_flat = self.weights.reshape(self.params['num_filters'], -1)

        output = cp.dot(im2col_matrix, weights_flat.T)

        output = output.reshape(batch_size, out_h, out_w, self.params['num_filters'])
        self.z = output + self.biases[None, None, None, :]


        if self.activation_func is not None:
            self.a = self.activation_func(self.z)
            return self.a
        return self.z

    def backward(self, d_out):
        batch_size, out_h, out_w, num_filters = d_out.shape
        im2col_matrix, _, _ = self.im2col(self.inputs)
        if self.activation_func is not None:
            grad_activation = self.activation_func.derivative(self.z)
            d_out = d_out * grad_activation
        d_out_flat = d_out.reshape(batch_size * out_h * out_w, num_filters)

        # Градиент весов
        self.grad_weights = cp.dot(d_out_flat.T, im2col_matrix).reshape(self.weights.shape)
        self.grad_biases = cp.sum(d_out, axis=(0, 1, 2))

        # Градиент входа
        weights_flat = self.weights.reshape(self.params['num_filters'], -1)
        d_inputs_flat = cp.dot(d_out_flat, weights_flat)
        d_inputs = self._col2im(d_inputs_flat, self.inputs.shape)
        return d_inputs

    def _col2im(self, cols, input_shape):
        batch_size, h, w, in_channels = input_shape
        p, s, k = self.params['padding'], self.params['stride'], self.params['kernel_size']
        out_h = (h + 2 * p - k) // s + 1
        out_w = (w + 2 * p - k) // s + 1
        d_inputs = cp.zeros((batch_size, h + 2 * p, w + 2 * p, in_channels), dtype=cp.float32)
        cols_reshaped = cols.reshape(batch_size, out_h, out_w, k, k, in_channels)
        for i in range(out_h):
            for j in range(out_w):
                h_start = i * s
                w_start = j * s
                d_inputs[:, h_start:h_start + k, w_start:w_start + k, :] += cols_reshaped[:, i, j, :, :, :]
        if p > 0:
            d_inputs = d_inputs[:, p:-p, p:-p, :]
        return d_inputs

class BatchNorm2D(LayerWithParameters):
    def __init__(self, num_features, eps=1e-5, momentum=0.99, biases_initializer='zeros'):
        super().__init__(weights_shape=(1, 1, 1, num_features), biases_shape=(1, 1, 1, num_features),
                         decay_rate=0.9, epsilon=eps)
        self.num_features = num_features
        self.momentum = momentum
        self.weights = cp.ones((1, 1, 1, num_features), dtype=cp.float32)
        if biases_initializer == 'zeros':
            self.biases = cp.zeros((1, 1, 1, num_features), dtype=cp.float32)
        else:
            raise ValueError(f"Unsupported biases_initializer: {biases_initializer}")
        self.running_mean = cp.zeros((1, 1, 1, num_features), dtype=cp.float32)
        self.running_var = cp.ones((1, 1, 1, num_features), dtype=cp.float32)
        self.cache = None

    def forward(self, inputs, training=True):
        batch_size,  height, width, channels= inputs.shape
        assert channels == self.num_features, "Несоответствие количества каналов"
        if training and batch_size > 1:
            mu = cp.mean(inputs, axis=(0, 1, 2), keepdims=True)
            var = cp.var(inputs, axis=(0, 1, 2), keepdims=True)
            inputs_hat = (inputs - mu) / cp.sqrt(var + self.epsilon)
            self.cache = (inputs, inputs_hat, mu, var)

            if cp.any(cp.isnan(mu)) or cp.any(cp.isnan(var)):
                raise ValueError("NaN в mu или var")
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mu
            self.running_var = self.momentum * self.momentum * self.running_var + (1 - self.momentum) * var
        else:
            inputs_hat = (inputs - self.running_mean) / cp.sqrt(self.running_var + self.epsilon)
        output = self.weights * inputs_hat + self.biases
        return output

    def backward(self, d_out):
        if self.cache is None:
            raise ValueError("Прямой проход с training=True должен быть вызван перед обратным")
        inputs, inputs_hat, mu, var = self.cache
        batch_size, height, width, channels = inputs.shape
        N = batch_size * height * width
        self.grad_weights = cp.sum(d_out * inputs_hat, axis=(0, 1, 2), keepdims=True)
        self.grad_biases = cp.sum(d_out, axis=(0, 1, 2), keepdims=True)
        d_inputs_hat = d_out * self.weights
        var_eps = var + self.epsilon
        d_var = cp.sum(d_inputs_hat * (inputs - mu) * -0.5 * var_eps ** (-1.5), axis=(0, 1, 2), keepdims=True)
        d_mu = cp.sum(d_inputs_hat * (-1 / cp.sqrt(var_eps)), axis=(0, 1, 2), keepdims=True) + \
               d_var * cp.sum(-2 * (inputs - mu), axis=(0, 1, 2), keepdims=True) / N
        d_inputs = d_inputs_hat / cp.sqrt(var_eps) + \
                   d_var * 2 * (inputs - mu) / N + \
                   d_mu / N
        return d_inputs


class Flatten:
    def forward(self, inputs):
        self.input_shape = inputs.shape
        batch_size = inputs.shape[0]
        return inputs.reshape(batch_size, -1)

    def backward(self, d_out):
        return d_out.reshape(self.input_shape)


class AveragePooling2D:
    def __init__(self, pool_size=2, stride=None):
        self.pool_size = pool_size
        self.stride = stride if stride is not None else pool_size
        self.inputs = None
        self.input_shape = None

    def forward(self, inputs):
        assert inputs.ndim == 4, "Input must be 4D (batch_size, height, width, channels)"
        self.input_shape = inputs.shape
        batch_size, height, width, channels = inputs.shape

        assert (height - self.pool_size) % self.stride == 0, "Invalid height for pooling"
        assert (width - self.pool_size) % self.stride == 0, "Invalid width for pooling"

        output_height = (height - self.pool_size) // self.stride + 1
        output_width = (width - self.pool_size) // self.stride + 1

        self.inputs = inputs

        strides = (
            inputs.strides[0],
            self.stride * inputs.strides[1],
            self.stride * inputs.strides[2],
            inputs.strides[1],
            inputs.strides[2],
            inputs.strides[3]
        )
        view = as_strided(
            inputs,
            shape=(batch_size, output_height, output_width, self.pool_size, self.pool_size, channels),
            strides=strides
        )

        outputs = cp.mean(view, axis=(3, 4))

        assert outputs.shape == (batch_size, output_height, output_width, channels), \
            f"Unexpected output shape: {outputs.shape}, expected: {(batch_size, output_height, output_width, channels)}"

        return outputs

    def backward(self, d_out):
        batch_size, out_height, out_width, channels = d_out.shape
        assert d_out.shape[0] == self.input_shape[0], "Batch size mismatch"
        assert d_out.shape[3] == self.input_shape[3], "Channels mismatch"

        d_inputs = cp.zeros_like(self.inputs)

        scale = 1.0 / (self.pool_size * self.pool_size)
        d_out_scaled = d_out * scale

        for i in range(out_height):
            for j in range(out_width):
                h_start = i * self.stride
                h_end = h_start + self.pool_size
                w_start = j * self.stride
                w_end = w_start + self.pool_size
                d_inputs[:, h_start:h_end, w_start:w_end, :] += d_out_scaled[:, i, j, :][:, None, None, :]

        return d_inputs


class MaxPooling2D:
    def __init__(self, pool_size=2, stride=None):
        self.pool_size = pool_size
        self.stride = stride if stride is not None else pool_size
        self.inputs = None
        self.input_shape = None

    def forward(self, inputs):
        assert inputs.ndim == 4, "Input must be 4D (batch_size, height, width, channels)"
        self.input_shape = inputs.shape
        batch_size, height, width, in_channels = inputs.shape

        assert (height - self.pool_size) % self.stride == 0, "Invalid height for pooling"
        assert (width - self.pool_size) % self.stride == 0, "Invalid width for pooling"

        output_height = (height - self.pool_size) // self.stride + 1
        output_width = (width - self.pool_size) // self.stride + 1

        self.inputs = inputs

        strides = (
            inputs.strides[0],  # batch
            self.stride * inputs.strides[1],
            self.stride * inputs.strides[2],
            inputs.strides[1],
            inputs.strides[2],
            inputs.strides[3]
        )
        view = as_strided(
            inputs,
            shape=(batch_size, output_height, output_width, self.pool_size, self.pool_size, in_channels),
            strides=strides
        )

        outputs = cp.max(view, axis=(3, 4))
        assert outputs.shape == (batch_size, output_height, output_width, in_channels), \
            f"Unexpected output shape: {outputs.shape}, expected: {(batch_size, output_height, output_width, in_channels)}"

        return outputs

    def backward(self, d_out):
        batch_size, out_height, out_width, channels = d_out.shape
        assert d_out.shape[0] == self.input_shape[0], "Batch size mismatch"
        assert d_out.shape[3] == self.input_shape[3], "Channels mismatch"

        d_inputs = cp.zeros_like(self.inputs)

        scale = 1.0 / (self.pool_size * self.pool_size)
        d_out_scaled = d_out * scale

        for i in range(out_height):
            for j in range(out_width):
                h_start = i * self.stride
                h_end = h_start + self.pool_size
                w_start = j * self.stride
                w_end = w_start + self.pool_size
                d_inputs[:, h_start:h_end, w_start:w_end, :] += d_out_scaled[:, i, j, :][:, None, None, :]

        return d_inputs

class Reshape:
    def __init__(self, target_shape):
        self.target_shape = target_shape
        self.input_shape = None

    def forward(self, inputs):
        self.input_shape = inputs.shape
        return inputs.reshape(self.target_shape)

    def backward(self, grad_output):
        return grad_output.reshape(self.input_shape)
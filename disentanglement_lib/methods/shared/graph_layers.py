
#flags = tf.app.flags
flags = tf.compat.v1.flags


# global unique layer ID dictionary for layer name assignment
_LAYER_UIDS = {}


def get_layer_uid(layer_name=''):
    """Helper function, assigns unique layer IDs
    """
    if layer_name not in _LAYER_UIDS:
        _LAYER_UIDS[layer_name] = 1
        return 1
    else:
        _LAYER_UIDS[layer_name] += 1
        return _LAYER_UIDS[layer_name]



def dropout_sparse(x, keep_prob, num_nonzero_elems):
    """Dropout for sparse tensors. Currently fails for very large sparse tensors (>1M elements)
    """
    noise_shape = [num_nonzero_elems]
    random_tensor = keep_prob
    random_tensor += tf.random_uniform(noise_shape)
    dropout_mask = tf.cast(tf.floor(random_tensor), dtype=tf.bool)
    pre_out = tf.sparse_retain(x, dropout_mask)
    return pre_out * (1./keep_prob)


class Layer(object):
    """Base layer class. Defines basic API for all layer objects.

    # Properties
        name: String, defines the variable scope of the layer.

    # Methods
        _call(inputs): Defines computation graph of layer
            (i.e. takes input, returns output)
        __call__(inputs): Wrapper for _call()
    """
    def __init__(self, **kwargs):
        allowed_kwargs = {'name'}
        for kwarg in kwargs.keys():
            assert kwarg in allowed_kwargs, 'Invalid keyword argument: ' + kwarg
        name = kwargs.get('name')
        if not name:
            layer = self.__class__.__name__.lower()
            name = layer + '_' + str(get_layer_uid(layer))
        self.name = name
        self.vars = {}
        self.issparse = False

    def _call(self, inputs):
        return inputs

    def __call__(self, inputs):
        with tf.name_scope(self.name):
            outputs = self._call(inputs)
            return outputs


class GraphConvolution(Layer):
    """Basic graph convolution layer for undirected graph without edge labels."""
    def __init__(self, input_dim, name, output_dim, adj, dropout=0., act=tf.nn.relu, **kwargs):
        self.name = name
        super(GraphConvolution, self).__init__(**kwargs)
        with tf.variable_scope(self.name + '_vars'):
            self.vars['weights'] = weight_variable_glorot(input_dim, output_dim, name="weights")
        self.dropout = dropout
        self.adj = adj
        self.act = act

    def _call(self, inputs):
        x = inputs
        x = tf.nn.dropout(x, 1-self.dropout)
        x = tf.matmul(x, self.vars['weights'])
        x = tf.sparse_tensor_dense_matmul(self.adj, x)
        outputs = self.act(x)
        return outputs


class GraphConvolutionSparse(Layer):
    """Graph convolution layer for sparse inputs."""
    def __init__(self, input_dim, output_dim, adj, features_nonzero, dropout=0., act=tf.nn.relu, **kwargs):
        super(GraphConvolutionSparse, self).__init__(**kwargs)
        with tf.variable_scope(self.name + '_vars'):
            self.vars['weights'] = weight_variable_glorot(input_dim, output_dim, name="weights")
        self.dropout = dropout
        self.adj = adj
        self.act = act
        self.issparse = True
        self.features_nonzero = features_nonzero

    def _call(self, inputs):
        x = inputs
        x = dropout_sparse(x, 1-self.dropout, self.features_nonzero)
        x = tf.sparse_tensor_dense_matmul(x, self.vars['weights'])
        x = tf.sparse_tensor_dense_matmul(self.adj, x)
        outputs = self.act(x)
        return outputs


class InnerProductDecoder(Layer):
    """Decoder model layer for link prediction."""
    def __init__(self, input_dim, dropout=0., act=tf.nn.sigmoid, **kwargs):
        super(InnerProductDecoder, self).__init__(**kwargs)
        self.dropout = dropout
        self.act = act

    def _call(self, inputs):
        inputs = tf.nn.dropout(inputs, 1-self.dropout)
        x = tf.transpose(inputs)
        x = tf.matmul(inputs, x)
        x = tf.reshape(x, [-1])
        outputs = self.act(x)
        return outputs

class GaussianExponentialDecoder(Layer):
    """Decoder model layer for link prediction."""
    def __init__(self, input_dim, kernel_parameter=0.1, dropout=0., act=tf.nn.sigmoid, **kwargs):
        super(GaussianExponentialDecoder, self).__init__(**kwargs)
        self.dropout = dropout
        self.act = act
        self.kernel_parameter =kernel_parameter

    def _call(self, inputs):
        inputs = tf.nn.dropout(inputs, 1-self.dropout)
        sqrt = tf.math.square(inputs)
        s = tf.reshape(tf.math.reduce_sum(sqrt, axis=1), [-1,1]) + tf.reduce_sum(sqrt, axis=1)
        dot = tf.tensordot(inputs, tf.transpose(inputs), 1)
        sqdist = s - 2* dot
        param = tf.cast(-0.5 * (1/ self.kernel_parameter), dtype='float32')
        x = tf.math.exp(tf.multiply(sqdist, param))
        x = tf.reshape(x, [-1])
        outputs = self.act(x)
        return outputs


class AuxiliaryPredictor(Layer):
    """Decoder model layer for auxiliary prediction."""
    def __init__(self, input_dim, output_dim, dropout=0., act=tf.nn.sigmoid, **kwargs):
        super(AuxiliaryPredictor, self).__init__(**kwargs)
        with tf.variable_scope(self.name + '_vars'):
            self.vars['weights'] = weight_variable_glorot(input_dim, output_dim, name="weights")
        self.act = act

    def _call(self, inputs):
        x = tf.matmul(inputs,  self.vars['weights'])
        outputs = self.act(x)
        return outputs


class Discriminator(Layer): 
    def __init__(self, hidden_size=256, depth=2, name="discriminator", **kwargs):
        super(Discriminator, self).__init__(**kwargs)
        self.middle_layers = [tfkl.Dense(hidden_size, activation=tf.nn.leaky_relu) for i in range(depth-1)]
        self.output_layer = tfkl.Dense(1)

    def _call(self, X): 
        h = X
        for layer in self.middle_layers: 
            h = layer(h) 
        return self.output_layer(h)


import tensorflow as tf
import numpy as np

from .layer import Layer
from .inits import weight_variable, bias_variable


class FC(Layer):
    def __init__(self,
                 in_channels,
                 out_channels,
                 dropout=False,
                 weight_stddev=0.01,
                 weight_decay=None,
                 bias=True,
                 bias_constant=0.0,
                 act=tf.nn.relu,
                 **kwargs):

        super(FC, self).__init__(**kwargs)

        self.in_channels = in_channels
        self.bias = bias
        self.act = act
        self.dropout = dropout

        with tf.variable_scope('{}_vars'.format(self.name)):
            self.vars['weights'] = weight_variable(
                [in_channels, out_channels],
                weight_stddev,
                weight_decay,
                name='{}_weights'.format(self.name))

            if self.bias:
                self.vars['bias'] = bias_variable(
                    [out_channels],
                    bias_constant,
                    name='{}_bias'.format(self.name))

        if self.logging:
            self._log_vars()

    def _call(self, inputs):
        outputs = tf.reshape(inputs, [-1, self.in_channels])

        if self.dropout:
            outputs = tf.nn.dropout(outputs, 1 - self.placeholders['dropout'])

        outputs = tf.matmul(outputs, self.vars['weights'])

        if self.bias:
            outputs = tf.nn.bias_add(outputs, self.vars['bias'])

        return self.act(outputs)

from __future__ import print_function

from six.moves import xrange

import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

from lib.graph.adjacency import grid_adj, normalize_adj, invert_adj
from lib.graph.preprocess import preprocess_adj
from lib.layer.conv2d import Conv2d
from lib.layer.max_pool2d import MaxPool2d
from lib.layer.fc import FC
from lib.model.model import Model

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.001, 'Initial learning rate.')
flags.DEFINE_integer('epochs', 200, 'Number of epochs to train.')
flags.DEFINE_float('dropout', 0.25, 'Dropout rate (1 - keep probability).')
flags.DEFINE_string('data_dir', 'data/mnist/input/',
                    'Directory for storing input data.')
flags.DEFINE_string('train_dir', 'data/mnist/train/',
                    'Directory for storing training data.')
flags.DEFINE_string('log_dir', 'data/mnist/summaries/',
                    'Summaries log directory.')
flags.DEFINE_integer('max_degree', 3, 'Maximum Chebyshev polynomial degree.')

mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=False)

WIDTH = 28
HEIGHT = 28
NUM_LABELS = 10
BATCH_SIZE = 128

adj = grid_adj([HEIGHT, WIDTH], connectivity=8)
adj = normalize_adj(adj)
adj = invert_adj(adj)
adj = preprocess_adj(adj)  # D^(-1/2) * A * D^(-1/2)

placeholders = {
    'features':
    tf.placeholder(tf.float32, [None, HEIGHT, WIDTH, 1], 'features'),
    'labels': tf.placeholder(tf.int32, [None], 'labels'),
    'dropout': tf.placeholder(tf.float32, [], 'dropout'),
}


class MNIST(Model):
    def __init__(self, **kwargs):
        super(MNIST, self).__init__(**kwargs)
        self.build()

    def _build(self):
        self.layers.append(
            Conv2d(1, 32, size=5, stride=1, logging=self.logging))
        self.layers.append(MaxPool2d(size=2, stride=2, logging=self.logging))
        self.layers.append(
            Conv2d(32, 64, size=5, stride=1, logging=self.logging))
        self.layers.append(MaxPool2d(size=2, stride=2, logging=self.logging))
        self.layers.append(FC(7 * 7 * 64, 1024, logging=self.logging))
        self.layers.append(
            FC(1024,
               NUM_LABELS,
               dropout=True,
               placeholders={'dropout': placeholders['dropout']},
               act=lambda x: x,
               logging=self.logging))


if tf.gfile.Exists(FLAGS.log_dir):
    tf.gfile.DeleteRecursively(FLAGS.log_dir)

model = MNIST(
    placeholders=placeholders,
    learning_rate=FLAGS.learning_rate,
    train_dir=FLAGS.train_dir,
    logging=True)


def evaluate(features, labels):
    feed_dict = {
        placeholders['features']: features,
        placeholders['labels']: labels,
        placeholders['dropout']: 0.0,
    }

    loss, acc = sess.run([model.loss, model.accuracy], feed_dict)
    return loss, acc


sess = tf.Session()
writer = tf.summary.FileWriter(FLAGS.log_dir, sess.graph)
sess.run(tf.global_variables_initializer())

for step in xrange(500):
    train_features, train_labels = mnist.train.next_batch(BATCH_SIZE)
    train_features = np.reshape(train_features, (-1, HEIGHT, WIDTH, 1))

    train_feed_dict = {
        placeholders['features']: train_features,
        placeholders['labels']: train_labels,
        placeholders['dropout']: FLAGS.dropout,
    }

    _, summary = sess.run([model.train, model.summary], train_feed_dict)
    writer.add_summary(summary, step)

    if step % 10 == 0:
        # Evaluate on training and validation set.
        train_loss, train_acc = evaluate(train_features, train_labels)
        val_features, val_labels = mnist.validation.next_batch(BATCH_SIZE)
        val_features = np.reshape(val_features, (-1, HEIGHT, WIDTH, 1))
        val_loss, val_acc = evaluate(val_features, val_labels)

        # Print results.
        print(', '.join([
            'Step: {}'.format(step),
            'train_loss={:.5f}'.format(train_loss),
            'train_acc={:.5f}'.format(train_acc),
            'val_loss={:.5f}'.format(val_loss),
            'val_acc={:.5f}'.format(val_acc),
        ]))

print('Optimization finished!')

# Evaluate on test set.
test_features = mnist.test.images[:256]
test_features = np.reshape(test_features, (-1, HEIGHT, WIDTH, 1))
test_labels = mnist.test.labels[:256]
test_loss, test_acc = evaluate(test_features, test_labels)
print('Test set results: cost={:.5f}, accuracy={:.5f}'.format(test_loss,
                                                              test_acc))

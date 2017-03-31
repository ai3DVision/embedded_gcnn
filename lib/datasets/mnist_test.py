from unittest import TestCase

from .mnist import MNIST


class MNISTTest(TestCase):
    def test_read_dataset(self):
        mnist = MNIST('/tmp/mnist')

        self.assertEqual(mnist.train._data.shape, (55000, 28, 28, 1))
        self.assertEqual(mnist.train._labels.shape, (55000, ))
        self.assertEqual(mnist.validation._data.shape, (5000, 28, 28, 1))
        self.assertEqual(mnist.validation._labels.shape, (5000, ))
        self.assertEqual(mnist.test._data.shape, (10000, 28, 28, 1))
        self.assertEqual(mnist.test._labels.shape, (10000, ))

from tensorflow.keras import backend as K
from tensorflow.keras.layers import Lambda
from tensorflow.keras.layers import Layer
from tensorflow.keras.utils import get_custom_objects


def repeat_elem(tensor, rep, output_shape=None):
    # Lambda function to repeat elements of a tensor along an axis by a factor of rep.
    def lambda_fn(x, repnum):
        return K.repeat_elements(x, repnum, axis=3)

    if output_shape is None:
        def output_shape_fn(input_shape):
            return (input_shape[0], input_shape[1], input_shape[2], input_shape[3] * rep)
    else:
        output_shape_fn = output_shape

    return Lambda(lambda_fn, arguments={'repnum': rep}, output_shape=output_shape_fn)(tensor)


class RepeatElements(Layer):
    def __init__(self, rep, **kwargs):
        super(RepeatElements, self).__init__(**kwargs)
        self.rep = rep

    def call(self, inputs):
        return K.repeat_elements(inputs, self.rep, axis=3)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], input_shape[2], input_shape[3] * self.rep)

    def get_config(self):
        config = super(RepeatElements, self).get_config()
        config.update({'rep': self.rep})
        return config

# Register the custom layer
get_custom_objects().update({'RepeatElements': RepeatElements})

import contextlib

import tensorflow as tf

from tfsnippet.utils import is_tensor_object, TensorArgValidator

__all__ = ['validate_group_ndims', 'reduce_group_ndims']


def validate_group_ndims(group_ndims, name=None):
    """
    Validate the specified value for `group_ndims` argument.

    If the specified `group_ndims` is a dynamic :class:`~tf.Tensor`,
    additional assertion will be added to the graph node of `group_ndims`.

    Args:
        group_ndims: Object to be validated.
        name: TensorFlow name scope of the graph nodes. (default
            "validate_group_ndims")

    Returns:
        tf.Tensor or int: The validated `group_ndims`.

    Raises:
        ValueError: If the specified `group_ndims` cannot pass validation.
    """
    @contextlib.contextmanager
    def gen_name_scope():
        if is_tensor_object(group_ndims):
            with tf.name_scope(name, default_name='validate_group_ndims'):
                yield
        else:
            yield
    with gen_name_scope():
        validator = TensorArgValidator('group_ndims')
        group_ndims = validator.require_non_negative(
            validator.require_int32(group_ndims)
        )
    return group_ndims


def reduce_group_ndims(operation, tensor, group_ndims, name=None):
    """
    Reduce the last `group_ndims` dimensions in `tensor`, using `operation`.

    In :class:`~tfsnippet.distributions.Distribution`, when computing the
    (log-)densities of certain `tensor`, the last few dimensions
    may represent a group of events, thus should be accounted together.
    This method can be used to reduce these dimensions, for example:

    .. code-block:: python

         log_prob = reduce_group_ndims(tf.reduce_sum, log_prob, group_ndims)
         prob = reduce_group_ndims(tf.reduce_prod, log_prob, group_ndims)

    Args:
        operation: The operation for reducing the last `group_ndims`
            dimensions. It must receive `tensor` as the 1st argument, and
            `axis` as the 2nd argument.
        tensor: The tensor to be reduced.
        group_ndims: The number of dimensions at the end of `tensor` to be
            reduced.  If it is a constant integer and is zero, then no
            operation will take place.
        name: TensorFlow name scope of the graph nodes. (default
            "reduce_group_ndims")

    Returns:
        tf.Tensor: The reduced tensor.

    Raises:
        ValueError: If `group_ndims` cannot be validated by
            :meth:`validate_group_ndims`.
    """
    group_ndims = validate_group_ndims(group_ndims)
    with tf.name_scope(name, default_name='reduce_group_ndims'):
        if is_tensor_object(group_ndims):
            tensor = tf.cond(
                group_ndims > 0,
                lambda: operation(tensor, tf.range(-group_ndims, 0)),
                lambda: tensor
            )
        else:
            if group_ndims > 0:
                tensor = operation(tensor, tf.range(-group_ndims, 0))
    return tensor

# Source: https://github.com/scipy/scipy
#
# Copyright (C) 2003-2005 Peter J. Verveer
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. The name of the author may not be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy
from . import _nd_image  # _nd_image.cp36-win32.pyd ; source: https://github.com/scipy/scipy/tree/master/scipy/ndimage


def _extend_mode_to_code(mode):
    """Convert an extension mode to the corresponding integer code.
    """
    if mode == 'nearest':
        return 0
    elif mode == 'wrap':
        return 1
    elif mode == 'reflect':
        return 2
    elif mode == 'mirror':
        return 3
    elif mode == 'constant':
        return 4
    else:
        raise RuntimeError('boundary mode not supported')


def _normalize_sequence(input, rank):
    """If input is a scalar, create a sequence of length equal to the
    rank by duplicating the input. If input is a sequence,
    check if its length is equal to the length of array.
    """
    is_str = isinstance(input, str)
    if hasattr(input, '__iter__') and not is_str:
        normalized = list(input)
        if len(normalized) != rank:
            err = "sequence argument must have length equal to input rank"
            raise RuntimeError(err)
    else:
        normalized = [input] * rank
    return normalized


def _get_output(output, input, shape=None):
    if shape is None:
        shape = input.shape
    if output is None:
        output = numpy.zeros(shape, dtype=input.dtype.name)
    elif isinstance(output, (type, numpy.dtype)):
        # Classes (like `np.float32`) and dtypes are interpreted as dtype
        output = numpy.zeros(shape, dtype=output)
    elif isinstance(output, str):
        output = numpy.typeDict[output]
        output = numpy.zeros(shape, dtype=output)
    elif output.shape != shape:
        raise RuntimeError("output shape not correct")
    return output


def _check_axis(axis, rank):
    if axis < 0:
        axis += rank
    if axis < 0 or axis >= rank:
        raise ValueError('invalid axis')
    return axis


def _invalid_origin(origin, lenw):
    return (origin < -(lenw // 2)) or (origin > (lenw - 1) // 2)


def uniform_filter1d(input, size, axis=-1, output=None, mode="reflect", cval=0.0, origin=0):
    """Calculate a one-dimensional uniform filter along the given axis.

    The lines of the array along the given axis are filtered with a
    uniform filter of given size.

    Parameters
    ----------
    %(input)s
    size : int
        length of uniform filter
    %(axis)s
    %(output)s
    %(mode)s
    %(cval)s
    %(origin)s
    """
    input = numpy.asarray(input)
    if numpy.iscomplexobj(input):
        raise TypeError('Complex type not supported')
    axis = _check_axis(axis, input.ndim)
    if size < 1:
        raise RuntimeError('incorrect filter size')
    output = _get_output(output, input)
    if (size // 2 + origin < 0) or (size // 2 + origin >= size):
        raise ValueError('invalid origin')
    mode = _extend_mode_to_code(mode)
    _nd_image.uniform_filter1d(input, size, axis, output, mode, cval, origin)
    return output


def uniform_filter(input, size=3, output=None, mode="reflect", cval=0.0, origin=0):
    """Multi-dimensional uniform filter.

    Parameters
    ----------
    %(input)s
    size : int or sequence of ints, optional
        The sizes of the uniform filter are given for each axis as a
        sequence, or as a single number, in which case the size is
        equal for all axes.
    %(output)s
    %(mode_multiple)s
    %(cval)s
    %(origin_multiple)s

    Returns
    -------
    uniform_filter : ndarray
        Filtered array. Has the same shape as `input`.

    Notes
    -----
    The multi-dimensional filter is implemented as a sequence of
    one-dimensional uniform filters. The intermediate arrays are stored
    in the same data type as the output. Therefore, for output types
    with a limited precision, the results may be imprecise because
    intermediate results may be stored with insufficient precision.
    """
    input = numpy.asarray(input)
    output = _get_output(output, input)
    sizes = _normalize_sequence(size, input.ndim)
    origins = _normalize_sequence(origin, input.ndim)
    modes = _normalize_sequence(mode, input.ndim)
    axes = list(range(input.ndim))
    axes = [(axes[ii], sizes[ii], origins[ii], modes[ii])
            for ii in range(len(axes)) if sizes[ii] > 1]
    if len(axes) > 0:
        for axis, size, origin, mode in axes:
            uniform_filter1d(input, int(size), axis, output, mode,
                             cval, origin)
            input = output
    else:
        output[...] = input[...]
    return output


def correlate1d(input, weights, axis=-1, output=None, mode="reflect", cval=0.0, origin=0):
    """Calculate a one-dimensional correlation along the given axis.

    The lines of the array along the given axis are correlated with the
    given weights.

    Parameters
    ----------
    %(input)s
    weights : array
        One-dimensional sequence of numbers.
    %(axis)s
    %(output)s
    %(mode)s
    %(cval)s
    %(origin)s
    """
    input = numpy.asarray(input)
    if numpy.iscomplexobj(input):
        raise TypeError('Complex type not supported')
    output = _get_output(output, input)
    weights = numpy.asarray(weights, dtype=numpy.float64)
    if weights.ndim != 1 or weights.shape[0] < 1:
        raise RuntimeError('no filter weights given')
    if not weights.flags.contiguous:
        weights = weights.copy()
    axis = _check_axis(axis, input.ndim)
    if _invalid_origin(origin, len(weights)):
        raise ValueError('Invalid origin; origin must satisfy '
                         '-(len(weights) // 2) <= origin <= '
                         '(len(weights)-1) // 2')
    mode = _extend_mode_to_code(mode)
    _nd_image.correlate1d(input, weights, axis, output, mode, cval,
                          origin)
    return output


def _gaussian_kernel1d(sigma, order, radius):
    """
    Computes a 1D Gaussian convolution kernel.
    """
    if order < 0:
        raise ValueError('order must be non-negative')
    exponent_range = numpy.arange(order + 1)
    sigma2 = sigma * sigma
    x = numpy.arange(-radius, radius + 1)
    phi_x = numpy.exp(-0.5 / sigma2 * x ** 2)
    phi_x = phi_x / phi_x.sum()

    if order == 0:
        return phi_x
    else:
        # f(x) = q(x) * phi(x) = q(x) * exp(p(x))
        # f'(x) = (q'(x) + q(x) * p'(x)) * phi(x)
        # p'(x) = -1 / sigma ** 2
        # Implement q'(x) + q(x) * p'(x) as a matrix operator and apply to the
        # coefficients of q(x)
        q = numpy.zeros(order + 1)
        q[0] = 1
        D = numpy.diag(exponent_range[1:], 1)  # D @ q(x) = q'(x)
        P = numpy.diag(numpy.ones(order) / -sigma2, -1)  # P @ q(x) = q(x) * p'(x)
        Q_deriv = D + P
        for _ in range(order):
            q = Q_deriv.dot(q)
        q = (x[:, None] ** exponent_range).dot(q)
        return q * phi_x


def gaussian_filter1d(input, sigma, axis=-1, order=0, output=None, mode="reflect", cval=0.0, truncate=4.0):
    """One-dimensional Gaussian filter.

    Parameters
    ----------
    %(input)s
    sigma : scalar
        standard deviation for Gaussian kernel
    %(axis)s
    order : int, optional
        An order of 0 corresponds to convolution with a Gaussian
        kernel. A positive order corresponds to convolution with
        that derivative of a Gaussian.
    %(output)s
    %(mode)s
    %(cval)s
    truncate : float, optional
        Truncate the filter at this many standard deviations.
        Default is 4.0.

    Returns
    -------
    gaussian_filter1d : ndarray
    """
    sd = float(sigma)
    # make the radius of the filter equal to truncate standard deviations
    lw = int(truncate * sd + 0.5)
    # Since we are calling correlate, not convolve, revert the kernel
    weights = _gaussian_kernel1d(sigma, order, lw)[::-1]
    return correlate1d(input, weights, axis, output, mode, cval, 0)


def gaussian_filter(input, sigma, order=0, output=None, mode="reflect", cval=0.0, truncate=4.0):
    """Multidimensional Gaussian filter.

    Parameters
    ----------
    %(input)s
    sigma : scalar or sequence of scalars
        Standard deviation for Gaussian kernel. The standard
        deviations of the Gaussian filter are given for each axis as a
        sequence, or as a single number, in which case it is equal for
        all axes.
    order : int or sequence of ints, optional
        The order of the filter along each axis is given as a sequence
        of integers, or as a single number.  An order of 0 corresponds
        to convolution with a Gaussian kernel. A positive order
        corresponds to convolution with that derivative of a Gaussian.
    %(output)s
    %(mode_multiple)s
    %(cval)s
    truncate : float
        Truncate the filter at this many standard deviations.
        Default is 4.0.

    Returns
    -------
    gaussian_filter : ndarray
        Returned array of same shape as `input`.

    Notes
    -----
    The multidimensional filter is implemented as a sequence of
    one-dimensional convolution filters. The intermediate arrays are
    stored in the same data type as the output. Therefore, for output
    types with a limited precision, the results may be imprecise
    because intermediate results may be stored with insufficient
    precision.
    """
    input = numpy.asarray(input)
    output = _get_output(output, input)
    orders = _normalize_sequence(order, input.ndim)
    sigmas = _normalize_sequence(sigma, input.ndim)
    modes = _normalize_sequence(mode, input.ndim)
    axes = list(range(input.ndim))
    axes = [(axes[ii], sigmas[ii], orders[ii], modes[ii])
            for ii in range(len(axes)) if sigmas[ii] > 1e-15]
    if len(axes) > 0:
        for axis, sigma, order, mode in axes:
            gaussian_filter1d(input, sigma, axis, order, output,
                              mode, cval, truncate)
            input = output
    else:
        output[...] = input[...]
    return output

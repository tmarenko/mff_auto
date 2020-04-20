# Source: https://pypi.org/project/scikit-image/
import numpy
from numpy.lib.arraypad import _as_pairs
from scipy.ndimage import uniform_filter, gaussian_filter

_integer_types = (numpy.byte, numpy.ubyte,          # 8 bits
                  numpy.short, numpy.ushort,        # 16 bits
                  numpy.intc, numpy.uintc,          # 16 or 32 or 64 bits
                  numpy.int_, numpy.uint,           # 32 or 64 bits
                  numpy.longlong, numpy.ulonglong)  # 64 bits
_integer_ranges = {t: (numpy.iinfo(t).min, numpy.iinfo(t).max)
                   for t in _integer_types}
dtype_range = {numpy.bool_: (False, True),
               numpy.bool8: (False, True),
               numpy.float16: (-1, 1),
               numpy.float32: (-1, 1),
               numpy.float64: (-1, 1)}
dtype_range.update(_integer_ranges)


def compare_ssim(x, y, win_size=None, gradient=False,
                 data_range=None, multichannel=False, gaussian_weights=False,
                 full=False, **kwargs):
    """Compute the mean structural similarity index between two images.

    Parameters
    ----------
    x, y : ndarray
        Image. Any dimensionality.
    win_size : int or None
        The side-length of the sliding window used in comparison. Must be an
        odd value. If `gaussian_weights` is True, this is ignored and the
        window size will depend on `sigma`.
    gradient : bool, optional
        If True, also return the gradient with respect to Y.
    data_range : float, optional
        The data range of the input image (distance between minimum and
        maximum possible values). By default, this is estimated from the image
        data-type.
    multichannel : bool, optional
        If True, treat the last dimension of the array as channels. Similarity
        calculations are done independently for each channel then averaged.
    gaussian_weights : bool, optional
        If True, each patch has its mean and variance spatially weighted by a
        normalized Gaussian kernel of width sigma=1.5.
    full : bool, optional
        If True, return the full structural similarity image instead of the
        mean value.

    Other Parameters
    ----------------
    use_sample_covariance : bool
        If True, normalize covariances by N-1 rather than, N where N is the
        number of pixels within the sliding window.
    K1 : float
        Algorithm parameter, K1 (small constant, see [1]_).
    K2 : float
        Algorithm parameter, K2 (small constant, see [1]_).
    sigma : float
        Standard deviation for the Gaussian when `gaussian_weights` is True.

    Returns
    -------
    mssim : float
        The mean structural similarity over the image.
    grad : ndarray
        The gradient of the structural similarity index between X and Y [2]_.
        This is only returned if `gradient` is set to True.
    S : ndarray
        The full SSIM image.  This is only returned if `full` is set to True.

    Notes
    -----
    To match the implementation of Wang et. al. [1]_, set `gaussian_weights`
    to True, `sigma` to 1.5, and `use_sample_covariance` to False.

    References
    ----------
    .. [1] Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P.
       (2004). Image quality assessment: From error visibility to
       structural similarity. IEEE Transactions on Image Processing,
       13, 600-612.
       https://ece.uwaterloo.ca/~z70wang/publications/ssim.pdf,
       :DOI:`10.1109/TIP.2003.819861`

    .. [2] Avanaki, A. N. (2009). Exact global histogram specification
       optimized for structural similarity. Optical Review, 16, 613-621.
       :arXiv:`0901.0065`
       :DOI:`10.1007/s10043-009-0119-z`

    """
    if not x.shape == y.shape:
        raise ValueError('Input images must have the same dimensions.')

    if multichannel:
        # loop over channels
        args = dict(win_size=win_size,
                    gradient=gradient,
                    data_range=data_range,
                    multichannel=False,
                    gaussian_weights=gaussian_weights,
                    full=full)
        args.update(kwargs)
        nch = x.shape[-1]
        mssim = numpy.empty(nch)
        g, s = None, None
        if gradient:
            g = numpy.empty(x.shape)
        if full:
            s = numpy.empty(x.shape)
        for ch in range(nch):
            ch_result = compare_ssim(x[..., ch], y[..., ch], **args)
            if gradient and full:
                mssim[..., ch], g[..., ch], s[..., ch] = ch_result
            elif gradient:
                mssim[..., ch], g[..., ch] = ch_result
            elif full:
                mssim[..., ch], s[..., ch] = ch_result
            else:
                mssim[..., ch] = ch_result
        mssim = mssim.mean()
        if gradient and full:
            return mssim, g, s
        elif gradient:
            return mssim, g
        elif full:
            return mssim, s
        else:
            return mssim

    k1 = kwargs.pop('K1', 0.01)
    k2 = kwargs.pop('K2', 0.03)
    sigma = kwargs.pop('sigma', 1.5)
    if k1 < 0:
        raise ValueError("K1 must be positive")
    if k2 < 0:
        raise ValueError("K2 must be positive")
    if sigma < 0:
        raise ValueError("sigma must be positive")
    use_sample_covariance = kwargs.pop('use_sample_covariance', True)

    truncate = None
    if gaussian_weights:
        # Set to give an 11-tap filter with the default sigma of 1.5 to match
        # Wang et. al. 2004.
        truncate = 3.5

    if win_size is None:
        if gaussian_weights:
            # set win_size used by crop to match the filter size
            r = int(truncate * sigma + 0.5)  # radius as in ndimage
            win_size = 2 * r + 1
        else:
            win_size = 7   # backwards compatibility

    if numpy.any((numpy.asarray(x.shape) - win_size) < 0):
        raise ValueError(
            "win_size exceeds image extent.  If the input is a multichannel (color) image, set multichannel=True.")

    if not (win_size % 2 == 1):
        raise ValueError('Window size must be odd.')

    if data_range is None:
        if x.dtype != y.dtype:
            print("Inputs have mismatched dtype.  Setting data_range based on X.dtype.")
        dmin, dmax = dtype_range[x.dtype.type]
        data_range = dmax - dmin

    ndim = x.ndim

    if gaussian_weights:
        filter_func = gaussian_filter
        filter_args = {'sigma': sigma, 'truncate': truncate}
    else:
        filter_func = uniform_filter
        filter_args = {'size': win_size}

    # ndimage filters need floating point data
    x = x.astype(numpy.float64)
    y = y.astype(numpy.float64)

    np = win_size ** ndim

    # filter has already normalized by NP
    if use_sample_covariance:
        cov_norm = np / (np - 1)  # sample covariance
    else:
        cov_norm = 1.0  # population covariance to match Wang et. al. 2004

    # compute (weighted) means
    ux = filter_func(x, **filter_args)
    uy = filter_func(y, **filter_args)

    # compute (weighted) variances and covariances
    uxx = filter_func(x * x, **filter_args)
    uyy = filter_func(y * y, **filter_args)
    uxy = filter_func(x * y, **filter_args)
    vx = cov_norm * (uxx - ux * ux)
    vy = cov_norm * (uyy - uy * uy)
    vxy = cov_norm * (uxy - ux * uy)

    r = data_range
    c1 = (k1 * r) ** 2
    c2 = (k2 * r) ** 2

    a1, a2, b1, b2 = ((2 * ux * uy + c1,
                       2 * vxy + c2,
                       ux ** 2 + uy ** 2 + c1,
                       vx + vy + c2))
    d = b1 * b2
    s = (a1 * a2) / d

    # to avoid edge effects will ignore filter radius strip around edges
    pad = (win_size - 1) // 2

    # compute (weighted) mean of ssim
    mssim = crop(s, pad).mean()

    if gradient:
        # The following is Eqs. 7-8 of Avanaki 2009.
        grad = filter_func(a1 / d, **filter_args) * x
        grad += filter_func(-s / b2, **filter_args) * y
        grad += filter_func((ux * (a2 - a1) - uy * (b2 - b1) * s) / d,
                            **filter_args)
        grad *= (2 / x.size)

        if full:
            return mssim, grad, s
        else:
            return mssim, grad
    else:
        if full:
            return mssim, s
        else:
            return mssim


def crop(ar, crop_width, copy=False, order='K'):
    """Crop array `ar` by `crop_width` along each dimension.

    Parameters
    ----------
    ar : array-like of rank N
        Input array.
    crop_width : {sequence, int}
        Number of values to remove from the edges of each axis.
        ``((before_1, after_1),`` ... ``(before_N, after_N))`` specifies
        unique crop widths at the start and end of each axis.
        ``((before, after),)`` specifies a fixed start and end crop
        for every axis.
        ``(n,)`` or ``n`` for integer ``n`` is a shortcut for
        before = after = ``n`` for all axes.
    copy : bool, optional
        If `True`, ensure the returned array is a contiguous copy. Normally,
        a crop operation will return a discontiguous view of the underlying
        input array.
    order : {'C', 'F', 'A', 'K'}, optional
        If ``copy==True``, control the memory layout of the copy. See
        ``np.copy``.

    Returns
    -------
    cropped : array
        The cropped array. If ``copy=False`` (default), this is a sliced
        view of the input array.
    """
    ar = numpy.array(ar, copy=False)
    crops = _as_pairs(crop_width, ar.ndim, as_index=True)
    slices = tuple(slice(a, ar.shape[i] - b)
                   for i, (a, b) in enumerate(crops))
    if copy:
        cropped = numpy.array(ar[slices], order=order, copy=True)
    else:
        cropped = ar[slices]
    return cropped

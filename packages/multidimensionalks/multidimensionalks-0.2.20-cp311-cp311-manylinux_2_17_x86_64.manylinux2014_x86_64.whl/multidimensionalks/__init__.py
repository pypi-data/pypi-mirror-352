from .pure import test as test_pure
from .avx2 import test as test_avx2
from .avx512 import test as test_avx512
from .brute import test as test_brute
from .brute_avx2 import test as test_brute_avx2
from .brute_avx512 import test as test_brute_avx512

import platform
import numpy as np

def test(rvs, **kwargs):
    if platform.processor() != 'arm':
        from cpufeature.extension import CPUFeature
    try:
        if not CPUFeature:
            CPUFeature = {
                'AVX512vl': False,
                'AVX2': False
            }
    except NameError:
        CPUFeature = {
            'AVX512vl': False,
            'AVX2': False
        }
    use_avx = kwargs.pop("use_avx", 3)
    brute = kwargs.pop("brute", False)
    method = test_brute if brute else test_pure
    if use_avx == 1 and not CPUFeature['AVX512vl']:
        print("!!! Warning: AVX512vl instruction set is not supported by your CPU, backing up to pure implementation")
    elif use_avx in (1, 3) and CPUFeature['AVX512vl']:
        method = test_brute_avx512 if brute else test_avx512
    elif use_avx == 2 and not CPUFeature['AVX2']:
        print("!!! Warning: AVX2 instruction set is not supported by your CPU, backing up to pure implementation")
    elif use_avx in (2, 3) and CPUFeature['AVX2']:
        method = test_brute_avx2 if brute else test_avx2

    if not isinstance(rvs, np.ndarray):
        rvs = np.array(rvs)
    if len(np.shape(rvs)) == 1:
        rvs = np.expand_dims(rvs, axis=1)

    cdf = kwargs.pop("cdf", None)
    if cdf is not None:
        if not isinstance(cdf, np.ndarray):
            cdf = np.array(cdf)
        if len(np.shape(cdf)) == 1:
            cdf = np.expand_dims(cdf, axis=1)
        kwargs["cdf"] = cdf

    return method(rvs, **kwargs)

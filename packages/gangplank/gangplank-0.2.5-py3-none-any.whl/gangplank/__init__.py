"""
Please refer to the documentation provided in the README.md,
which can be found at gangplank's PyPI URL: https://pypi.org/project/gangplank/
"""

from .train_test_exporter import (
    TrainTestExporter,
    # Represents histogram weight buckets in interval [-0.3, +0.3]
    HISTOGRAM_WEIGHT_BUCKETS_0_3,
    # Represents histogram weight buckets in interval [-1.0, +1.0]
    HISTOGRAM_WEIGHT_BUCKETS_1_0,
)

# Defines the public API of the module, specifying the names to be imported when using
# `from module import *`. These names are included in `__all__` because they represent
# key components of the module's functionality.
__all__ = [
    TrainTestExporter,
    HISTOGRAM_WEIGHT_BUCKETS_0_3,
    HISTOGRAM_WEIGHT_BUCKETS_1_0,
]

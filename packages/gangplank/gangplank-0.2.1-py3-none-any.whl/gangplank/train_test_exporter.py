"""
This module defines the `TrainTestExporter` Keras callback for exporting training and
testing metrics to a Prometheus Pushgateway.

Classes:
    TrainTestExporter:
        A Keras callback that collects and pushes training and testing metrics, model
        parameter counts, and optionally weight histograms to a Prometheus Pushgateway.

Constants:
    HISTOGRAM_WEIGHT_BUCKETS_1_0: List of float
        Predefined histogram buckets ranging from -1.0 to 1.0 for model weights.
    HISTOGRAM_WEIGHT_BUCKETS_0_3: List of float
        Predefined histogram buckets ranging from -0.3 to 0.3 for model weights.

Dependencies:
    - keras
    - prometheus_client

Usage:
    Instantiate `TrainTestExporter` and pass it as a callback to Keras model training
    or evaluation. Metrics and model statistics will be pushed to the specified
    Prometheus Pushgateway address.
"""

import keras

import numbers
import sys
import time
import traceback
from prometheus_client import CollectorRegistry, Gauge, Histogram, push_to_gateway

HISTOGRAM_WEIGHT_BUCKETS_1_0 = [
    -1.0,
    -0.9,
    -0.8,
    -0.7,
    -0.6,
    -0.5,
    -0.4,
    -0.3,
    -0.2,
    -0.1,
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0,
]

HISTOGRAM_WEIGHT_BUCKETS_0_3 = [
    -0.30,
    -0.25,
    -0.20,
    -0.15,
    -0.10,
    -0.05,
    0.00,
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
]


class TrainTestExporter(keras.callbacks.Callback):
    """
    Initializes the exporter with configuration for Prometheus metrics collection.

    Args:
        pgw_addr: The address of the Prometheus gateway.
        job: The job name for Prometheus metrics.
        metrics (optional): A list of metrics to be exported.
        histogram_buckets (optional): Custom buckets for Prometheus histograms.
        handler (optional): An authentication handler for the gateway.
        ignore_exceptions (bool, optional): Whether to ignore exceptions during metric
            export. Defaults to True.
    """

    def __init__(
        self,
        pgw_addr,
        job,
        metrics=None,
        histogram_buckets=None,
        handler=None,
        ignore_exceptions=True,
    ):
        super().__init__()
        self.pgw_addr = pgw_addr
        self.job = job
        self.metrics = metrics
        self.histogram_buckets = histogram_buckets
        self.handler = handler
        self.ignore_exceptions = ignore_exceptions
        self.registry = CollectorRegistry()
        self.gauges = {}
        self.is_done = False
        # We need to distinguish between training and testing.
        # We'll set this to True if on_training_start is called.
        self.is_training = False

    @staticmethod
    def _exception_handler(func):
        def wrapper_func(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                if self.ignore_exceptions:
                    traceback.print_exc(file=sys.stderr)
                else:
                    raise e

        return wrapper_func

    def _get_metrics(self, logs):
        if self.metrics is not None:
            return self.metrics
        metrics = []
        for k, v in logs.items():
            if isinstance(v, numbers.Number):
                metrics.append(k)

        return metrics

    def _get_gauge(self, name, desc):
        if not self.gauges.get(name):
            self.gauges[name] = Gauge(name, desc, registry=self.registry)
        return self.gauges[name]

    def _push_to_gateway(self):
        if self.handler:
            push_to_gateway(
                self.pgw_addr, self.job, self.registry, handler=self.handler
            )
        else:
            push_to_gateway(self.pgw_addr, self.job, self.registry)

    def _construct_histogram(self, name):
        histogram = Histogram(
            name,
            "model trainable weights",
            buckets=self.histogram_buckets,
            registry=self.registry,
        )
        for layer in self.model.layers:
            if not layer.trainable:
                continue
            weights = layer.get_weights()
            for weight in weights:
                weight = weight.flatten()
                for w in weight:
                    histogram.observe(w)

    @_exception_handler
    def on_test_begin(self, logs):
        if self.is_done:
            raise RuntimeError("cannot reuse this callback for a new run.")

        if self.is_training:
            return

        self.start_time = time.time()

    @_exception_handler
    def on_test_end(self, logs):
        if self.is_training:
            return

        self.is_done = True

        metrics = self._get_metrics(logs)
        for k in metrics:
            v = logs.get(k)
            if v is not None:
                gauge = self._get_gauge("gangplank_test_" + k, k)
                gauge.set(v)

        gauge = self._get_gauge(
            "gangplank_test_model_parameters_count",
            "the number of trainable and non-trainable model weights",
        )
        gauge.set(self.model.count_params())

        gauge = self._get_gauge(
            "gangplank_test_elapsed_time_seconds",
            "the amount of time spent testing the model",
        )
        gauge.set(time.time() - self.start_time)

        if self.histogram_buckets:
            self._construct_histogram("gangplank_test_model_weights")

        self._push_to_gateway()

    @_exception_handler
    def on_train_begin(self, logs):
        if self.is_done:
            raise RuntimeError("cannot reuse this callback for a new run.")

        self.is_training = True
        self.start_time = time.time()

    @_exception_handler
    def on_epoch_end(self, epoch, logs):
        metrics = self._get_metrics(logs)
        for k in metrics:
            v = logs.get(k)
            if v is not None:
                gauge = self._get_gauge("gangplank_train_" + k, k)
                gauge.set(v)

        gauge = self._get_gauge(
            "gangplank_train_model_parameters_count",
            "the number of trainable and non-trainable model weights",
        )
        gauge.set(self.model.count_params())

        gauge = self._get_gauge(
            "gangplank_train_epochs_count", "the number of completed training epochs"
        )
        gauge.set(epoch + 1)

        gauge = self._get_gauge(
            "gangplank_train_elapsed_time_seconds",
            "the amount of time spent training the model",
        )
        gauge.set(time.time() - self.start_time)

        self._push_to_gateway()

    @_exception_handler
    def on_train_end(self, logs):
        self.is_done = True

        if not self.histogram_buckets:
            return

        self._construct_histogram("gangplank_train_model_weights")

        self._push_to_gateway()

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Abstract base class for training tasks supported by the framework.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import abc
from pydoc import locate

import six

from seq2seq.training import hooks
from seq2seq import models
from seq2seq.configurable import Configurable
from seq2seq.metrics.metric_specs import METRIC_SPECS_DICT

@six.add_metaclass(abc.ABCMeta)
class TrainingTask(Configurable):
  """
  Abstract base class for training tasks. Defines the logic used to
  create training models.

  Params:
    model_class: The model class to instantiate.
    model_params: Model hyperparameters.
    metrics: A list of metrics to monitor during evaluation.

  Args:
    params: See Params above.
    train_options: A `TrainOptions` instance.
  """
  def __init__(self, params):
    super(TrainingTask, self).__init__(params, None)
    self._model_cls = locate(self.params["model_class"]) or \
      getattr(models, self.params["model_class"])

  @staticmethod
  def default_params():
    return {
        "metrics": [],
        "model_class": "",
        "model_params": {},
        "hooks": [
            {
                "class": "PrintModelAnalysisHook",
                "params": hooks.PrintModelAnalysisHook.default_params()
            },
            {
                "class": "MetadataCaptureHook",
                "params": hooks.MetadataCaptureHook.default_params()
            }
        ]
    }

  def create_model(self, mode):
    """Creates a model instance.

    Args:
      mode: The mode to create the model in. One of tf.contrib.learn.ModeKeys.

    Returns:
      A new model instance.
    """
    return self._model_cls(
        params=self.params["model_params"],
        mode=mode)

  def create_training_hooks(self, estimator):
    """Creates SessionRunHooks to be used during training.

    Args:
      estimator: The tf.learn model estimator.

    Returns:
      A list of SessionRunHooks.
    """
    training_hooks = []
    for hook_dict in self.params["hooks"]:
      hook_cls = locate(hook_dict["class"]) or \
        getattr(hooks, hook_dict["class"])
      hook = hook_cls(hook_dict["params"], estimator.model_dir)
      training_hooks.append(hook)
    return training_hooks

  def create_metrics(self):
    """Creates metrics to be used during evaluation.

    Returns:
      A list of MetricSpecs.
    """
    return {m : METRIC_SPECS_DICT[m] for m in self.params["metrics"]}

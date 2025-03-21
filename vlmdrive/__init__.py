import inspect

import torch
import torch.utils.data
from torch import optim
from torch import nn

from common import Registry
VLMDRIVE_REGISTRY = Registry('vlmdrive') 
from vlmdrive import vlm
from vlmdrive import controller

__all__ = ['vlm', 'controller']


def _register_all_classes_within_module(m):
    for k, v in m.__dict__.items():
        # filter out private objects and magic methods
        if k.startswith('_'):
            continue
        # filter out non-class object,
        #   assuming python naming convention being strictly followed within PyTorch
        if not k[0].isupper():
            continue
        if k in VLMDRIVE_REGISTRY:
            continue
        if not inspect.isclass(v):
            continue
        if not inspect.isclass(v):
            continue
        if v.__name__ in VLMDRIVE_REGISTRY:
            continue
        VLMDRIVE_REGISTRY.register(v)


# register all optimizers from torch
_register_all_classes_within_module(optim)
# register all lr_schedulers from torch
_register_all_classes_within_module(optim.lr_scheduler)
# register all nn.Modules from torch
_register_all_classes_within_module(nn)
# register all torch.utils.data from torch
_register_all_classes_within_module(torch.utils.data)

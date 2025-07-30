import os
import random
from typing import List, Optional, Tuple

import numpy as np
import torch


def show_environment_setting(print_fn):
    msg = "CUDA INFO:"
    msg += f"\n\tIs CUDA supported by this system? {torch.cuda.is_available()}"
    if torch.cuda.is_available():
        msg += f"\n\tCUDA version: {torch.version.cuda}"
        msg += f"\n\tID of current CUDA device: {torch.cuda.current_device()}"
        msg += f"\n\tName of current CUDA device: {torch.cuda.get_device_name(torch.cuda.current_device())}"
    print_fn(msg)


def att_mask_from_individual_masks(
    tgt_mask: torch.Tensor, src_mask: torch.Tensor
) -> torch.Tensor:
    """Combine two individual masks for attention mask

    :param tgt_mask: mask for target sequence with shape (bsz, tgt_len)
    :type tgt_mask: torch.Tensor
    :param src_mask: mask for source sequence with shape (bsz, src_len)
    :type src_mask: torch.Tensor
    :return: attention mask with shape (bsz, tgt_len, src_len)
    :rtype: torch.Tensor
    """
    tgt_len = tgt_mask.shape[-1]
    src_len = src_mask.shape[-1]

    _tgt_mask = tgt_mask.unsqueeze(-1).repeat(1, 1, src_len)
    _src_mask = src_mask.unsqueeze(1).repeat(1, tgt_len, 1)

    return _tgt_mask * _src_mask


def zero_pad_batching_one_dim(
    tensor_list: List[torch.Tensor], return_mask=True
) -> Tuple[torch.Tensor, torch.Tensor]:
    max_len = max([len(tensor) for tensor in tensor_list])
    device = tensor_list[0].device
    shape = (
        (len(tensor_list), max_len)
        if len(tensor_list[0].shape) == 1
        else (len(tensor_list), max_len, *list(tensor_list[0].shape[1:]))
    )
    token_tensor = torch.zeros(shape, dtype=tensor_list[0].dtype, device=device)
    if return_mask:
        mask_tensor = torch.ones(shape, dtype=torch.bool, device=device)
    for idx, tensor in enumerate(tensor_list):
        token_tensor[idx, : len(tensor)] = tensor
        if return_mask:
            mask_tensor[idx, : len(tensor)] = False
    return (token_tensor, mask_tensor) if return_mask else token_tensor


def zero_pad_batching_two_dim(
    tensor_list: List[torch.Tensor], return_mask=True
) -> torch.Tensor:
    device = tensor_list[0].device
    dim_one_max_len = max([len(tensor) for tensor in tensor_list])
    dim_two_max_len = max([len(tensor[0]) for tensor in tensor_list])
    token_tensor = torch.zeros(
        len(tensor_list),
        dim_one_max_len,
        dim_two_max_len,
        dtype=tensor_list[0].dtype,
        device=device,
    )
    if return_mask:
        mask_tensor = torch.ones(token_tensor, dtype=torch.bool, device=device)
    for idx, tensor in enumerate(tensor_list):
        token_tensor[idx, : len(tensor), : len(tensor[0])] = tensor
        if return_mask:
            mask_tensor[idx, : len(tensor), : len(tensor[0])] = False
    return (token_tensor, mask_tensor) if return_mask else token_tensor


def zero_pad_batching(tensor_list: List[torch.Tensor]) -> torch.Tensor:
    tensor_item = tensor_list[0]
    if len(tensor_item.shape) == 1:
        return zero_pad_batching_one_dim(tensor_list)
    elif len(tensor_item.shape) == 2:
        return zero_pad_batching_two_dim(tensor_list)
    else:
        raise NotImplementedError(
            f"Only support 1D and 2D tensor, but found: {tensor_item.shape}"
        )


def set_torch_deterministic(seed: Optional[int] = 0) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if you are using multi-GPU.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def is_torch_compile_available() -> None:
    if torch.cuda.is_available():
        device_cap = torch.cuda.get_device_capability()
        return device_cap[0] >= 7
    return False


def calculate_model_size(model: torch.nn.Module, in_MB: bool = False) -> float:
    """Compute model size in KB or MB

    :param model: model to compute size
        in_MB: if True, return size in MB, otherwise return size in KB
    :type model: torch.nn.Module
    :return: model size in KB or MB
    :rtype: int
    """
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    # Default is in KB
    exp_val = 2 if in_MB else 3
    return (param_size + buffer_size) / 1024**exp_val


def count_parameters(model: torch.nn.Module, only_trainable: bool = True) -> int:
    """Count the number of trainable model parameter

    :param model: model to compute size
    :type model: torch.nn.Module
    :return: number of model parameter
    :rtype: int
    """
    return sum(
        p.numel() for p in model.parameters() if p.requires_grad or (not only_trainable)
    )


def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )


if __name__ == "__main__":
    show_environment_setting(print)

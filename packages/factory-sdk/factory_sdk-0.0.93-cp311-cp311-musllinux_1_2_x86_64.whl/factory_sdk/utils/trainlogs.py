import torch
import logging
from typing import Dict

import GPUtil


def compute_model_dynamics(model) -> Dict[str, Dict[str, float]]:
    """
    Collect simple layer statistics (norm, mean, std)
    for weights and optionally for gradients if available.
    """
    layers_stats = {}
    for name, module in model.named_modules():
        has_trainable_weight = (
            hasattr(module, "weight")
            and module.weight is not None
            and module.weight.requires_grad
        )
        if not has_trainable_weight:
            continue

        # Basic weight stats
        w = module.weight.detach()
        layer_info = {
            "weight_norm": float(w.norm().item()),
            "weight_mean": float(w.mean().item()),
            "weight_std": float(w.std().item()),
        }

        # Optional gradient stats
        if module.weight.grad is not None:
            g = module.weight.grad.detach()
            layer_info.update(
                {
                    "grad_norm": float(g.norm().item()),
                    "grad_mean": float(g.mean().item()),
                    "grad_std": float(g.std().item()),
                }
            )

        layers_stats[name] = layer_info

    return layers_stats


def log_gpu_utilization(global_step: int) -> Dict[int, Dict[str, float]]:
    """
    Return a dictionary of GPU metrics for each visible GPU:
    { gpu_idx: {step, utilization, memory_used, memory_total} }
    """
    gpu_data = {}
    try:
        if torch.cuda.is_available():
            for idx, gpu in enumerate(GPUtil.getGPUs()):
                gpu_data[idx] = {
                    "step": global_step,
                    "utilization": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal,
                }
    except Exception as e:
        logging.warning(f"GPU metric collection error: {e}")
    return gpu_data

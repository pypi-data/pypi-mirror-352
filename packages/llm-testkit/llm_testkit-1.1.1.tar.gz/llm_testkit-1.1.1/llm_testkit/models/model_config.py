#!/usr/bin/env python3
"""
Model configuration utilities for LLM evaluation.
"""

from typing import Dict, Any, List, Optional, Union
from ..utils.gpu import get_available_gpus

def build_model_args(
    model_type: str,
    model_name: str,
    quantize: bool = False,
    quantization_method: Optional[str] = None,
    dtype: Optional[str] = None,
    max_model_len: Optional[int] = None,
    tensor_parallel_size: int = 1,
    gpu_memory_utilization: float = 0.9,
    vllm_quantization: Optional[str] = None,
    additional_model_args: Optional[str] = None
) -> str:
    """
    Build model arguments string based on model type and configuration.
    """
    if model_type == "vllm":
        # vLLM model_args format
        model_args = [f"pretrained={model_name}"]
        
        if tensor_parallel_size > 1:
            model_args.append(f"tensor_parallel_size={tensor_parallel_size}")
        
        if dtype:
            model_args.append(f'dtype={dtype}')
        
        if max_model_len:
            model_args.append(f"max_model_len={max_model_len}")
            
        # Add GPU memory utilization
        model_args.append(f"gpu_memory_utilization={gpu_memory_utilization}")
        
        # Add quantization for vLLM if specified
        if vllm_quantization:
            model_args.append(f"quantization={vllm_quantization}")
    else:
        # Standard HF model_args format
        model_args = [f"pretrained={model_name}"]
        
        if quantize:
            # Map our quantization method to proper HuggingFace parameters
            if quantization_method == "4bit":
                model_args.append("load_in_4bit=True")
            elif quantization_method == "8bit":
                model_args.append("load_in_8bit=True")
            elif quantization_method in ["nf4", "fp4"]:
                model_args.append("load_in_4bit=True")
                model_args.append(f"bnb_4bit_quant_type={quantization_method}")
            elif quantization_method == "int8":
                model_args.append("load_in_8bit=True")
            elif quantization_method == "int4":
                model_args.append("load_in_4bit=True")
    
    # Add additional model args if specified
    if additional_model_args:
        model_args.extend(additional_model_args.split(','))
        
    return ",".join(model_args)

def check_gpu_requirements(model_type: str, tensor_parallel_size: int) -> None:
    """
    Check if enough GPUs are available for tensor parallelism.
    Raises ValueError if not enough GPUs are available.
    """
    if model_type == "vllm" and tensor_parallel_size > 1:
        available_gpus = get_available_gpus()
        if available_gpus < tensor_parallel_size:
            raise ValueError(
                f"Not enough GPUs available for tensor parallelism. "
                f"Requested {tensor_parallel_size} GPUs but only {available_gpus} available. "
                f"Please reduce tensor_parallel_size to {available_gpus} or fewer."
            )

def get_comprehensive_model_info(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract comprehensive model information from evaluation config.
    
    Args:
        config: Configuration dictionary from evaluation results
        
    Returns:
        Dictionary with detailed model configuration information
    """
    model_info = {
        # Basic model information
        "name": "Unknown Model",
        "parameters": "Not specified",
        "architecture": "Not specified", 
        "context_length": "Not specified",
        "backend": "Unknown",
        "quantization": "None",
        "device_mapping": "Single GPU",
        "data_type": "Not specified",
        
        # Advanced configuration
        "tensor_parallel_size": 1,
        "pipeline_parallel_size": 1,
        "gpu_memory_utilization": "Not specified",
        "max_model_len": "Not specified",
        "trust_remote_code": "False",
        "revision": "main",
        "torch_dtype": "auto",
        
        # Generation parameters
        "temperature": "Not specified",
        "top_p": "Not specified", 
        "top_k": "Not specified",
        "max_tokens": "Not specified",
        "max_new_tokens": "Not specified",
        "do_sample": "Not specified",
        "num_beams": "Not specified",
        "repetition_penalty": "Not specified",
        "length_penalty": "Not specified",
        "early_stopping": "Not specified",
        
        # Attention and memory settings
        "attention_implementation": "Not specified",
        "use_flash_attention": "Not specified",
        "gradient_checkpointing": "Not specified",
        "low_cpu_mem_usage": "Not specified",
        "device_map": "Not specified",
        
        # Batch and performance settings
        "batch_size": "Not specified",
        "max_batch_size": "Not specified",
        "enable_chunked_prefill": "Not specified",
        "max_num_batched_tokens": "Not specified",
        
        # PEFT and fine-tuning
        "peft_config": "None",
        "lora_config": "None",
        "adapter_name": "None",
        
        # Safety and filtering
        "safety_checker": "Not specified",
        "requires_safety_checker": "Not specified",
        
        # Caching and optimization
        "use_cache": "Not specified",
        "cache_dir": "Not specified",
        "offload_folder": "Not specified",
        "local_files_only": "False",
        
        # Training and optimization specific
        "fp16": "Not specified",
        "bf16": "Not specified",
        "tf32": "Not specified",
        "use_fast_tokenizer": "True",
        "model_max_length": "Not specified",
        "tokenizer_name": "Not specified",
        "padding_side": "Not specified",
        
        # vLLM specific
        "swap_space": "Not specified",
        "enable_lora": "False",
        "max_lora_rank": "Not specified",
        "enable_prefix_caching": "Not specified",
        "disable_log_stats": "False",
        "download_dir": "Not specified",
        "load_format": "auto",
        "seed": "Not specified",
        
        # Distributed settings
        "distributed_executor_backend": "Not specified",
        "worker_use_ray": "False",
        "ray_workers_use_nsight": "False",
        
        # Advanced features
        "enable_chunked_prefill": "Not specified",
        "speculative_model": "None",
        "num_speculative_tokens": "Not specified",
        "speculative_draft_tensor_parallel_size": "Not specified",
        "ngram_prompt_lookup_max": "Not specified",
        "ngram_prompt_lookup_min": "Not specified"
    }
    
    # Extract model name and backend
    if 'model' in config:
        model_info["backend"] = config['model'].upper()
    
    # Parse model_args for detailed information
    if 'model_args' in config:
        model_args = config['model_args']
        
        # Extract model name
        if 'pretrained=' in model_args:
            model_name = model_args.split('pretrained=')[1].split(',')[0]
            model_info["name"] = model_name
            
            # Infer model details from name
            name_lower = model_name.lower()
            _infer_model_details_from_name(model_info, name_lower)
        
        # Parse all model arguments
        _parse_model_args(model_info, model_args)
    
    # Extract generation parameters
    if 'generation_args' in config:
        _parse_generation_args(model_info, config['generation_args'])
    
    # Extract task-specific information
    if 'tasks' in config:
        model_info["evaluated_tasks"] = ', '.join(config['tasks'])
    else:
        model_info["evaluated_tasks"] = "Not specified"
    
    # Extract evaluation metadata
    if 'num_fewshot' in config:
        model_info["num_fewshot"] = str(config['num_fewshot'])
    else:
        model_info["num_fewshot"] = "Not specified"
        
    if 'batch_size' in config:
        model_info["batch_size"] = str(config['batch_size'])
    
    if 'device' in config:
        model_info["evaluation_device"] = config['device']
    else:
        model_info["evaluation_device"] = "Not specified"
    
    # Extract limit/num_samples information
    if 'limit' in config:
        model_info["samples_per_task"] = str(config['limit'])
    elif 'num_samples' in config:
        model_info["samples_per_task"] = str(config['num_samples'])
    else:
        model_info["samples_per_task"] = "All available"
    
    return model_info

def _infer_model_details_from_name(model_info: Dict[str, Any], name_lower: str) -> None:
    """Infer model details from the model name."""
    # Infer parameter count
    if "7b" in name_lower:
        model_info["parameters"] = "~7 billion"
    elif "13b" in name_lower:
        model_info["parameters"] = "~13 billion"
    elif "70b" in name_lower:
        model_info["parameters"] = "~70 billion"
    elif "3b" in name_lower:
        model_info["parameters"] = "~3 billion"
    elif "1b" in name_lower:
        model_info["parameters"] = "~1 billion"
    elif "405b" in name_lower:
        model_info["parameters"] = "~405 billion"
    elif "8b" in name_lower:
        model_info["parameters"] = "~8 billion"
    elif "22b" in name_lower:
        model_info["parameters"] = "~22 billion"
    elif "65b" in name_lower:
        model_info["parameters"] = "~65 billion"
    
    # Infer architecture family
    if "llama" in name_lower:
        model_info["architecture"] = "Llama (Transformer)"
        if "llama-3" in name_lower or "llama3" in name_lower:
            model_info["context_length"] = "8,192 tokens"
        elif "llama-2" in name_lower or "llama2" in name_lower:
            model_info["context_length"] = "4,096 tokens"
        else:
            model_info["context_length"] = "2,048 tokens"
    elif "mistral" in name_lower:
        model_info["architecture"] = "Mistral (Transformer)"
        model_info["context_length"] = "32,768 tokens"
    elif "gemma" in name_lower:
        model_info["architecture"] = "Gemma (Transformer)"
        model_info["context_length"] = "8,192 tokens"
    elif "gpt" in name_lower:
        model_info["architecture"] = "GPT (Transformer)"
        if "gpt-4" in name_lower:
            model_info["context_length"] = "8,192 tokens"
        elif "gpt-3.5" in name_lower:
            model_info["context_length"] = "4,096 tokens"
    elif "claude" in name_lower:
        model_info["architecture"] = "Claude (Transformer)"
        model_info["context_length"] = "200,000 tokens"
    elif "qwen" in name_lower:
        model_info["architecture"] = "Qwen (Transformer)"
        model_info["context_length"] = "32,768 tokens"
    elif "phi" in name_lower:
        model_info["architecture"] = "Phi (Transformer)"
        model_info["context_length"] = "4,096 tokens"
    elif "falcon" in name_lower:
        model_info["architecture"] = "Falcon (Transformer)"
        model_info["context_length"] = "2,048 tokens"

def _parse_model_args(model_info: Dict[str, Any], model_args: str) -> None:
    """Parse model arguments string into structured information."""
    args = model_args.split(',')
    
    for arg in args:
        arg = arg.strip()
        if '=' in arg:
            key, value = arg.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Map model arguments to model_info fields
            if key == "device_map":
                if value == "auto":
                    model_info["device_mapping"] = "Multi-GPU (Auto)"
                    model_info["device_map"] = "auto"
                else:
                    model_info["device_map"] = value
            elif key == "torch_dtype":
                model_info["torch_dtype"] = value
                model_info["data_type"] = value
            elif key == "dtype":
                model_info["data_type"] = value
            elif key == "load_in_4bit":
                if value.lower() == "true":
                    model_info["quantization"] = "4-bit"
            elif key == "load_in_8bit":
                if value.lower() == "true":
                    model_info["quantization"] = "8-bit"
            elif key == "quantization":
                model_info["quantization"] = value
            elif key == "tensor_parallel_size":
                model_info["tensor_parallel_size"] = int(value)
                if int(value) > 1:
                    model_info["device_mapping"] = f"Multi-GPU (TP={value})"
            elif key == "pipeline_parallel_size":
                model_info["pipeline_parallel_size"] = int(value)
            elif key == "gpu_memory_utilization":
                model_info["gpu_memory_utilization"] = f"{float(value):.2f}"
            elif key == "max_model_len":
                model_info["max_model_len"] = value
                model_info["context_length"] = f"{value} tokens"
            elif key == "trust_remote_code":
                model_info["trust_remote_code"] = value
            elif key == "revision":
                model_info["revision"] = value
            elif key == "use_flash_attention_2":
                if value.lower() == "true":
                    model_info["use_flash_attention"] = "True"
                    model_info["attention_implementation"] = "flash_attention_2"
            elif key == "attn_implementation":
                model_info["attention_implementation"] = value
            elif key == "low_cpu_mem_usage":
                model_info["low_cpu_mem_usage"] = value
            elif key == "use_cache":
                model_info["use_cache"] = value
            elif key == "cache_dir":
                model_info["cache_dir"] = value
            elif key == "local_files_only":
                model_info["local_files_only"] = value
            elif key == "offload_folder":
                model_info["offload_folder"] = value
            elif key == "peft":
                model_info["peft_config"] = value
            elif key == "swap_space":
                model_info["swap_space"] = value
            elif key == "enable_lora":
                model_info["enable_lora"] = value
            elif key == "max_lora_rank":
                model_info["max_lora_rank"] = value
            elif key == "seed":
                model_info["seed"] = value
            elif key == "download_dir":
                model_info["download_dir"] = value
            elif key == "load_format":
                model_info["load_format"] = value

def _parse_generation_args(model_info: Dict[str, Any], gen_args: Dict[str, Any]) -> None:
    """Parse generation arguments into model_info."""
    for key, value in gen_args.items():
        if key == "temperature":
            model_info["temperature"] = str(value)
        elif key == "top_p":
            model_info["top_p"] = str(value)
        elif key == "top_k":
            model_info["top_k"] = str(value)
        elif key == "max_tokens":
            model_info["max_tokens"] = str(value)
        elif key == "max_new_tokens":
            model_info["max_new_tokens"] = str(value)
        elif key == "do_sample":
            model_info["do_sample"] = str(value)
        elif key == "num_beams":
            model_info["num_beams"] = str(value)
        elif key == "repetition_penalty":
            model_info["repetition_penalty"] = str(value)
        elif key == "length_penalty":
            model_info["length_penalty"] = str(value)
        elif key == "early_stopping":
            model_info["early_stopping"] = str(value)

def get_model_architecture_info(model_name: str) -> Dict[str, str]:
    """
    Get detailed architecture information for common model families.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary with architecture details
    """
    name_lower = model_name.lower()
    
    if "llama" in name_lower:
        return {
            "family": "LLaMA",
            "attention": "Multi-head attention with RMSNorm",
            "activation": "SwiGLU",
            "positional_encoding": "RoPE (Rotary Position Embedding)",
            "vocab_size": "32,000 (LLaMA-1) / 32,016 (LLaMA-2)",
            "architecture_type": "Decoder-only Transformer"
        }
    elif "mistral" in name_lower:
        return {
            "family": "Mistral",
            "attention": "Grouped-query attention (GQA) with sliding window",
            "activation": "SwiGLU",
            "positional_encoding": "RoPE (Rotary Position Embedding)",
            "vocab_size": "32,000",
            "architecture_type": "Decoder-only Transformer",
            "special_features": "Sliding window attention (4096 tokens)"
        }
    elif "gemma" in name_lower:
        return {
            "family": "Gemma",
            "attention": "Multi-query attention with RMSNorm",
            "activation": "GeGLU",
            "positional_encoding": "RoPE (Rotary Position Embedding)",
            "vocab_size": "256,000",
            "architecture_type": "Decoder-only Transformer"
        }
    elif "gpt" in name_lower:
        return {
            "family": "GPT",
            "attention": "Multi-head attention",
            "activation": "GELU",
            "positional_encoding": "Learned positional embeddings",
            "architecture_type": "Decoder-only Transformer"
        }
    else:
        return {
            "family": "Unknown",
            "attention": "Not specified",
            "activation": "Not specified", 
            "positional_encoding": "Not specified",
            "architecture_type": "Transformer (assumed)"
        } 
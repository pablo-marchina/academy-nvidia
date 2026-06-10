# TensorRT-LLM

## Product
TensorRT-LLM

## Gaps Addressed
- high_inference_cost
- high_latency

## Description
TensorRT-LLM is an open-source library that optimizes large language model
inference on NVIDIA GPUs. It uses kernel fusion, quantization (FP8, INT4,
INT8), and in-flight batching to maximize throughput and minimize latency.
TensorRT-LLM is the recommended inference backend for LLMs in production.

## Keywords
LLM, inference, optimization, kernel fusion, quantization, throughput, latency, TensorRT

## Use Cases
- Reducing LLM inference cost by up to 4x through quantization
- Achieving sub-100ms latency for production LLM endpoints
- Serving multiple models efficiently with in-flight batching
- Benchmarking and comparing inference performance across GPU configurations

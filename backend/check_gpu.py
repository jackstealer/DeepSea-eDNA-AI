import torch

print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"Current Device: {torch.cuda.current_device()}")
    
    # Test tensor on GPU
    x = torch.rand(5, 3).cuda()
    print(f"\nTest tensor on GPU: {x.device}")
    print("✓ GPU is ready for training!")
else:
    print("✗ CUDA not available, will use CPU")

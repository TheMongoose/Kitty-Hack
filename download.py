import os
from huggingface_hub import snapshot_download

# Enable hf_transfer for faster downloads
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1" 

repo_id = "unsloth/gemma-3-4b-it-GGUF" # Or "tensorblock/gemma-3-4b-it-GGUF"
local_dir = "/home/konrad/Kitty/" # Your desired download directory


file_to_download = "gemma-3-4b-it-Q4_K_M.gguf" 

print(f"Downloading {file_to_download} from {repo_id} to {local_dir}...")
snapshot_download(
    repo_id=repo_id, 
    local_dir=local_dir, 
    allow_patterns=[file_to_download]
)
print("Download complete!")

# Now you can use this path in your Llama constructor
model_path = os.path.join(local_dir, file_to_download)
print(f"Model path: {model_path}")

# Your Llama initialization would then use this model_path
# llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1)
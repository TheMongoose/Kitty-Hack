import os
from huggingface_hub import snapshot_download

# Enable hf_transfer for faster downloads
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1" 

repo_id = "unsloth/gemma-3-4b-it-GGUF" # Or "tensorblock/gemma-3-4b-it-GGUF"


file_to_download = "gemma-3-4b-it-Q4_K_M.gguf" 

snapshot_download(
    local_dir='',
    repo_id=repo_id, 
    allow_patterns=[file_to_download]
)
print("Download complete!")

# Your Llama initialization would then use this model_path
# llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1)

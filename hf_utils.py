import os
import re
import subprocess
from typing import Optional

def discover_hf_endpoint() -> Optional[str]:
    """
    Discover the Hugging Face Space endpoint automatically.
    Priority:
    1. Environment var `HF_ENDPOINT`
    2. `HF_USERNAME` + `HF_SPACE` → https://<username>-<space>.hf.space
    3. Git remote `hf` (or any remote) pointing to huggingface.co/spaces/<username>/<space>

    Returns the endpoint URL, or None if it cannot be determined.
    """
    # 1. Direct env var
    env_endpoint = os.getenv("HF_ENDPOINT")
    if env_endpoint:
        return env_endpoint.strip()

    # 2. Username + space
    username = os.getenv("HF_USERNAME")
    space = os.getenv("HF_SPACE")
    if username and space:
        return f"https://{username.lower()}-{space.lower()}.hf.space"

    # 3. Parse git remotes
    try:
        out = subprocess.check_output(["git", "remote", "-v"], text=True)
        # Look for huggingface spaces remote lines
        # e.g., https://huggingface.co/spaces/MathCsAi/llm-quiz-solver (fetch)
        m = re.search(r"huggingface\.co/spaces/([\w-]+)/([\w-]+)", out)
        if m:
            user = m.group(1).lower()
            sp = m.group(2).lower()
            return f"https://{user}-{sp}.hf.space"
    except Exception:
        pass

    return None

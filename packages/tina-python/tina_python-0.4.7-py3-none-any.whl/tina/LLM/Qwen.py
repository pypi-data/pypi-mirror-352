from .api import BaseAPI

class Qwen(BaseAPI):
    # API_ENV_VAR_NAME = "DASHSCOPE_API_KEY"  # 重写API key环境变量名称
    # BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"  # 重写base_url

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        super().__init__(api_key=api_key, model=model, base_url=base_url)
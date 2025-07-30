# 环境变量配置指南

## 必需的环境变量

为了使用不同的LLM模型，你需要设置相应的API密钥环境变量：

### 1. OpenAI 模型 (GPT-3, GPT-4, GPT-o1)
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_BASE_URL="http://api.xunxkj.cn/v1"  # 可选，使用默认值
```

### 2. Qwen 模型 (Qwen-max, Qwen-plus, Qwen-turbo, Qwen-long)
```bash
export QWEN_API_KEY="your_qwen_api_key_here"
export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 可选，使用默认值
```

### 3. DeepSeek 模型
```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
export DEEPSEEK_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 可选，使用默认值
```

## 可选的环境变量

### 4. HKUST API (仅在 UST=True 时需要)
```bash
export HKUST_API_TOKEN="your_hkust_api_token_here"
```

### 5. RAG 功能
```bash
export RAG_API_KEY="your_rag_api_key_here"
export RAG_APP_ID="your_rag_app_id_here"
export RAGFLOW_API_KEY="your_ragflow_api_key_here"
```

### 6. Grok 模型
```bash
export GROK_API_KEY="your_grok_api_key_here"
```

### 7. BC API
```bash
export BC_API_KEY="your_bc_api_key_here"
```

## 设置方法

### 方法1: 临时设置 (当前终端会话)
```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

### 方法2: 永久设置 (添加到 shell 配置文件)
将环境变量添加到 `~/.bashrc`, `~/.zshrc` 或 `~/.profile`:
```bash
echo 'export OPENAI_API_KEY="sk-your-actual-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 方法3: 使用 .env 文件
创建一个 `.env` 文件在项目根目录：
```
OPENAI_API_KEY=sk-your-actual-key-here
QWEN_API_KEY=sk-your-actual-key-here
DEEPSEEK_API_KEY=sk-your-actual-key-here
```

然后在Python代码中使用 python-dotenv 加载：
```python
from dotenv import load_dotenv
load_dotenv()
```

## 验证设置
运行以下Python代码来验证环境变量是否正确设置：
```python
import os
from apexllm.core import validate_api_keys

# 检查环境变量
print("OPENAI_API_KEY:", "✓" if os.getenv('OPENAI_API_KEY') else "✗")
print("QWEN_API_KEY:", "✓" if os.getenv('QWEN_API_KEY') else "✗")
print("DEEPSEEK_API_KEY:", "✓" if os.getenv('DEEPSEEK_API_KEY') else "✗")

# 验证API密钥
validate_api_keys()
```

## 安全注意事项

1. **永远不要**将API密钥硬编码在代码中
2. **永远不要**将包含API密钥的 `.env` 文件提交到版本控制系统
3. 添加 `.env` 到 `.gitignore` 文件中
4. 定期轮换你的API密钥
5. 对不同的项目使用不同的API密钥

## 常见错误

### 错误1: "API client not initialized"
**原因**: 对应的环境变量未设置
**解决**: 检查并设置正确的环境变量

### 错误2: "Missing environment variables"
**原因**: 必需的API密钥未设置
**解决**: 参考上面的设置方法配置相应的环境变量

### 错误3: 环境变量设置后仍然无法识别
**原因**: 环境变量可能没有正确加载
**解决**: 重启终端或重新source配置文件 
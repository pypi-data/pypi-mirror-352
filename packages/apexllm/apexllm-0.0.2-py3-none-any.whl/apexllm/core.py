# site librarys
import json
import time
import requests
import tiktoken
import os
from datetime import datetime
from enum import Enum
from openai import OpenAI
from json import loads
from dotenv import load_dotenv

load_dotenv()

class LLMMODEL(Enum):
    GPT_3 = 'gpt-3.5-turbo'
    GPT_4 = 'gpt-4o'
    GPT_o1 = 'o1-mini'
    Qwen_max = 'qwen-max'
    Qwen_plus = 'qwen-plus'
    Qwen_turbo = 'qwen-turbo'
    Qwen_long = 'qwen-long'
    Deepseek_r1 = 'deepseek-r1'

# API Keys from environment variables
BC_key = os.getenv('BC_API_KEY', '')
Rag_KEY = os.getenv('RAGFLOW_API_KEY', '')
Openai_key = os.getenv('OPENAI_API_KEY', '')
Qwen_api_key = os.getenv('QWEN_API_KEY', '')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')

# Base URLs - can also be made configurable via environment variables
deepseek_baseURL = os.getenv('DEEPSEEK_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
openai_baseURL = os.getenv('OPENAI_BASE_URL', 'http://api.xunxkj.cn/v1')
qwen_baseURL = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

# Validate required API keys
def validate_api_keys():
    """Validate that required API keys are set"""
    missing_keys = []
    
    if not Openai_key:
        missing_keys.append('OPENAI_API_KEY')
    if not Qwen_api_key:
        missing_keys.append('QWEN_API_KEY')
    if not deepseek_api_key:
        missing_keys.append('DEEPSEEK_API_KEY')
    
    if missing_keys:
        print(f"\033[91mWarning: Missing environment variables: {', '.join(missing_keys)}\033[0m")
        print("Please set these environment variables before using the corresponding models.")
    
    return len(missing_keys) == 0

# clients - only initialize if keys are available
openai_client = None
qwen_client = None
deepseek_client = None

if Openai_key:
    openai_client = OpenAI(api_key=Openai_key, base_url=openai_baseURL)

if Qwen_api_key:
    qwen_client = OpenAI(api_key=Qwen_api_key, base_url=qwen_baseURL)

if deepseek_api_key:
    deepseek_client = OpenAI(api_key=deepseek_api_key, base_url=deepseek_baseURL)


def generate(template, output_format, generateModel: LLMMODEL, isJson: bool):
    """Main function to generate responses using different LLM models"""
    print(f"\033[92mProcessing with {generateModel.value}...\033[0m")
    start_time = datetime.now()
    try:
        if not isJson:
            if generateModel in [LLMMODEL.Qwen_long, LLMMODEL.Qwen_max, LLMMODEL.Qwen_plus, LLMMODEL.Qwen_turbo]:
                result = QwenLLM(generateModel, template)
            elif generateModel in [LLMMODEL.GPT_4, LLMMODEL.GPT_o1, LLMMODEL.GPT_3]:
                result = GPTLLM(generateModel, template, output_format)  
            elif generateModel in [LLMMODEL.Deepseek_r1]:
                result = DeepseekLLM(generateModel, template, output_format)
            else:
                raise ValueError(f"Unsupported model: {generateModel}")
        else:
            if generateModel in [LLMMODEL.Qwen_long, LLMMODEL.Qwen_max, LLMMODEL.Qwen_plus, LLMMODEL.Qwen_turbo]:
                result = QwenLLM_json(generateModel, template, output_format)
            elif generateModel in [LLMMODEL.GPT_4, LLMMODEL.GPT_3]:
                result = GPTLLM_json(generateModel, template, output_format)  
            elif generateModel in [LLMMODEL.GPT_o1]:
                raw_result = GPTLLM(model=generateModel, template=template, output_format=output_format)
                result = extract_json(raw_result=raw_result, output_format=output_format)
            elif generateModel in [LLMMODEL.Deepseek_r1]:
                result, reasoning = DeepseekLLM_json(
                    deepseek_model=LLMMODEL.Deepseek_r1,
                    qwen_model=LLMMODEL.Qwen_plus,
                    template=template,
                    output_format=output_format
                )
            else:
                raise ValueError(f"Unsupported model: {generateModel}")
            
        response_time = (datetime.now() - start_time).total_seconds()
        print(f"\033[92m{generateModel.value} processing completed in {response_time:.2f}s\033[0m")
        return result
    except Exception as e:
        print(f"\033[91mError in generate function: {e}\033[0m")
        raise


def extract_json(raw_result, output_format):
    """Extract JSON from raw result using GPT-4"""
    dialogue_history = f"Please convert the following content into a valid JSON format. The content to convert is:\n{raw_result},\n"
    refined_json = GPTLLM_json(model=LLMMODEL.GPT_4, template=dialogue_history, output_format=output_format)
    return refined_json


def calculate_token(prompt):
    """Calculate token count for a given prompt"""
    encoding = tiktoken.encoding_for_model("gpt-4-turbo")
    tokens = encoding.encode(prompt)
    return len(tokens)


def QwenLLM(model: LLMMODEL, prompt):
    """Generate response using Qwen models"""
    if not qwen_client:
        raise ValueError("Qwen client not initialized. Please set QWEN_API_KEY environment variable.")
    
    start_time = datetime.now()
    
    completion = qwen_client.chat.completions.create(
        model=model.value,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ]
    )
    
    end_time = datetime.now()
    response_time = (end_time - start_time).total_seconds()
    result = completion.choices[0].message.content
    print(f"Response Time: {response_time:.2f}s")
    return result


def QwenLLM_json(model: LLMMODEL, template, output_format, max_retry: int = 3, retry_delay: int = 5):
    """Generate JSON response using Qwen models with retry logic"""
    if not qwen_client:
        raise ValueError("Qwen client not initialized. Please set QWEN_API_KEY environment variable.")
    
    prompt = template + "\n strictly follow the json format as " + str(output_format) + " don't generate any \\ in your response, it would interfere the json transfer"
    start_time = datetime.now()

    for attempt in range(max_retry):
        try:
            completion = qwen_client.chat.completions.create(
                model=model.value,
                messages=[
                    {'role': 'system',
                     'content': "You are a helpful assistant, you will strictly follow the user's instructions to generate the required content"},
                    {'role': 'user', 'content': prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            json_string = completion.choices[0].message.content
                        
            if "\\" in json_string:
                print("Invalid content detected in JSON string:", json_string)
                raise ValueError("Invalid content detected in JSON string.")
            
            json_object = json.loads(json_string, strict=False)
            print(f"Response Time: {response_time:.2f}s")
            return json_object
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retry - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Failed to get a valid response.")
                raise e
        except Exception as e:
            print(f"LLM error: {e}")
            raise e


def GPTLLM(model: LLMMODEL, template, output_format, max_retries=3, retry_delay=15):
    """Generate response using GPT models"""
    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
    
    prompt = template + "\n strictly follow the json format as " + str(output_format)
    start_time = datetime.now()

    if model == LLMMODEL.GPT_4 or model == LLMMODEL.GPT_3:
        roles = [{"role": "system",
                  "content": "you are a helpful assistant, you will strictly follow the user's instructions to generate the required content"}]
    else:
        roles = [{"role": "assistant",
                  "content": "you are a helpful assistant, you will strictly follow the user's instructions to generate the required content"}]

    roles.append({"role": "user", "content": prompt})

    for attempt in range(max_retries):
        try:
            completion = openai_client.chat.completions.create(
                model=model.value,
                messages=roles,
            )
            
            result = completion.choices[0].message.content
            end_time = datetime.now()
            response_time = end_time - start_time
            return result
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Failed to get a valid response.")
                raise e


def GPTLLM_json(model: LLMMODEL, template, output_format, max_retries=3, retry_delay=15):
    """Generate JSON response using GPT models"""
    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
    
    prompt = template + "\n strictly follow the json format as " + str(output_format)
    start_time = datetime.now()

    for attempt in range(max_retries):
        try:
            if model == LLMMODEL.GPT_3 or model == LLMMODEL.GPT_4:
                role = 'system'
            else:
                role = 'assistant'
                
            completion = openai_client.chat.completions.create(
                response_format={"type": "json_object"},
                model=model.value,
                messages=[{"role": role,
                           "content": "you are a helpful assistant, you will strictly follow the user's instructions to generate the required content"},
                          {"role": "user", "content": prompt}]
            )
            
            result = json.loads(completion.choices[0].message.content)
            end_time = datetime.now()
            response_time = end_time - start_time
            return result
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Failed to get a valid response.")
                raise e


def DeepseekLLM(model: LLMMODEL, template, output_format, max_retries=3, retry_delay=15):
    """Generate response using Deepseek models"""
    prompt = template + "\n strictly follow the json format as " + str(output_format)
    start_time = datetime.now()

    if UST:
        url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
        hkust_token = os.getenv('HKUST_API_TOKEN', '')
        if not hkust_token:
            raise ValueError("HKUST API token not found. Please set HKUST_API_TOKEN environment variable.")
        
        headers = { 
            "Content-Type": "application/json", 
            "Authorization": hkust_token
        }
        data = { 
            "model": "DeepSeek-R1-671B",
            "messages": [{"role": "user", "content": prompt}], 
            "temperature": 0.7 
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        
        if '</think>' in content:
            result = content.split('</think>')[1]
            reasoning = content.split('</think>')[0]
            return result, reasoning
        else:
            return content, ""
    else: 
        if not deepseek_client:
            raise ValueError("Deepseek client not initialized. Please set DEEPSEEK_API_KEY environment variable.")
        
        for attempt in range(max_retries):
            try:
                response = deepseek_client.chat.completions.create(
                    model=model.value,
                    messages=[
                        {"role": "system",
                         "content": "you are a helpful assistant, you will strictly follow the user's instructions to generate the required content"},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )
                
                end_time = datetime.now()
                response_time = end_time - start_time
                
                raw_result = response.choices[0].message.content
                reasoning_result = getattr(response.choices[0].message, 'reasoning_content', '')
                
                if reasoning_result:
                    print("\033[93m" + reasoning_result + "\033[0m")
                
                return raw_result, reasoning_result
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Failed to get a valid response.")
                    raise e


def DeepseekLLM_json(deepseek_model: LLMMODEL, qwen_model: LLMMODEL, template, output_format) -> tuple:
    """Generate JSON response using Deepseek model and convert with Qwen"""
    result, reasoning_result = DeepseekLLM(
        model=deepseek_model,
        template=template,
        output_format=output_format
    )
    
    print(f"Raw result: {result}")
    dialogue_history = f"Please convert the following content into a valid JSON format. The content to convert is:\n{result},\n"

    json_result = QwenLLM_json(
        model=qwen_model,
        template=dialogue_history,
        output_format=output_format
    )
    
    print('Reasoning appended to result')
    return json_result, reasoning_result


def Researcher_rag(name, content):
    """RAG function for researcher - placeholder implementation"""
    # Note: This function requires the Application class which is not imported
    # You may need to import it from the appropriate library (e.g., from dashscope import Application)
    try:
        # Uncomment and modify the import below based on your actual RAG library
        # from dashscope import Application
        raise ImportError("Application import not configured")
        
        rag_api_key = os.getenv('RAG_API_KEY', '')
        rag_app_id = os.getenv('RAG_APP_ID', '')
        
        if not rag_api_key or not rag_app_id:
            raise ValueError("RAG_API_KEY and RAG_APP_ID environment variables must be set")
        
        biz_params = {"name": name, "content": content}
        response = Application.call(
            api_key=rag_api_key, 
            app_id=rag_app_id,
            prompt='请根据以下对话记录，提取出知识库中相关的文章段落',
            biz_params=biz_params
        )
        chunks = json.loads(str(response.output.text))['result']
        return chunks
    except ImportError:
        print("RAG Application not available - please configure the import")
        return []


def GORKLLM_json(template, output_format, output_schema):
    """Generate JSON response using Grok model"""
    grok_api_key = os.getenv('GROK_API_KEY', '')
    if not grok_api_key:
        raise ValueError("Grok API key not found. Please set GROK_API_KEY environment variable.")
    
    prompt = template + "\n strictly follow the json format as " + str(output_format)
    print(prompt)
    
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {grok_api_key}"
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant helps user so simulate the researcher's thought process to generate the required content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "grok-2-1212",
        "stream": False,
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": output_schema
        }
    }

    response = requests.post(url, headers=headers, json=data)
    result = json.loads(response.json()['choices'][0]['message']['content'])
    print(result)
    return result
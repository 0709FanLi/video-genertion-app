#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# --- 配置 ---
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-8b6db5929e244a159deb8e77b08bcf5b")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
WANX_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

# --- FastAPI 应用初始化 ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 模型定义 ---
class PromptGenerationRequest(BaseModel):
    idea: str

class ImageGenerationRequest(BaseModel):
    prompt: str

class VideoPromptOptimiseRequest(BaseModel):
    prompt: str

class VideoGenerationRequest(BaseModel):
    image_url: str
    prompt: str

# --- 阿里云API调用封装 ---

# 通义千问客户端
qw_client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=QWEN_BASE_URL,
)

# 异步任务轮询
def poll_task(task_id):
    url = f"{WANX_BASE_URL}/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to poll task: {response.text}")

        data = response.json()
        status = data.get("output", {}).get("task_status")

        if status == "SUCCEEDED":
            return data
        elif status == "FAILED":
            raise HTTPException(status_code=500, detail=f"Task failed: {data}")
        elif status in ["PENDING", "RUNNING"]:
            time.sleep(5)  # 轮询间隔
        else:
            raise HTTPException(status_code=500, detail=f"Unknown task status: {status}")

# --- API Endpoints ---

@app.post("/api/generate-image-prompts")
def generate_image_prompts(request: PromptGenerationRequest):
    try:
        completion = qw_client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个专业的提示词工程师。请将用户的想法扩展成3个详细的、用于AI绘画的英文提示词，包含场景描述、光线、画风、构图等细节，并以JSON格式返回。"},
                {"role": "user", "content": request.idea}
            ],
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-images")
def generate_images(request: ImageGenerationRequest):
    url = f"{WANX_BASE_URL}/services/aigc/text2image/image-synthesis"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    payload = {
        "model": "wanx-v1",
        "input": {"prompt": request.prompt},
        "parameters": {"n": 4, "size": "1024*1024"}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    task_id = response.json().get("output", {}).get("task_id")
    if not task_id:
        raise HTTPException(status_code=500, detail="Failed to create image generation task.")

    return poll_task(task_id)

@app.post("/api/optimise-video-prompt")
def optimise_video_prompt(request: VideoPromptOptimiseRequest):
    try:
        completion = qw_client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个专业的视频提示词工程师。请将用户的想法优化成一个更专业的、细节丰富的视频动态描述提示词，并以JSON格式返回。"},
                {"role": "user", "content": request.prompt}
            ],
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-video")
def generate_video(request: VideoGenerationRequest):
    url = f"{WANX_BASE_URL}/services/aigc/video-generation/video-synthesis"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    payload = {
        "model": "wan2.5-i2v-preview",
        "input": {
            "prompt": request.prompt,
            "img_url": request.image_url
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    task_id = response.json().get("output", {}).get("task_id")
    if not task_id:
        raise HTTPException(status_code=500, detail="Failed to create video generation task.")

    return poll_task(task_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


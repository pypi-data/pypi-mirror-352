#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : adapters
# @Time         : 2025/5/30 16:38
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.io.files_utils import to_url, to_url_fal
from meutils.schemas.openai_types import CompletionRequest
from meutils.schemas.image_types import ImageRequest
from meutils.llm.openai_utils import chat_completion, chat_completion_chunk, create_chat_completion_chunk

async def stream_to_nostream(
        request: CompletionRequest,
):
    pass

async def chat_for_image(
        generate: Callable,
        request: CompletionRequest,
):
    if request.last_user_content.startswith(  # 跳过nextchat
            (
                    "hi",
                    "使用四到五个字直接返回这句话的简要主题",
                    "简要总结一下对话内容，用作后续的上下文提示 prompt，控制在 200 字以内"
            )):
        return chat_completion

    prompt = request.last_user_content
    if request.last_urls:  # image_url
        urls = await to_url_fal(request.last_urls["image_url"], content_type="image/png")
        prompt = "\n".join(urls + [prompt])

    request = ImageRequest(
        model=request.model,
        prompt=prompt,
    )

    future_task = asyncio.create_task(generate(request))  # 异步执行

    async def gen():
        for i in f"> 🖌️正在绘画\n\n```json\n{request.model_dump_json(exclude_none=True)}\n```\n\n":
            await asyncio.sleep(0.05)
            yield i

        response = await future_task

        for image in response.data:
            yield f"![{image.revised_prompt}]({image.url})\n\n"

    chunks = create_chat_completion_chunk(gen(), redirect_model=request.model)
    return chunks

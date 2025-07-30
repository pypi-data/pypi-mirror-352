#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_siliconflow
# @Time         : 2024/6/26 10:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.llm.clients import OpenAI

# from openai import OpenAI


client = OpenAI(
    base_url=os.getenv("SOPHNET_BASE_URL"),
    # api_key=os.getenv("SOPHNET_API_KEY"),

    api_key="EZvbHTgRIFKQaRpT92kFVCnVZBJXuWCsqw89nAfZZQC5T4A_57QXba21ZKpVCIcBpFb-WBemZ7BNZdJjCHyn1A"

)

# EZvbHTgRIFKQaRpT92kFVCnVZBJXuWCsqw89nAfZZQC5T4A_57QXba21ZKpVCIcBpFb-WBemZ7BNZdJjCHyn1A

model = "DeepSeek-Prover-V2"
model = "DeepSeek-R1"
model = "DeepSeek-v3"

prompt = """
Complete the following Lean 4 code:\n\nlean4\nimport Mathlib\n\nopen Finset\n\n/-- For a set $S$ of nonnegative integers, let $r_S(n)$ denote the number of ordered pairs $(s_1, s_2)$ such that $s_1 \in S$, $s_2 \in S$, $s_1 \ne s_2$, and $s_1 + s_2 = n$. Is it possible to partition the nonnegative integers into two sets $A$ and $B$ in such a way that $r_A(n) = r_B(n)$ for all $n$?\n Prove that the answer is: Yes, such a partition is possible.-/\ntheorem omni_theorem_3521 :\n    ∃ A B : Set ℕ,\n      A ∪ B = ℕ ∧\n      A ∩ B = ∅ ∧\n      ∀ n : ℕ, {p : ℕ × ℕ | p.1 ∈ A ∧ p.2 ∈ A ∧ p.1 ≠ p.2 ∧ p.1 + p.2 = n}.ncard =\n        {p : ℕ × ℕ | p.1 ∈ B ∧ p.2 ∈ B ∧ p.1 ≠ p.2 ∧ p.1 + p.2 = n}.ncard := by\n\n\nBefore producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.\nThe plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
"""

messages = [
    {'role': 'user', 'content': prompt}
]
response = client.chat.completions.create(
    model=model,

    messages=messages,
    stream=True,
    max_tokens=10,
)
print(response)
# for chunk in response:
#     print(chunk)

class llama3:
    def __init__(self):
        pass
    def convert_messages_to_llama3_prompt(self, messages):
        prompt = "<|begin_of_text|>"
        for msg in messages:
            if msg.type == "system":
                prompt += f"<|start_header_id|>system<|end_header_id|>\n{msg.content}<|eot_id|>"
            elif msg.type == "human":
                prompt += f"<|start_header_id|>user<|end_header_id|>\n{msg.content}<|eot_id|>"
            elif msg.type == "assistant":
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n{msg.content}<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n"  # 답변 시작
        return prompt

import os
import torch
from typing import List, Dict, Any
from app.config import settings

class LLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.used_fallback = False
        self.is_loaded = False

    def load_model(self):
        if self.is_loaded:
            return

        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print(f"Loading base model: {settings.MODEL_NAME}")
        self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        device = "cuda" if torch.cuda.is_available() and settings.DEVICE == "cuda" else "cpu"
        
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.MODEL_NAME,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True
        )

        adapter_exists = os.path.exists(settings.ADAPTER_PATH) and os.path.exists(
            os.path.join(settings.ADAPTER_PATH, "adapter_config.json")
        )

        if adapter_exists:
            try:
                from peft import PeftModel
                print(f"Loading LoRA adapter from {settings.ADAPTER_PATH}")
                self.model = PeftModel.from_pretrained(self.model, settings.ADAPTER_PATH)
                self.used_fallback = False
            except Exception as e:
                print(f"Failed to load adapter: {e}")
                if not settings.ALLOW_BASE_MODEL_FALLBACK:
                    raise e
                self.used_fallback = True
        else:
            print("No LoRA adapter found. Running in Base-Model Fallback Mode.")
            self.used_fallback = True

        self.model.eval()
        self.is_loaded = True

    def generate_answer(self, question: str, retrieved_passages: List[Dict[str, Any]]) -> str:
        if not self.is_loaded:
            self.load_model()

        context_str = "\n\n".join([f"[Page {p['page_number']}]: {p['text']}" for p in retrieved_passages])
        system_prompt = (
            "You are FinExplain, a helpful financial assistant. Answer the question relying ONLY on "
            "the provided financial document passages below. If the information is missing or "
            "insufficient, state clearly: 'The uploaded report does not contain sufficient information to answer this question.' "
            "Do not invent facts or numbers."
        )

        user_content = f"Context Passages:\n{context_str}\n\nQuestion: {question}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        prompt_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt_text, return_tensors="pt")
        if torch.cuda.is_available() and settings.DEVICE == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=256, temperature=0.2, top_p=0.9, do_sample=False)

        response_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        answer = self.tokenizer.decode(response_tokens, skip_special_tokens=True).strip()
        return answer

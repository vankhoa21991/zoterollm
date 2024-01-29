import os

from torch import cuda, bfloat16
import transformers
import torch
from langchain.llms import HuggingFacePipeline
from langchain.llms import CTransformers
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer, pipeline
import time
class LLModel:
	def __init__(self):
		pass

	def load_llm_4bit(self, model_id, hf_auth, device='cuda:0'):
		bnb_config = transformers.BitsAndBytesConfig(
			load_in_4bit=True,
			bnb_4bit_quant_type='nf4',
			bnb_4bit_use_double_quant=True,
			bnb_4bit_compute_dtype=bfloat16
		)

		config = transformers.AutoConfig.from_pretrained(model_id, trust_remote_code=True)
		config.init_device = "cuda"

		model = transformers.AutoModelForCausalLM.from_pretrained(
			model_id, config=config, torch_dtype=torch.bfloat16, trust_remote_code=True,
			use_auth_token=hf_auth,
			quantization_config=bnb_config,
		)
		model.eval()

		tokenizer = transformers.AutoTokenizer.from_pretrained(
			model_id,
			use_auth_token=hf_auth
		)
		streamer = TextStreamer(tokenizer, skip_prompt=True)

		generate_text = transformers.pipeline(
			model=model,
			tokenizer=tokenizer,
			# return_full_text=True,  # langchain expects the full text
			task='text-generation',
			# we pass model parameters here too
			temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
			max_new_tokens=256,  # max number of tokens to generate in the output
			repetition_penalty=1.1,  # without this output begins repeating
			torch_dtype=torch.float16,
			device_map='auto',
			# streamer=streamer,
			# device='cuda:0'
		)

		llm = HuggingFacePipeline(pipeline=generate_text)
		return llm

	def load_llm(self, model_id, hf_auth=None, device='cuda:0'):
		config = transformers.AutoConfig.from_pretrained(model_id, trust_remote_code=True)
		config.init_device = "cuda"

		model = transformers.AutoModelForCausalLM.from_pretrained(
			model_id, config=config, torch_dtype=torch.bfloat16, trust_remote_code=True,
			use_auth_token=hf_auth,
		).to("cuda:0")
		model.eval()

		tokenizer = transformers.AutoTokenizer.from_pretrained(
			model_id,
			use_auth_token=hf_auth
		)

		generate_text = transformers.pipeline(
			model=model,
			tokenizer=tokenizer,
			return_full_text=True,  # langchain expects the full text
			task='text-generation',
			# we pass model parameters here too
			temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
			max_new_tokens=256,  # max number of tokens to generate in the output
			repetition_penalty=1.1,  # without this output begins repeating
			torch_dtype=torch.float16,
			device='cuda:0'
		)

		llm = HuggingFacePipeline(pipeline=generate_text)

		return llm

	def load_ctransformer(self):
		# load the llm with ctransformers
		model_path = '/home/vankhoa@median.cad/code/llm/zoterollm/models/llama-2-7b-chat.ggmlv3.q2_K.bin'
		# model_path = '/data/llm/Llama-2-7b-chat-hf/llama-2-7b-chat-hf.Q4_K_M.gguf'
		model_path = '/data/llm/llama-2-7b-chat.Q2_K.gguf'

		llm = CTransformers(model=model_path, # model available here: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main
		                model_type='llama',
		                config={'max_new_tokens': 256, 'temperature': 0.1, 'repetition_penalty':1.1},
		 				callbacks = [StreamingStdOutCallbackHandler()]
							)

		return llm

if __name__ == '__main__':
	llmodel = LLModel()

	template = """
	Context: {context}
	Question: {question}

		Answer: Let's think step by step."""
	prompt = PromptTemplate.from_template(template)

	question = "What is LLM?"

	t = time.time()
	# model = llmodel.load_llm(model_id='/data/llm/Llama-2-7b-chat-hf/',
	# 						 hf_auth=None,
	# 						 device='cuda:0')
	# chain = prompt | model
	#
	# print(chain.invoke({"question": question}))
	# print("Time taken: ", time.time()-t)

	model = llmodel.load_llm_4bit(model_id='/data/llm/Llama-2-7b-chat-hf/', hf_auth=None, device='cuda:0')
	chain = prompt | model

	chain.invoke({"question": question,
				  "context": "you are answering questions about large language model"})
	print("Time taken: ", time.time() - t)

	# model = llmodel.load_ctransformer()
	# # print(model(question))
	# # print("Time taken: ", time.time() - t)
	#
	# llm_chain = LLMChain(prompt=prompt, llm=model)
	# response = llm_chain.run(question=question,
	# 						 context="you are answering questions about large language model")
	# print("Time taken: ", time.time() - t)
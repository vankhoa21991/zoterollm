import os

MODEL_ID = 'meta-llama/Llama-2-7b-chat-hf'
QUANTIZATION_METHODS = ["q4_k_m", "q5_k_m"]
QUANTIZATION_METHODS = ["q2_k"]

# Constants
MODEL_NAME = MODEL_ID.split('/')[-1]

fp16 = f"{MODEL_NAME}/{MODEL_NAME.lower()}.fp16.bin"
commannd = f"python /home/vankhoa@median.cad/code/llm/llama.cpp/convert.py /data/llm/{MODEL_NAME} --outtype f16 --outfile /data/llm/{fp16}"
# os.system(commannd)

for method in QUANTIZATION_METHODS:
	qtype = f"/data/llm/{MODEL_NAME}/{MODEL_NAME.lower()}.{method.upper()}.gguf"
	command = f"/home/vankhoa@median.cad/code/llm/llama.cpp/build/bin/quantize /data/llm/{fp16} {qtype} {method}"
	os.system(command)

model_list = [file for file in os.listdir(f'/data/llm/{MODEL_NAME}') if "gguf" in file]
print("List of models: " + ", ".join(model_list))
prompt = 'who is Elon Musk?'
chosen_method = model_list[0]

qtype = f"{MODEL_NAME}/{MODEL_NAME.lower()}.{method.upper()}.gguf"
command = f'/home/vankhoa@median.cad/code/llm/llama.cpp/build/bin/main -m /data/llm/{qtype} -n 128 --color -ngl 35 -p "{prompt}"'
os.system(command)
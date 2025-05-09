import time
from ollama import chat, ChatResponse

start_time = time.time()
response: ChatResponse = chat(model="deepseek-r1:7b", messages=[
# response: ChatResponse = chat(model="granite3.2:8b", messages=[
    {
        "role": "system",
        "content": "only answer with yes or no. is this url malicious ? https://divineenterprises.net HTTP/2.0, no need explanation"
    }
])

end_time = time.time()
elapsed_time = end_time - start_time
print(response['message']['content'])
print(f"Time elapsed: {elapsed_time:.2f} seconds")


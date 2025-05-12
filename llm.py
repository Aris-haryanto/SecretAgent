import time
from ollama import chat, ChatResponse

def helpAI(url):
    start_time = time.time()
    # response: ChatResponse = chat(model="deepseek-r1:7b", messages=[
    response: ChatResponse = chat(model="granite3.2:8b", messages=[
        {
            "role": "system",
            "content": f"only answer with 'this malicious url' or 'this safe url', , no need explanation. is this url malicious ? {url}"
        }
    ])

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    return response['message']['content']
    



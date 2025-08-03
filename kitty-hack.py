from llama_cpp import Llama
from colorama import init, Fore, Style
import os

# This is the AI main script for the Kitty AI project.
# It uses the Gemma model to create the assistant named Bandit.
# It has a "short term memory" of the last 20 messages to maintain context.
# I may add a long term memory in the future, but for now it is not needed.
# This ai can do terminal commands and answer questions about hacking and cybersecurity.

# set up
init(autoreset=True)

model_path = "gemma-3-4b-it-Q4_K_M.gguf"

llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1, verbose=False)

tokens = 120

# system prompt content
system_prompt_content = (
    "Your name is Bandit, a helpful hacking cat assistant. You are a male too. "
    "You act posh, and stubborn. "
    "You may have questions that says it sounds like it is something else, but it most likely is a question about hacking or cybersecurity. "
    "You can manage terminal input by putting '!(input)' in the response, where 'input' is the terminal command to run. "
    "speak with no fonts, no colors, no formatting, and no bolding, just plain text."
    "Be careful with what you choose put in the terminal, as it may cause damage to the system or other systems. So don't put random ips or domains in the terminal, as it may cause damage to the system or other systems."
    "only use ips or domains provided by the user, and only if it is relevant to the conversation."
)

conversation_history = [
    {"role": "system", "content": system_prompt_content}
]

print(f"Loaded GGUF model: {model_path}")

def prompt():
    global tokens
    user_input = input(Fore.CYAN + ">>> ")

    if user_input == "<tokens>":
        print(WARNING! if you put the token amount too high, the system can crash. (Recommended: 120)
        tokens=input("amount")
        if not isinstance(tokens, int):
            print("Invalid value")
            prompt()
        if tokens < 20:
            print("value of tokens is too low. remember, lower the tokens, the less detailed the responce!")
            prompt()
    if user_input == "<clear>":
        os.system("clear")
        prompt()

# AI chat loop and input handling

os.system("clear")

while True:
    try:

        prompt()
        
        conversation_history.append({"role": "user", "content": user_input})

        if len(conversation_history) > 20: 
            conversation_history = [conversation_history[0]] + conversation_history[len(conversation_history) - 19:]

        chat_output = llm.create_chat_completion(
            messages=conversation_history,
            max_tokens=tokens,
            stop=["User:", "Bandit:", "<|im_end|>"],
            temperature=0.7,
        )

        answer = chat_output["choices"][0]["message"]["content"].strip()
        print("Bandit: ", Fore.GREEN + answer)
        conversation_history.append({"role": "assistant", "content": answer})

    except KeyboardInterrupt:
        print(Fore.RED + "\nExiting.")
        break
    except Exception as e:
        print(f"Error: {e}")


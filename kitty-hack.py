from llama_cpp import Llama
from colorama import init, Fore, Style
import os
import re
import subprocess
import json

init(autoreset=True)

model_path = "gemma-3-4b-it-Q4_K_M.gguf"

llm = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=-1, verbose=False)

tokens = 120
HISTORY_FILE = "bandit_history.json"

system_prompt_content = (
    "Your name is Bandit, a helpful hacking cat assistant. You are a male too. "
    "You act posh, and stubborn. "
    "You may have questions that says it sounds like it is something else, but it most likely is a question about hacking or cybersecurity. "
    "To provide terminal commands, you **MUST** enclose them with the EXACT starting symbol `!(` and the EXACT ending symbol `)!`. "
    "**Place the exact, executable command directly between the `!(` and `)!` symbols, with NO surrounding quotes (single, double, or backticks), and NO extra spaces immediately inside or outside these specific symbols.** "
    "For example, if the user asks to list files, your response should be: `A simple 'ls -la' will do. !(ls -la)!` "
    "Another example: `To check current working directory: !(pwd)!`. "
    "The command must always be wrapped by these precise five characters at the start `!(` and these precise two characters at the end `)!`. "
    "You are working on a Linux system. "
    "When a command is executed, you will be provided with its output formatted as: "
    "`<TOOL_CODE>`\n[command output here]\n`</TOOL_CODE>`. "
    "Analyze this output and use it to inform your next response to the user. "
    "If you provide a command, you should generally expect to receive its output next, and then formulate a response based on that output to the user. "
    "speak with no fonts, no colors, no formatting, and no bolding, just plain text."
    "Be careful with what you choose put in the terminal, as it may cause damage to the system or other systems. So don't put random ips or domains in the terminal, as it may cause damage to the system or other systems."
    "only use ips or domains provided by the user, and only if it is relevant to the conversation."
    "try to keep responces simple and short"
)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("No saved history found.")
        return None

print(f"Loaded GGUF model: {model_path}")
load_prev = input("Load previous session? (y/n): ").lower()
if load_prev == 'y':
    loaded = load_history()
    if loaded:
        conversation_history = loaded
        print(f"Loaded conversation history with {len(conversation_history)} entries.")
    else:
        conversation_history = [{"role": "system", "content": system_prompt_content}]
        print("Starting new session.")
else:
    conversation_history = [{"role": "system", "content": system_prompt_content}]
    print("Starting new session.")

command_pattern = re.compile(r'!\((.*?)\)!')

def prompt_user_input():
    global tokens
    user_input = input(Fore.CYAN + ">>> ")

    if user_input == "/tokens":
        print("WARNING! if you put the token amount too high, the system can crash. (Recommended: 120)")
        tokens_input = input("amount: ")

        try:
            tokens = int(tokens_input)
        except ValueError:
            print("Invalid value")

        if tokens < 20:
            print("value of tokens is too low. remember, lower the tokens, the less detailed the responce!")
        return prompt_user_input()

    if user_input == "/clear":
        os.system("clear")
        return prompt_user_input()
    if user_input == "/clearmemory":
        os.system("rm bandit_history.json")
        return prompt_user_input()

    return user_input

def process_ai_response_for_commands(ai_response_text):
    commands_to_suggest = command_pattern.findall(ai_response_text)
    outputs_for_ai = []

    if commands_to_suggest:
        print(Fore.YELLOW + "\n--- Suggested Commands (REVIEW BEFORE RUNNING!) ---")
        cleaned_commands = []
        for i, cmd in enumerate(commands_to_suggest):
            cleaned_cmd = cmd.replace('`', '').strip()
            cleaned_commands.append(cleaned_cmd)
            print(f"  [{i+1}] {cleaned_cmd}")

        print(Fore.YELLOW + "--------------------------------------------------")
        print(Fore.RED + "WARNING: AI-generated commands can be dangerous. Only run if you understand and trust them.")

        for cmd_to_execute in cleaned_commands:
            confirm = input(Fore.MAGENTA + f"Execute command '{cmd_to_execute}'? (y/n): " + Style.RESET_ALL).lower()
            if confirm == 'y':
                print(Fore.BLUE + f"Executing: {cmd_to_execute}" + Style.RESET_ALL)
                print(Fore.YELLOW + f"DEBUG: Command sent to shell: '{cmd_to_execute}'" + Style.RESET_ALL)

                try:
                    result = subprocess.run(
                        cmd_to_execute,
                        shell=True,
                        capture_output=True,
                        text=True,
                        check=False
                    )

                    command_output_content = ""
                    if result.stdout:
                        print(Fore.CYAN + "Command Output (stdout):\n" + Style.RESET_ALL + result.stdout)
                        command_output_content += f"STDOUT:\n{result.stdout}\n"
                    if result.stderr:
                        print(Fore.RED + "Command Error (stderr):\n" + Style.RESET_ALL + result.stderr)
                        command_output_content += f"STDERR:\n{result.stderr}\n"

                    if result.returncode != 0:
                        print(Fore.RED + f"Command exited with non-zero status: {result.returncode}" + Style.RESET_ALL)
                        command_output_content += f"RETURN CODE: {result.returncode}\n"
                    else:
                        print(Fore.GREEN + "Command executed successfully." + Style.RESET_ALL)
                        command_output_content += f"RETURN CODE: {result.returncode} (Success)\n"

                    outputs_for_ai.append({
                        "command": cmd_to_execute,
                        "output": command_output_content.strip()
                    })

                except FileNotFoundError:
                    print(Fore.RED + f"Error: Command not found - '{cmd_to_execute}'" + Style.RESET_ALL)
                    outputs_for_ai.append({
                        "command": cmd_to_execute,
                        "output": "ERROR: Command not found on system."
                    })
                except Exception as e:
                    print(Fore.RED + f"An unexpected error occurred during command execution: {e}" + Style.RESET_ALL)
                    outputs_for_ai.append({
                        "command": cmd_to_execute,
                        "output": f"ERROR: An unexpected error occurred: {e}"
                    })
            else:
                print(Fore.YELLOW + f"Skipped execution of: {cmd_to_execute}" + Style.RESET_ALL)

    return outputs_for_ai

os.system("clear")

def token_estimate(text):
    return int(len(text.split()) * 1.2)

while True:
    try:
        # Flag to control whether we need new user input or are processing command output
        should_get_user_input = True
        command_output_feedback = None

        if 'last_command_output' in locals() and last_command_output:
            # If there's pending command output from the previous iteration,
            # use that as the input for this turn's AI processing.
            combined_output_message = "I executed the following command(s) and here are the results:\n"
            for item in last_command_output:
                combined_output_message += f"\n--- Command: `{item['command']}` ---\n"
                combined_output_message += f"<TOOL_CODE>\n{item['output']}\n</TOOL_CODE>\n"
            command_output_feedback = combined_output_message.strip()
            should_get_user_input = False # Don't ask user for input yet

        if should_get_user_input:
            user_input = prompt_user_input()
            if not user_input:
                continue
            conversation_history.append({"role": "user", "content": user_input})
        else:
            conversation_history.append({"role": "user", "content": command_output_feedback})
            print(Fore.YELLOW + "Command outputs sent to AI for context." + Style.RESET_ALL)
            last_command_output = None # Clear the pending output


        if len(conversation_history) >= 2 and conversation_history[-1]["role"] == conversation_history[-2]["role"]:
            print(Fore.RED + "WARNING: Detected consecutive roles. Fixing history." + Style.RESET_ALL)
            conversation_history.pop(-2)

        if len(conversation_history) > 20:
            conversation_history = [conversation_history[0]] + conversation_history[-19:]

        if token_estimate(conversation_history[-1]["content"]) > (4096 - tokens - 100):
            print(Fore.YELLOW + "Warning: The last message was too long for the model context and has been excluded." + Style.RESET_ALL)
            conversation_history.pop()
            if not conversation_history:
                print(Fore.RED + "Error: Conversation history is empty after trimming. Resetting." + Style.RESET_ALL)
                conversation_history = [{"role": "system", "content": system_prompt_content}]
                continue

        chat_output = llm.create_chat_completion(
            messages=conversation_history,
            max_tokens=tokens,
            stop=["User:", "Bandit:", "<|im_end|>"],
            temperature=0.7,
        )

        ai_response = chat_output["choices"][0]["message"]["content"].strip()
        print("Bandit: ", Fore.GREEN + ai_response)
        conversation_history.append({"role": "assistant", "content": ai_response})

        executed_commands = process_ai_response_for_commands(ai_response)

        if executed_commands:
            # Store the output to be processed in the *next* iteration
            last_command_output = executed_commands
            save_history(conversation_history) # Save history immediately after AI response and before looping back for command output
        else:
            last_command_output = None # No commands executed, so no pending output
            save_history(conversation_history) # Save history if no commands were executed

    except KeyboardInterrupt:
        print(Fore.RED + "\nExiting.")
        break
    except Exception as e:
        print(f"Error: {e}")

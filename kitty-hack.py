from llama_cpp import Llama
from colorama import init, Fore, Style
import os
import re
import subprocess

init(autoreset=True)

model_path = "gemma-3-4b-it-Q4_K_M.gguf"

llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1, verbose=False)

tokens = 120

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

conversation_history = [
    {"role": "system", "content": system_prompt_content}
]

print(f"Loaded GGUF model: {model_path}")

def prompt_user_input():
    global user_input
    global tokens
    user_input = input(Fore.CYAN + ">>> ")

    if user_input == "/tokens":
        print("WARNING! if you put the token amount too high, the system can crash. (Recommended: 120)")
        tokens=input("amount: ")

        try:
            tokens = int(tokens)
        except ValueError:
            print("Invalid value")

        if tokens < 20:
            print("value of tokens is too low. remember, lower the tokens, the less detailed the responce!")
        prompt_user_input()

    if user_input == "/clear":
        os.system("clear")
        prompt_user_input()

os.system("clear")

command_pattern = re.compile(r'!\((.*?)\)!')

while True:
    try:
        prompt_user_input()
        conversation_history.append({"role": "user", "content": user_input})

        if len(conversation_history) > 20:
            conversation_history = [conversation_history[0]] + conversation_history[len(conversation_history) - 19:]

        chat_output = llm.create_chat_completion(
            messages=conversation_history,
            max_tokens=tokens,
            stop=["User:", "Bandit:", "<|im_end|>"],
            temperature=0.7,
        )

        initial_ai_answer = chat_output["choices"][0]["message"]["content"].strip()
        print("Bandit: ", Fore.GREEN + initial_ai_answer)
        conversation_history.append({"role": "assistant", "content": initial_ai_answer})

        # This block now becomes a function to avoid code duplication
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

        # Process commands from the initial AI answer
        executed_command_outputs = process_ai_response_for_commands(initial_ai_answer)

        if executed_command_outputs:
            combined_output_message = "I executed the following command(s) and here are the results:\n"
            for item in executed_command_outputs:
                combined_output_message += f"\n--- Command: `{item['command']}` ---\n"
                combined_output_message += f"<TOOL_CODE>\n{item['output']}\n</TOOL_CODE>\n"

            conversation_history.append({"role": "user", "content": combined_output_message.strip()})
            print(Fore.YELLOW + "Command outputs sent to AI for context." + Style.RESET_ALL)

            follow_up_ai_output = llm.create_chat_completion(
                messages=conversation_history,
                max_tokens=tokens,
                stop=["User:", "Bandit:", "<|im_end|>"],
                temperature=0.7,
            )
            follow_up_answer = follow_up_ai_output["choices"][0]["message"]["content"].strip()
            print("Bandit (follow-up): ", Fore.GREEN + follow_up_answer)
            conversation_history.append({"role": "assistant", "content": follow_up_answer})

            process_ai_response_for_commands(follow_up_answer) # This will now check for commands in the follow-up

    except KeyboardInterrupt:
        print(Fore.RED + "\nExiting.")
        break
    except Exception as e:
        print(f"Error: {e}")

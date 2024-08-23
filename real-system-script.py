import subprocess
import os

def run_command(command, timeout=1):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout, errors='replace')
        output = result.stdout
        error = result.stderr
        
        if result.returncode != 0:
            output += f"\nError executing command: {error}"
        
        return output
    
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds\n"
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    commands_file = "commands.txt"  # command file
    
    if not os.path.isfile(commands_file):
        print(f"{commands_file}: No such file or directory")
        return

    # read file
    with open(commands_file, 'r') as file:
        commands = file.readlines()
    
    # log
    with open('commands_reply.txt', 'w') as log_file:
        for command in commands:
            
            command = command.strip()
            
            if command:
                print(f"Running command: {command}") 
                output = run_command(command, timeout=1)
                log_file.write(f"Command: {command}\n{output}\n----\n")
            else:
                print("Skipping empty line")  

    print("All commands executed. See commands_reply.txt for details.")

if __name__ == "__main__":
    main()

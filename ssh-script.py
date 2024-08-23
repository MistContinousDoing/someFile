import subprocess
import argparse
import os
import time

def parse_args():
    parser = argparse.ArgumentParser(description="Execute commands from a file via SSH.")
    parser.add_argument("--host", required=True, help="Hostname or IP address of the target system.")
    parser.add_argument("--port", default="22", help="Port number of the SSH service.")
    parser.add_argument("--user", default="root", help="Username for the SSH connection.")
    parser.add_argument("--password", required=True, help="Password for the SSH connection.")
    parser.add_argument("--commands", required=True, help="Path to the file containing the commands to execute.")
    return parser.parse_args()

def run_command(host, port, user, password, command, timeout=1):
    ssh_command = [
        '/usr/bin/sshpass', '-p', password,
        'ssh', '-p', port,
        f'{user}@{host}',
        command
    ]
    
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=timeout)
        output = result.stdout
        error = result.stderr
        
        if result.returncode != 0:
            output += f"\nError executing command: {error}"
        
        return output
    
    except subprocess.TimeoutExpired as e:
        return f"\nError: Command timed out after {timeout} seconds\n{str(e)}"
    except Exception as e:
        return f"\nError: {str(e)}"


def main():
    args = parse_args()
    
    if not os.path.isfile(args.commands):
        print(f"{args.commands}: No such file or directory")
        return

    # read file
    with open(args.commands, 'r') as file:
        commands = file.readlines()
    
    # log
    with open('commands_reply.txt', 'w') as log_file:
        for command in commands:
            
            command = command.strip()
            
            if command:
                print(f"Running command: {command}") 
                output = run_command(args.host, args.port, args.user, args.password, command, timeout=1)
                log_file.write(f"Command: {command}\n{output}\n----\n")
            else:
                print("Skipping empty line") 

    print("All commands executed. See commands_reply.txt for details.")

if __name__ == "__main__":
    main()

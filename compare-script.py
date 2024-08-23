import re

def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

def extract_commands_and_responses(responses):
    responses_list = []
    current_command = None
    for line in responses:
        if line.startswith("Command:"):
            if current_command is not None:
                responses_list.append(current_command)
            current_command = {'command': line[9:].strip(), 'response': ''}
        elif current_command is not None:
            current_command['response'] += line + '\n'
    if current_command is not None:
        responses_list.append(current_command)
    return responses_list

def classify_responses(cowrie_responses, real_responses):
    metrics = {'SALC': 0, 'SANLC': 0, 'FALC': 0, 'FANLC': 0}

    # Define regex patterns to match common error messages
    error_patterns = {
        "general_error": r"error",
        "not_found": r"not found",
        "command_not_found": r"command not found",
        "no_such_file_or_directory": r"no such file or directory",
        "no_such_file": r"no such file",
        "cannot_open_file": r"cannot open file",
        "file_not_found": r"file not found",
        "directory_not_found": r"directory not found"
    }

    min_length = min(len(cowrie_responses), len(real_responses))
    cowrie_responses = cowrie_responses[:min_length]
    real_responses = real_responses[:min_length]

    # Open files to write commands
    with open('SALC_commands.txt', 'w') as salc_file, \
         open('SANLC_commands.txt', 'w') as sanlc_file, \
         open('FALC_commands.txt', 'w') as falc_file, \
         open('FANLC_commands.txt', 'w') as fanlc_file:

        for cowrie_response, real_response in zip(cowrie_responses, real_responses):
            # check “Command timed out after 1 seconds”
            if "Command timed out after 1 seconds" in cowrie_response['response'] and \
               "Command timed out after 1 seconds" in real_response['response']:
                metrics['SALC'] += 1
                salc_file.write(cowrie_response['command'] + '\n')
                continue

            # Initialize flags for error matching
            cowrie_error_matched = False
            real_error_matched = False

            # Check for errors in both Cowrie and real system responses
            for pattern_name, pattern in error_patterns.items():
                if re.search(pattern, cowrie_response['response'], re.IGNORECASE):
                    cowrie_error_matched = True
                if re.search(pattern, real_response['response'], re.IGNORECASE):
                    real_error_matched = True

            # Classify based on error matching
            if cowrie_error_matched and real_error_matched:
                metrics['FALC'] += 1
                falc_file.write(cowrie_response['command'] + '\n')
            elif not cowrie_error_matched and not real_error_matched:
                # Match the general format of the responses
                cowrie_format = re.sub(r'\s+', ' ', re.sub(r'\d+', '', cowrie_response['response']))
                real_format = re.sub(r'\s+', ' ', re.sub(r'\d+', '', real_response['response']))

                if cowrie_format == real_format:
                    metrics['SALC'] += 1
                    salc_file.write(cowrie_response['command'] + '\n')
                else:
                    metrics['SANLC'] += 1
                    sanlc_file.write(cowrie_response['command'] + '\n')
            else:
                metrics['FANLC'] += 1
                fanlc_file.write(cowrie_response['command'] + '\n')

    return metrics

# read
cowrie_responses = extract_commands_and_responses(read_file('cowrie_commands_reply.txt'))
real_responses = extract_commands_and_responses(read_file('real-system_commands_reply.txt'))

# match
cowrie_commands = [r['command'] for r in cowrie_responses]
real_commands = [r['command'] for r in real_responses]

if cowrie_commands != real_commands:
    raise ValueError("Txt length error")

# classify
metrics = classify_responses(cowrie_responses, real_responses)

# print
print(f"SALC: {metrics['SALC']}")
print(f"SANLC: {metrics['SANLC']}")
print(f"FALC: {metrics['FALC']}")
print(f"FANLC: {metrics['FANLC']}")

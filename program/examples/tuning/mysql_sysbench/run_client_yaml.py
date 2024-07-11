import yaml
import subprocess

def execute_command(command):
    """
    Executes a shell command and returns the output.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None

def main():
    # Load YAML configuration
    with open('mysql_sysbench_client.yaml', 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)

    project_name = config.get('project', 'mysql_sysbench')
    benchmark_command = config.get('benchmark', '')
    evaluations = config.get('evaluations', [])

    # Execute benchmark command
    if benchmark_command:
        print(f"Executing benchmark command...")
        output = execute_command(benchmark_command)
        if output is not None:
            print(f"Benchmark command executed successfully.")
            print(f"Output:\n{output}")
        else:
            print(f"Failed to execute benchmark command.")
    
    # Execute each evaluation command
    for evaluation in evaluations:
        eval_name = evaluation.get('name', '')
        eval_info = evaluation.get('info', {})
        eval_command = eval_info.get('get', '')

        if eval_command:
            print(f"Executing evaluation command '{eval_name}'...")
            output = execute_command(eval_command)
            if output is not None:
                print(f"Evaluation command '{eval_name}' executed successfully.")
                print(f"Output:\n{output}")
            else:
                print(f"Failed to execute evaluation command '{eval_name}'.")
        else:
            print(f"Invalid evaluation command definition: {evaluation}")

if __name__ == "__main__":
    main()

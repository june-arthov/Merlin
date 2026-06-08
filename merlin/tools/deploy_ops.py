import subprocess
from .base import BaseTool

class DockerManager(BaseTool):
    @property
    def name(self):
        return "docker_manager"

    @property
    def description(self):
        return "Manages Docker containers and images (build, run, stop, ps, logs)."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["build", "up", "down", "ps", "logs", "restart"], "description": "Action to perform."},
                "target": {"type": "string", "description": "Container name or image name."},
                "args": {"type": "string", "description": "Additional docker arguments."}
            },
            "required": ["action"]
        }

    def execute(self, action, target=None, args=""):
        cmd = f"docker {action} {target if target else ''} {args}"
        if action == "up":
            cmd = f"docker-compose up -d {target if target else ''} {args}"
        elif action == "down":
            cmd = f"docker-compose down {args}"
            
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return {
                "command": cmd,
                "exit_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except Exception as e:
            return {"error": str(e)}

class SSHExec(BaseTool):
    @property
    def name(self):
        return "ssh_exec"

    @property
    def description(self):
        return "Executes a command on a remote server via SSH."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "host": {"type": "string", "description": "Remote host (user@ip)."},
                "command": {"type": "string", "description": "Command to run remotely."},
                "identity_file": {"type": "string", "description": "Path to SSH private key."}
            },
            "required": ["host", "command"]
        }

    def execute(self, host, command, identity_file=None):
        ssh_cmd = f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no"
        if identity_file:
            ssh_cmd += f" -i {identity_file}"
        
        full_cmd = f'{ssh_cmd} {host} "{command}"'
        
        try:
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
            return {
                "host": host,
                "exit_code": result.returncode,
                "output": (result.stdout + "\n" + result.stderr).strip()
            }
        except Exception as e:
            return {"error": str(e)}

import subprocess, re

class ShellProcessor:
    def __init__(self, command: str = "", timeout: int = 60):
        self.command = command
        self.timeout = timeout
        self._output = ''
        self._error = None
        self.executing = False

    def execute(self):
        self.executing = True
        try:
            process = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            self._output = process.stdout
            if process.stderr:
                self._error = process.stderr
            
        except subprocess.TimeoutExpired:
            self._error = f"Command timed out after {self.timeout} seconds"
        except Exception as e:
            self._error = f"{type(e).__name__}: {str(e)}"
        finally:
            self.executing = False

    @property
    def result(self):
        output = self._output.strip()
        output = re.sub(r'\n+$', '', output)
        
        return {
            'output': output,
            'error': self._error,
            'returncode': 1 if self._error else 0
        }
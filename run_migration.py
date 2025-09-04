import subprocess
import sys

# Executar o script de migração
result = subprocess.run([sys.executable, "migrate_debug.py"], capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print("Return code:", result.returncode)

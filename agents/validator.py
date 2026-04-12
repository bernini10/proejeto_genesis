import subprocess, sys
def run_tests():
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'], capture_output=True, text=True)
    return {'success': result.returncode == 0, 'stdout': result.stdout, 'stderr': result.stderr}

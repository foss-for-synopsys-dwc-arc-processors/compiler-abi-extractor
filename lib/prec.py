
import subprocess

def pre_condition(cmd):

    print(cmd)

    result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    assert (result.returncode == 0)

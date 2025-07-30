import subprocess


def start():
    print("Starting static checks with ty:")
    print("------------------------------------------------------------")
    ty_process = subprocess.Popen(["ty", "check", "./src"])
    ty_exit_code = ty_process.wait()
    exit(ty_exit_code)

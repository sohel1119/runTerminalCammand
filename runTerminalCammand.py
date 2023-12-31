from subprocess import Popen, PIPE
from os import kill
from signal import alarm, signal, SIGALRM, SIGKILL


def get_process_children(pid):

    p = Popen('ps --no-headers -o pid --ppid %d' % pid, shell=True,
              stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]


def run(args, cwd=None, shell=False, kill_tree=True, timeout=-1, env=None):

    class Alarm(Exception):
        pass

    def alarm_handler(signum, frame):
        raise Alarm
    p = Popen(args, shell=shell, cwd=cwd, stdout=PIPE, stderr=PIPE, env=env)

    if timeout != -1:
        signal(SIGALRM, alarm_handler)
        alarm(timeout)
    try:
        stdout, stderr = p.communicate()
        if timeout != -1:
            alarm(0)

    except Alarm:
        pids = [p.pid]

        if kill_tree:
            pids.extend(get_process_children(p.pid))

        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try:
                kill(pid, SIGKILL)

            except OSError:
                print("OSError")
                pass

        return -9, '', ''
    return p.returncode, stdout, stderr


data = run("ls", shell=True, timeout=20)
print(data)

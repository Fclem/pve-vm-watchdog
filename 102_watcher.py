#!/usr/bin/env python3

import os
from time import sleep
import datetime

hostname = "192.168.0.10"
# hostname = "home.fiere.fr"
vm_id = 101
interval = 10
deadline = 30
add_ts = False
backend = 'curl'  # 'ping'


def f_print(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def ts_print(*args, **kwargs):
    if add_ts:
        f_print(str(datetime.datetime.now())[:-4], *args, **kwargs)
    else:
        f_print(*args, **kwargs)


def get_status():
    return os.popen('qm status %s' % vm_id).read()


def is_running():
    return str(get_status()).replace('\n', '').strip() == 'status: running'


def is_host_up(deadline=3, init=False):
    if init or backend == 'ping':
        return os.system("ping -w %d -c 1 %s >/dev/null" % (deadline, hostname)) == 0
    elif backend == 'curl':
        return os.system("curl -s -m %d %s >/dev/null" % (deadline, hostname)) == 0


def wait_for_host_to_be_online(init=False):
    if not is_host_up(1, init):
        ts_print('waiting for host %s to come up' % hostname)
        while not is_host_up(1, init):
            f_print('.', end='')
        f_print('')


def wait_for_vm_to_be_up():
    if not is_running():
        ts_print("VM is down, waiting for it to start")
        while not is_running():
            f_print('.', end='')
            sleep(1)
        f_print('')
        ts_print('VM is running !')


def cycle_vm():
    ts_print('Restarting VM %d' % vm_id)
    ret = os.system('qm stop %d && qm start %d' % (vm_id, vm_id))
    ts_print('(%d) done' % ret)


def ping():
    if is_host_up(deadline):
        ts_print(hostname, 'is up :D')
    else:
        ts_print(hostname, 'is down !')
        cycle_vm()
        wait_for_host_to_be_online()
        ping()


def watchdog():
    wait_for_vm_to_be_up()
    wait_for_host_to_be_online(True)
    while True:
        ping()
        sleep(interval)


if __name__ == '__main__':
    watchdog()

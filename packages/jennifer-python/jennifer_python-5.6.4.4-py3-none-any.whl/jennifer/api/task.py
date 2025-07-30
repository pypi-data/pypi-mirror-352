# -*- coding: utf-8 -*-
import os
from threading import Thread, Timer
import time
from .util import _log


def run_task(target, thread_name, args=()):
    t = Thread(target=target, args=args)
    t.daemon = True
    if thread_name is not None:
        t.name = thread_name
    t.start()
    return t


def run_timer(target_func, thread_name, interval=1):

    def handler():
        old = time.time()

        while True:
            try:
                time.sleep(interval)
                current = time.time()

                if (current - old) > 3:  # fork 프로세스가 처리할 요청이 없어 모든 파이썬 스레드가 suspend 상태로 된 이후,
                                         # 다시 깨어난 경우 시간이 많이 지났을 수 있음.
                                         # uwsgi의 경우 --enable-threads 옵션이 있는 경우 이런 처리가 불필요
                    old = current
                    continue

                target_func()
            except Exception as e:
                _log('INFO', e)

    t = Thread(target=handler)
    if thread_name is not None:
        t.name = thread_name
    t.daemon = True
    t.start()

    return t

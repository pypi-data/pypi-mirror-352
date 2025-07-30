import time
import traceback
import threading

"""
2019-09-04
本来我觉得原生的线程池应该比较好，可是我发现
from concurrent.futures import ThreadPoolExecutor, wait 
该线程池控制线程启动的时候，并不精确，我本来只想一次只运行一个

2025-03-20
线程数控制十分精确
"""


class ThreadExecutor:
    def __init__(self, task: list, max_workers=1):
        self.__task = task  # 任务队列
        self.__max_workers = max_workers  # 最大执行数量
        self.__running_count = 0  # 正在执行的线程数

        self.__main = None  # 任务方法
        self.__start_time = 0

        self.task_count = len(task)  # 任务数
        self.done_task = []
        self.fail_task = []

    def __repr__(self):
        return self.shape()

    def __worker(self, worker_param):
        self.__running_count += 1
        if callable(worker_param):
            worker_param = worker_param()
        while True:
            try:
                parameter = self.__task.pop()
            except:
                break

            try:
                if isinstance(parameter, dict):
                    if worker_param is not None:
                        parameter['worker_param'] = worker_param
                    self.__main(**parameter)
                elif isinstance(parameter, (list, tuple)):
                    if worker_param is not None:
                        parameter.append(worker_param)
                    self.__main(*parameter)
                else:
                    if worker_param is not None:
                        self.__main(parameter, worker_param)
                    else:
                        self.__main(parameter)

                self.done_task.append(parameter)
            except Exception as e:
                self.fail_task.append(parameter)
                traceback.print_exc()
                print(e)

        self.__running_count -= 1

    def run(self, mian: callable, worker_param=None):
        self.__start_time = time.time_ns()
        self.__main = mian
        for _ in range(self.__max_workers):
            threading.Thread(target=self.__worker, args=(worker_param,)).start()

    def residue(self):
        return self.task_count - (len(self.done_task) + len(self.fail_task))

    def progress(self, tqdm_bar, logger=None):
        """
        tqdm_bar = tqdm(total=total)
        """
        last_finish = 0
        while True:
            residue = self.residue()
            curr_finish = self.task_count - residue
            tqdm_bar.update(curr_finish - last_finish)
            last_finish = curr_finish
            if residue <= 0:
                break
            time.sleep(1)
            try:
                logger.info(self.shape())
            except:
                pass

        tqdm_bar.close()

    def shape(self):
        tip = [
            ('任务数', self.task_count),
            ('完成数', len(self.done_task)),
            ('失败数', len(self.fail_task)),
            ('运行数', self.__running_count),
            ('已用时', (time.time_ns() - self.__start_time) / 10 ** 9),
        ]
        return '; '.join([f'{_[0]}: {_[1]}' for _ in tip])

    def completed(self):
        while self.residue() > 0:
            time.sleep(0.1)


if '__main__' == __name__:
    from tqdm import tqdm
    from random import randint
    from src.efficient import LoggingFactory


    def f(_id, wp):
        time.sleep(1)


    t = [_ for _ in range(30)]

    te = ThreadExecutor(t, 5)
    te.run(f, lambda: randint(1, 1000))

    te.progress(
        tqdm(total=te.task_count),
        LoggingFactory.get_logger(console=dict(open=False), file=dict(path='./xxx.log'))
    )
    print(te)

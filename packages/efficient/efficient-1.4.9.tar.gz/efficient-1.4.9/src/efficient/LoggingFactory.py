import os
import logging


class LoggingFactory:
    instance = dict()

    @classmethod
    def get_logger(cls, name=None, level=None, formatter=None, console=None, file=None):
        if logger := cls.instance.get(name):
            return logger

        level = logging.DEBUG if level is None else level
        formatter = cls.formatter() if formatter is None else formatter
        logger = logging.getLogger(name)
        logger.setLevel(level)  # logging.getLogger 是单例模式。不设置 level 的话，StreamHandler 的设置将无效

        cls.set_console_handler(logger, console, level, formatter)
        cls.set_file_handler(logger, file, level, formatter)
        cls.instance[name] = logger

        return logger

    # 输出到console
    @classmethod
    def set_console_handler(cls, logger, config, level=None, formatter=None):
        if config is None:
            config = dict()

        handler = logging.StreamHandler()
        handler.setFormatter(config.get('formatter', formatter))
        handler.setLevel(config.get('level', level))
        logger.addHandler(handler)
        if not config.get('open', True):
            # 动态移除 console 输出
            logger.removeHandler(handler)

    # 输出到文件
    @classmethod
    def set_file_handler(cls, logger, config, level=None, formatter=None):
        if config is None:
            config = dict()
        log_file = config.get('path')
        if log_file is None:
            return

        file_path = os.path.dirname(log_file)
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        handler = logging.FileHandler(log_file, mode=config.get('mode', 'a'))
        handler.setLevel(config.get('level', level))
        handler.setFormatter(config.get('formatter', formatter))

        logger.addHandler(handler)

    @classmethod
    def formatter(cls):
        # out_formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(pathname)s:%(lineno)d >>> %(message)s')
        """
        级别排序:CRITICAL > ERROR > WARNING > INFO > DEBUG
        格式化
        %(levelno)s：打印日志级别的数值
        %(levelname)s：打印日志级别的名称
        %(pathname)s：打印当前执行程序的路径，其实就是sys.argv[0]
        %(filename)s：打印当前执行程序名
        %(funcName)s：打印日志的当前函数
        %(lineno)d：打印日志的当前行号
        %(asctime)s：打印日志的时间
        %(thread)d：打印线程ID
        %(threadName)s：打印线程名称
        %(process)d：打印进程ID
        %(message)s：打印日志信息
        """
        return logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(filename)s:%(lineno)d >>> %(message)s')


if '__main__' == __name__:
    # log = LoggingFactory.get_logger(console=dict(open=False)) # 虽然意图不启用 console 打印，但 console 会使用默认的打印
    # log = LoggingFactory.get_logger(console=dict(open=False), file=dict(path='./xxx.log')) # 只在文件中打印
    # log = LoggingFactory.get_logger( file=dict(path='./xxx.log')) # console 打印，文件中打印
    log = LoggingFactory.get_logger()  # 只在 console 打印
    log.debug(u"debug")  # 打印全部的日志,详细的信息,通常只出现在诊断问题上
    log.info(u"info")  # 打印info,warning,error,critical级别的日志,确认一切按预期运行
    log.warning(u"warning")  # 打印warning,error,critical级别的日志,一个迹象表明,一些意想不到的事情发生了,或表明一些问题在不久的将来(例如。磁盘空间低”),这个软件还能按预期工作
    log.error(u"error")  # 打印error,critical级别的日志,更严重的问题,软件没能执行一些功能
    log.critical(u"critical")  # 打印critical级别,一个严重的错误,这表明程序本身可能无法继续运行
    try:
        print(1 + 'a')
    except Exception as e:
        log.critical("发生异常 {}".format(e), exc_info=True)

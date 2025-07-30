import time
from datetime import date, datetime, timezone, timedelta


class Date:
    # 时间戳转为日期
    @staticmethod
    def date(fmt=None, timestamp=None):
        if fmt is None:
            fmt = '%Y-%m-%d %H:%M:%S'
        if timestamp is None:
            timestamp = round(time.time())
        date_str = time.strftime(fmt, time.localtime(timestamp))
        return date_str

    # 日期转为时间戳
    @staticmethod
    def date_to_time(date_str):
        fmt = Date.infer_time_format(date_str)
        time_array = time.strptime(date_str, fmt)
        timestamp = round(time.mktime(time_array))
        return timestamp

    @staticmethod
    def calc_date(date_str, days=1):
        fmt = Date.infer_time_format(date_str)
        tm = time.strptime(date_str, fmt)
        # print('年', tm.tm_year)
        # print('月', tm.tm_mon)
        # print('月的日', tm.tm_mday)
        # print('周的日', tm.tm_wday)
        # print('年的日', tm.tm_yday)
        curr_date = date(tm.tm_year, tm.tm_mon, tm.tm_mday)
        next_date = curr_date + timedelta(days=days)
        # return next_date.year, next_date.month, next_date.day
        return next_date.strftime(fmt)

    @staticmethod
    def infer_time_format(date_str):
        time_formats = [
            '%Y%m%d',  # 20241010
            '%Y-%m-%d',  # 2024-10-10
            '%Y/%m/%d',  # 2024/10/10
            '%Y.%m.%d',  # 2024.10.10
            '%Y-%m-%d %H:%M:%S',  # 2024-10-10 10:01:27
            '%Y/%m/%d %H:%M:%S',  # 2024/10/10 10:01:27
            '%H:%M:%S',  # 10:01:27
        ]
        for time_format in time_formats:
            try:
                # 尝试解析时间字符串
                time.strptime(date_str, time_format)
                return time_format
            except ValueError:
                continue
        return None

    @staticmethod
    def iso8601_utc_utc8(time_str):
        """
        2024-10-30T03:57:51.770Z
        ISO 8601 格式。ISO 8601 是一种国际标准化的日期和时间表示方法，常用于数据传输和存储。
        结构解析
            2024-10-30：日期部分，年-月-日。
            T：日期和时间的分隔符。
            03:57:51.770：时间部分，时:分:秒.毫秒。
            Z：指的是 UTC 时区（也称零时区）。Z 是 “Zulu time” 的缩写，表示 UTC+0。
        :return:
        """
        parsed_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        # parsed_time 是一个 “无时区的” datetime 对象。尽管字符串 2024-10-30T03:57:51.770Z 表示的是 UTC 时间，但 datetime.strptime 默认不会将其解析为特定时区
        # 设置时区 UTC
        parsed_time = parsed_time.replace(tzinfo=timezone.utc)
        # 转换为东八区时间
        parsed_time = parsed_time.astimezone(timezone(timedelta(hours=8)))

        return {
            '_date': parsed_time.strftime("%Y%m%d"),
            '_date_time': parsed_time.strftime("%Y-%m-%d %H:%M:%S"),
            'timestamp': int(parsed_time.timestamp()),
        }


fmt_date = Date.date
date_to_time = Date.date_to_time
calc_date = Date.calc_date
infer_time_format = Date.infer_time_format
iso8601_utc_utc8 = Date.iso8601_utc_utc8

if '__main__' == __name__:
    import calendar

    # year = 2024
    # moth = 10
    # _, num_days = calendar.monthrange(year, moth)
    # for i in range(num_days):
    #     main(year, moth, i + 1)
    print(fmt_date())

    print(date_to_time('2025-03-20'))
    print(date_to_time('2025/03/20'))
    print(date_to_time('2025.03.20'))
    print(date_to_time('2025-03-20 14:53:00'))

    print(calc_date('2020-10-10', -1))
    print(calc_date('2020-10-10', 0))
    print(calc_date('2020-10-10', +1))

    print(iso8601_utc_utc8('2024-10-30T03:57:51.770Z'))

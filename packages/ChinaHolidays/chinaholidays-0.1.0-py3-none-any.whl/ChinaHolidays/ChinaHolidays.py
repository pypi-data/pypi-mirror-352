"""
获取中国节假日信息
"""

import toml, os
from datetime import datetime, timedelta

OFFICIAL_INFO_PATH = os.path.join(os.path.dirname(__file__), "official_info.toml")
with open(OFFICIAL_INFO_PATH, "r", encoding="utf-8") as f:
    OFFICIAL_INFO = toml.load(f)

def date_range(start_date: datetime, end_date: datetime) -> set[datetime]:
    """获取日期范围

    :param start_date: 开始日期
    :type start_date: datetime
    :param end_date: 结束日期（包含）
    :type end_date: datetime
    :return: 日期范围
    :rtype: set[datetime]"""
    if start_date > end_date:
        raise ValueError(f"start_date[{start_date}] > end_date[{end_date}].")
    days = (end_date - start_date).days + 1
    return {start_date + timedelta(days=i) for i in range(days)}


class ChinaHolidays:
    """中国节假日"""

    def __init__(self, year: int = None):
        self.year = year
        if self.year < 2024:
            raise ValueError(f"目前只支持2024年及以后的节假日信息。")
        if self.year > datetime.now().year:
            raise ValueError(f"{self.year}年的官方节假日安排还未发布。")
        self.official_info = OFFICIAL_INFO

    @property
    def festivals(self):
        """节假日"""
        kv: dict[str, str] = self.official_info[str(self.year)]["festivals"]
        for key, value in kv.items():
            if isinstance(value, set):
                break
            if "~" in value:
                start_date, end_date = [s.strip() for s in value.split("~")]
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                kv[key] = date_range(start_date, end_date)
            else:
                kv[key] = {datetime.strptime(value, "%Y-%m-%d")}
        return kv

    @property
    def festival_days(self):
        """节假日日期"""
        return {day for days in self.festivals.values() for day in days}

    @property
    def compensatory_workdays(self):
        """调休工作日"""
        workdays = self.official_info[str(self.year)]["调休工作日"]
        return {datetime.strptime(day, "%Y-%m-%d") for day in workdays}

    @property
    def weekends(self):
        """周末"""
        days = date_range(datetime(self.year, 1, 1), datetime(self.year, 12, 31))
        return {day for day in days if day.weekday() >= 5}


def get_all_holidays(
    consider_compensatory_workdays: bool = False, year: int = datetime.now().year
) -> set[datetime]:
    """获取所有休息日（法定节假日+周末）

    :param consider_compensatory_workdays: 是否考虑调休工作日，默认为False
    :type consider_compensatory_workdays: bool
    :param year: 年份。默认为当前年份
    :type year: int
    :return: 休息日列表
    :rtype: set[datetime]"""
    ch = ChinaHolidays(year)
    holidays = set()
    holidays.update(ch.weekends)
    holidays.update(ch.festival_days)
    if consider_compensatory_workdays:
        holidays = holidays - ch.compensatory_workdays
    return holidays


def filter_holidays(
    start_date: datetime,
    end_date: datetime,
    consider_compensatory_workdays: bool = False,
) -> set[datetime]:
    """筛掉休息日（法定节假日+周末）

    :param start_date: 开始日期
    :type start_date: datetime
    :param end_date: 结束日期（包含）
    :type end_date: datetime
    :param consider_compensatory_workdays: 是否考虑调休工作日，默认为False
    :type consider_compensatory_workdays: bool
    :return: 指定时间范围非休息日列表
    :rtype: set[datetime]"""
    holidays = get_all_holidays(consider_compensatory_workdays, start_date.year)
    holidays.update(get_all_holidays(consider_compensatory_workdays, end_date.year))
    return {day for day in date_range(start_date, end_date) if day not in holidays}


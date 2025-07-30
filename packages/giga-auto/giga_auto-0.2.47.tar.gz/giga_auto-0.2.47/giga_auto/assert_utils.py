import datetime

from giga_auto.utils import to_date


class AssertUtils:

    @staticmethod
    def assert_equal(actual, expected, msg=None):
        """
        断言两个值相等
        """
        assert actual == expected, f"{msg or ''} \nAssert Equal Failed: Expected:{expected},Actual:{actual}"

    @staticmethod
    def assert_not_equal(actual, expected, msg=None):
        """
        断言两个值不相等
        """
        assert actual != expected, f"{msg or ''} \nAssert Not Equal Failed: Expected:{expected},Actual:{actual}"

    @staticmethod
    def assert_in(expected, actual, msg=None):
        """
        断言actual在expected中，支持字符串和列表
        """
        if isinstance(actual, list) and isinstance(expected, list):
            assert all(item in actual for item in expected), \
                f"{msg or ''} \nAssert In Failed: Expected items {expected} not all in Actual:{actual}"
        else:
            assert expected in actual, \
                f"{msg or ''} \nAssert In Failed: Expected:{expected}"

    @staticmethod
    def assert_not_in(expect_text, actual_text, msg=None):
        """
        断言actual不在expected中
        """
        assert expect_text not in actual_text, f"{msg or ''} \nAssert Not In Failed"

    @staticmethod
    def assert_not_none(actual, msg=None):
        assert actual is not None, f"{msg or ''} \nAssert Not None Failed: Actual:{actual}"

    @staticmethod
    def assert_is_none(actual, msg=None):
        assert actual is None, f"{msg or ''} \nAssert Not None Failed: Actual:{actual}"

    @staticmethod
    def assert_true(actual, msg=None):
        assert actual is True, f"{msg or ''} \nAssert True Failed: Actual:{actual}"

    @staticmethod
    def assert_false(actual, msg=None):
        assert actual is False, f"{msg or ''} \nAssert False Failed: Actual:{actual}"

    @staticmethod
    def assert_equal_ignore_type(actual, expected, msg=None):
        try:
            # 尝试将两者作为数值进行比较
            assert float(actual) == float(
                expected), f"{msg or ''} \nAssert Equal (Ignore Type) Failed: Expected:{expected}, Actual:{actual}"
        except (ValueError, TypeError):
            # 如果无法转成 float，则回退到字符串比较
            assert str(actual) == str(
                expected), f"{msg or ''} \nAssert Equal (Ignore Type) Failed: Expected:{expected}, Actual:{actual}"

    @staticmethod
    def assert_is_empty(value, msg=None):
        assert value in (None, '', [], {}, set()), f"{msg or ''} \nAssert Empty Failed: Actual:{value}"

    @staticmethod
    def assert_not_empty(value, msg=None):
        """
        排除0， False
        """
        assert value not in (None, '', [], {}, set()), f"{msg or ''} \nAssert Not Empty Failed: Actual:{value}"

    @staticmethod
    def assert_greater(actual, expected, msg=None):
        """
        断言actual大于expected
        """
        assert actual > expected, f"{msg or ''} \nAssert Greater Failed: Expected greater than {expected}, Actual:{actual}"

    @staticmethod
    def assert_greater_equal(actual, expected, msg=None):
        """
        断言actual大于expected
        """
        assert actual >= expected, f"{msg or ''} \nAssert Greater Failed: Expected greater or equal {expected}, Actual:{actual}"

    @staticmethod
    def assert_less(actual, expected, msg=None):
        """
        断言actual小于expected
        """
        assert actual < expected, f"{msg or ''} \nAssert Less Failed: Expected less than {expected}, Actual:{actual}"

    @staticmethod
    def assert_less_equal(actual, expected, msg=None):
        """
        断言actual小于expected
        """
        assert actual <= expected, f"{msg or ''} \nAssert Less Failed: Expected less or equal {expected}, Actual:{actual}"

    @staticmethod
    def assert_between(actual, min_value, max_value, msg=None):
        """
        断言actual在min_value和max_value之间
        """
        assert min_value <= actual <= max_value, f"{msg or ''} \nAssert Between Failed: Expected between {min_value} and {max_value}, Actual:{actual}"

    @staticmethod
    def assert_starts_with(actual, prefix, msg=None):
        """
        断言actual以prefix开头
        """
        assert str(actual).startswith(
            str(prefix)), f"{msg or ''} \nAssert Starts With Failed: Expected prefix {prefix}, Actual:{actual}"

    @staticmethod
    def assert_ends_with(actual, suffix, msg=None):
        """
        断言actual以suffix结尾
        """
        assert str(actual).endswith(
            str(suffix)), f"{msg or ''} \nAssert Ends With Failed: Expected suffix {suffix}, Actual:{actual}"

    @staticmethod
    def assert_regex_match(actual, pattern, msg=None):
        import re
        assert re.match(pattern,
                        str(actual)), f"{msg or ''} \nAssert Regex Match Failed: Expected pattern {pattern}, Actual:{actual}"

    @staticmethod
    def assert_date_equal(expected, actual):
        """
        通用日期比较方法，支持 str、datetime、date 类型
        """
        expected_date = to_date(expected)
        actual_date = to_date(actual)

        assert expected_date == actual_date, f"Expected: {expected_date}, Actual: {actual_date}"

    @staticmethod
    def assert_time_range(start_time, end_time, actual_time, msg=None):
        """
        断言时间范围
        """
        start_time = to_date(start_time)
        end_time = to_date(end_time)
        actual_time = to_date(actual_time)
        assert start_time <= actual_time <= end_time, f"{msg or ''} \nAssert Time Range Failed: Expected between {start_time} and {end_time}, Actual:{actual_time}"

    @staticmethod
    def assert_date_has_overlap(period1, period2, label='', msg=None):
        # 将字符串转换为 datetime 对象
        if isinstance(period1, str):
            period1 = period1.split(label)
        if isinstance(period2, str):
            period2 = period2.split(label)
        start1, end1 = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), period1)
        start2, end2 = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), period2)
        # 判断是否有交集
        assert max(start1, start2) <= min(end1,
                                          end2), f"{msg or ''} \nAssert Date Has Overlap Failed: Expected no overlap, Actual:{period1} and {period2}"

    @staticmethod
    def assert_sorted_data(data, reverse=False):
        """
        利用sorted()辅助函数，用于判断数据是否按顺序排列
        """
        assert data == sorted(data, reverse=reverse)

    @staticmethod
    def assert_msg_code(response, expect):
        """统一校验响应码"""
        expect_msg = expect.get('msg') or expect.get('message')
        resp_msg = response.get('msg') or response.get('message')
        expect_code = expect.get('code')

        assert expect_code == response.get('code'), f"响应码校验失败: 预期 {expect_code}, 实际 {response.get('code')}"
        assert expect_msg == resp_msg, f"响应消息校验失败: 预期 {expect_msg}, 实际 {resp_msg}"

    @staticmethod
    def assert_msg(resp: dict, expect, msg=""):
        """通用响应msg断言"""
        response_msg = resp.get('msg') or resp.get('message')
        if isinstance(expect, str):
            expect_msg = expect
        elif isinstance(expect, dict):
            expect_msg = expect.get('msg') or expect.get('message')
        else:
            raise TypeError("expect参数类型错误")
        AssertUtils.assert_equal(response_msg, expect_msg,
                                 f"resp_msg: {response_msg},expect_msg: {expect_msg}, {msg}响应msg不符")

    @staticmethod
    def assert_code(resp: dict, expect: dict, msg=""):
        """通用响应code断言"""
        AssertUtils.assert_equal(resp.get('code'), expect.get('code'),
                                 f"resp_code: {resp.get('code')},expect_code: {expect.get('code')}, {msg}响应code不符")

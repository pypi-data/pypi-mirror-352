"""
Tests for Status enumeration.
Status列挙型のテスト。
"""

import pytest
from flexify.core import Status


class TestStatus:
    """
    Test cases for Status enum.
    Status列挙型のテストケース。
    """
    
    def test_status_values_exist(self):
        """
        Test that all expected status values exist.
        期待されるすべてのステータス値が存在することをテストします。
        """
        assert Status.PENDING
        assert Status.RUNNING
        assert Status.SUCCESS
        assert Status.FAILED
        assert Status.SKIPPED
    
    def test_status_unique_values(self):
        """
        Test that all status values are unique.
        すべてのステータス値が一意であることをテストします。
        """
        status_values = [status.value for status in Status]
        assert len(status_values) == len(set(status_values))
    
    def test_status_comparison(self):
        """
        Test that status values can be compared.
        ステータス値が比較できることをテストします。
        """
        assert Status.PENDING != Status.RUNNING
        assert Status.SUCCESS != Status.FAILED
        assert Status.PENDING == Status.PENDING
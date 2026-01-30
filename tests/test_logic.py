"""
Tests for logic.py
"""
import pytest
from src.logic import check_number

def test_check_number_special_prize():
    winning_numbers = {
        "special_prize": "12345678",
        "grand_prize": "87654321",
        "first_prize": ["11223344", "55667788"]
    }
    
    # Test Special Prize
    assert "特別獎" in check_number("12345678", winning_numbers)
    
    # Test Not Winning
    assert "未中獎" in check_number("00000000", winning_numbers)

def test_check_number_suffix():
    winning_numbers = {
        "special_prize": "12345678",
        "grand_prize": "87654321",
        "first_prize": ["11223344", "55667788"]
    }
    
    # Test 3-digit match (Sixth Prize) on First Prize
    # First prize is 11223344. Suffix 3 is 344.
    assert "六獎" in check_number("344", winning_numbers)
    
    # Test 4-digit match
    assert "五獎" in check_number("3344", winning_numbers)

def test_invalid_input():
    winning_numbers = {}
    assert "Invalid input" in check_number("abc", winning_numbers)

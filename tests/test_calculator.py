from backend.app.calculator import SafeFinancialCalculator

def test_percentage_change():
    res = SafeFinancialCalculator.calculate_percentage_change(600, 500)
    assert res["result"] == 20.0

def test_difference():
    res = SafeFinancialCalculator.calculate_difference(600, 500)
    assert res["result"] == 100.0

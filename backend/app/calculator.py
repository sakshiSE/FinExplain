import re
from typing import Optional, Dict, Any

class SafeFinancialCalculator:
    @staticmethod
    def calculate_percentage_change(current: float, previous: float) -> Dict[str, Any]:
        if previous == 0:
            raise ValueError("Division by zero: Previous value cannot be zero.")
        diff = current - previous
        pct_change = (diff / abs(previous)) * 100.0
        return {
            "operation": "Percentage Change",
            "formula": "((Current - Previous) / |Previous|) * 100",
            "substituted_values": f"(({current} - {previous}) / |{previous}|) * 100",
            "result": round(pct_change, 2),
            "formatted_result": f"{pct_change:+.2f}%",
            "explanation": f"Value changed by {diff:+.2f}, representing a {pct_change:+.2f}% change."
        }

    @staticmethod
    def calculate_difference(val1: float, val2: float) -> Dict[str, Any]:
        diff = val1 - val2
        return {
            "operation": "Absolute Difference",
            "formula": "Value1 - Value2",
            "substituted_values": f"{val1} - {val2}",
            "result": round(diff, 2),
            "formatted_result": f"{diff:+.2f}",
            "explanation": f"The difference between {val1} and {val2} is {diff:+.2f}."
        }

    @staticmethod
    def calculate_profit_margin(profit: float, revenue: float) -> Dict[str, Any]:
        if revenue <= 0:
            raise ValueError("Revenue must be greater than zero.")
        margin = (profit / revenue) * 100.0
        return {
            "operation": "Profit Margin",
            "formula": "(Profit / Revenue) * 100",
            "substituted_values": f"({profit} / {revenue}) * 100",
            "result": round(margin, 2),
            "formatted_result": f"{margin:.2f}%",
            "explanation": f"Profit of {profit} on revenue of {revenue} gives a {margin:.2f}% margin."
        }

    @classmethod
    def detect_and_execute(cls, query: str, context_text: str) -> Optional[Dict[str, Any]]:
        numbers = [float(x.replace(',', '')) for x in re.findall(r'[-+]?\d+(?:,\d{3})*(?:\.\d+)?', query)]
        query_lower = query.lower()

        if len(numbers) >= 2:
            if "percent" in query_lower or "increase" in query_lower or "growth" in query_lower or "change" in query_lower:
                try:
                    return cls.calculate_percentage_change(numbers[1], numbers[0])
                except ValueError:
                    pass
            elif "margin" in query_lower:
                try:
                    return cls.calculate_profit_margin(numbers[0], numbers[1])
                except ValueError:
                    pass
            elif "difference" in query_lower or "how much" in query_lower or "compared" in query_lower:
                return cls.calculate_difference(numbers[0], numbers[1])

        return None

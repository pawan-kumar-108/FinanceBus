# services/investment_service.py
import google.generativeai as genai
from datetime import datetime
from config import Config

class InvestmentService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_investment_potential(self, transactions, emergency_fund, monthly_income):
        total_savings = self._calculate_total_savings(transactions)
        monthly_expenses = self._calculate_monthly_expenses(transactions)
        investable_amount = self._calculate_investable_amount(total_savings, emergency_fund, monthly_expenses)
        
        prompt = f"""
        Analyze investment potential based on:
        - Monthly Income: Rs. {monthly_income}
        - Monthly Expenses: Rs. {monthly_expenses}
        - Total Savings: Rs. {total_savings}
        - Emergency Fund: Rs. {emergency_fund}
        - Investable Amount: Rs. {investable_amount}

        Provide ONLY:
        1. YES/NO for investment readiness
        2. If YES, suggest exactly where to invest with percentages (max 2 lines)
        3. If NO, state single most important reason
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def get_smart_savings_plan(self, transactions, monthly_income):
        expenses_by_category = self._analyze_expenses_by_category(transactions)
        
        prompt = f"""
        Based on:
        - Monthly Income: Rs. {monthly_income}
        - Expense Pattern: {expenses_by_category}

        Provide ONLY two specific, actionable savings strategies in exactly 2 lines.
        Focus on highest-impact areas for immediate savings.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def suggest_investment_opportunities(self, transactions, emergency_fund):
        risk_profile = self._calculate_risk_profile(transactions)
        investable_surplus = self._calculate_investable_surplus(transactions, emergency_fund)
        
        prompt = f"""
        Given:
        - Risk Profile: {risk_profile}
        - Investable Surplus: Rs. {investable_surplus}
        - Emergency Fund: Rs. {emergency_fund}

        Suggest specific investment allocations in exactly 2-3 lines.
        Include exact percentages and investment types.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def get_risk_management_plan(self, transactions, monthly_income):
        expense_ratio = self._calculate_expense_ratio(transactions, monthly_income)
        
        prompt = f"""
        Based on:
        - Monthly Income: Rs. {monthly_income}
        - Expense Ratio: {expense_ratio}%
        - Transaction History Analysis

        Provide ONLY:
        1. One specific insurance recommendation
        2. One portfolio diversification strategy
        3. One long-term security measure
        Each in single line.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def _calculate_total_savings(self, transactions):
        income = sum(t['amount'] for t in transactions if t.get('category') == 'Income')
        expenses = sum(t['amount'] for t in transactions if t.get('category') != 'Income')
        return income - expenses

    def _calculate_monthly_expenses(self, transactions):
        monthly_totals = {}
        for t in transactions:
            if t.get('category') != 'Income':
                date = datetime.fromisoformat(t['date'].replace('Z', '+00:00')) if isinstance(t['date'], str) else t['date']
                month_key = date.strftime('%Y-%m')
                monthly_totals[month_key] = monthly_totals.get(month_key, 0) + t['amount']
        
        if not monthly_totals:
            return 0
        return sum(monthly_totals.values()) / len(monthly_totals)

    def _calculate_investable_amount(self, total_savings, emergency_fund, monthly_expenses):
        # Basic formula: Investable = Total Savings - (Emergency Fund + 3 months expenses)
        safety_buffer = emergency_fund + (monthly_expenses * 3)
        return max(0, total_savings - safety_buffer)

    def _analyze_expenses_by_category(self, transactions):
        category_totals = {}
        for t in transactions:
            if t.get('category') != 'Income':
                category_totals[t['category']] = category_totals.get(t['category'], 0) + t['amount']
        return category_totals

    def _calculate_risk_profile(self, transactions):
        # Simple risk profile based on spending patterns
        monthly_variation = self._calculate_monthly_expense_variation(transactions)
        if monthly_variation > 0.5:
            return "Conservative"
        elif monthly_variation > 0.3:
            return "Moderate"
        return "Aggressive"

    def _calculate_investable_surplus(self, transactions, emergency_fund):
        total_savings = self._calculate_total_savings(transactions)
        monthly_expenses = self._calculate_monthly_expenses(transactions)
        return max(0, total_savings - emergency_fund - (monthly_expenses * 2))

    def _calculate_expense_ratio(self, transactions, monthly_income):
        monthly_expenses = self._calculate_monthly_expenses(transactions)
        return (monthly_expenses / monthly_income * 100) if monthly_income > 0 else 0

    def _calculate_monthly_expense_variation(self, transactions):
        monthly_expenses = {}
        for t in transactions:
            if t.get('category') != 'Income':
                date = datetime.fromisoformat(t['date'].replace('Z', '+00:00')) if isinstance(t['date'], str) else t['date']
                month_key = date.strftime('%Y-%m')
                monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + t['amount']
        
        if not monthly_expenses:
            return 0
            
        values = list(monthly_expenses.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return (variance ** 0.5) / mean  # Coefficient of variation

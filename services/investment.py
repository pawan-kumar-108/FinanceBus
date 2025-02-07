# services/investment_service.py
import google.generativeai as genai
from datetime import datetime
import re
from config import Config

class InvestmentService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def _format_date(self, date_input):
        """
        Handles various date formats and returns a properly formatted datetime object
        """
        try:
            if isinstance(date_input, datetime):
                return date_input

            if isinstance(date_input, str):
                # Remove any milliseconds and timezone info
                date_str = re.sub(r'\.\d+([+-]\d{2}:?\d{2}|Z)?$', '', date_input)
                date_str = re.sub(r'([+-]\d{2}:?\d{2}|Z)$', '', date_str)

                # Split into date and time parts
                if 'T' in date_str:
                    date_part, time_part = date_str.split('T')
                else:
                    date_part = date_str
                    time_part = "00:00:00"

                # Pad the date components
                year, month, day = map(str, date_part.split('-'))
                month = month.zfill(2)
                day = day.zfill(2)

                # Ensure time part is properly formatted
                if ':' in time_part:
                    hour, minute, second = map(str, time_part.split(':'))
                    hour = hour.zfill(2)
                    minute = minute.zfill(2)
                    second = second.zfill(2)
                    time_part = f"{hour}:{minute}:{second}"

                # Reconstruct the date string
                formatted_date = f"{year}-{month}-{day}T{time_part}"
                return datetime.fromisoformat(formatted_date)

            return datetime.utcnow()
        except Exception as e:
            print(f"Date parsing error: {e} for input {date_input}")
            return datetime.utcnow()

    # Rest of the InvestmentService class remains the same
    def _process_transaction_dates(self, transactions):
        """
        Process all transactions and ensure dates are properly formatted
        """
        processed = []
        for t in transactions:
            t_copy = t.copy()
            t_copy['date'] = self._format_date(t.get('date', datetime.utcnow()))
            processed.append(t_copy)
        return processed

    def analyze_investment_potential(self, transactions, emergency_fund, monthly_income):
        transactions = self._process_transaction_dates(transactions)
        total_savings = self._calculate_total_savings(transactions)
        monthly_expenses = self._calculate_monthly_expenses(transactions)
        investable_amount = self._calculate_investable_amount(total_savings, emergency_fund, monthly_expenses)
        
        prompt = f"""
        Analyze investment potential based on:
        - Monthly Income: Rs. {monthly_income}
        - Monthly Expenses: Rs. {monthly_expenses:.2f}
        - Total Savings: Rs. {total_savings:.2f}
        - Emergency Fund: Rs. {emergency_fund}
        - Investable Amount: Rs. {investable_amount:.2f}

        Provide ONLY:
        1. YES/NO for investment readiness
        2. If YES, suggest exactly where to invest with percentages (max 2 lines)
        3. If NO, state single most important reason
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def get_smart_savings_plan(self, transactions, monthly_income):
        transactions = self._process_transaction_dates(transactions)
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
        transactions = self._process_transaction_dates(transactions)
        risk_profile = self._calculate_risk_profile(transactions)
        investable_surplus = self._calculate_investable_surplus(transactions, emergency_fund)
        
        prompt = f"""
        Given:
        - Risk Profile: {risk_profile}
        - Investable Surplus: Rs. {investable_surplus:.2f}
        - Emergency Fund: Rs. {emergency_fund}

        Suggest specific investment allocations in exactly 2-3 lines.
        Include exact percentages and investment types.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def get_risk_management_plan(self, transactions, monthly_income):
        transactions = self._process_transaction_dates(transactions)
        expense_ratio = self._calculate_expense_ratio(transactions, monthly_income)
        
        prompt = f"""
        Based on:
        - Monthly Income: Rs. {monthly_income}
        - Expense Ratio: {expense_ratio:.2f}%
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
                month_key = t['date'].strftime('%Y-%m')
                monthly_totals[month_key] = monthly_totals.get(month_key, 0) + t['amount']
        
        if not monthly_totals:
            return 0
        return sum(monthly_totals.values()) / len(monthly_totals)

    def _calculate_investable_amount(self, total_savings, emergency_fund, monthly_expenses):
        safety_buffer = emergency_fund + (monthly_expenses * 3)
        return max(0, total_savings - safety_buffer)

    def _analyze_expenses_by_category(self, transactions):
        category_totals = {}
        for t in transactions:
            if t.get('category') != 'Income':
                category_totals[t['category']] = category_totals.get(t['category'], 0) + t['amount']
        return {k: round(v, 2) for k, v in category_totals.items()}

    def _calculate_risk_profile(self, transactions):
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
                month_key = t['date'].strftime('%Y-%m')
                monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + t['amount']
        
        if not monthly_expenses:
            return 0
            
        values = list(monthly_expenses.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return (variance ** 0.5) / mean

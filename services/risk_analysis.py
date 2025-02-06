from datetime import datetime
import google.generativeai as genai
from config import Config

class RiskAnalysisService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_risk(self, transactions, savings):
        monthly_spending = self._calculate_monthly_spending(transactions)
        avg_monthly_spend = sum(monthly_spending.values()) / len(monthly_spending) if monthly_spending else 0
        total_spent = sum(t['amount'] for t in transactions)
        
        context = f"""
        Financial Risk Analysis Data:
        - Total Spending: Rs. {total_spent:,.2f}
        - Average Monthly Spending: Rs. {avg_monthly_spend:,.2f}
        - Current Savings: Rs. {savings:,.2f}
        - Monthly Spending Pattern: {monthly_spending}
        
        Based on this data:
        1. Calculate risk score (1-10, where 10 is highest risk)
        2. Estimate months until potential bankruptcy if spending patterns continue
        3. Provide detailed risk assessment and specific recommendations
        4. List key risk factors identified from spending patterns
        
        Format as JSON with keys: risk_score, months_to_bankruptcy, assessment, recommendations
        """
        
        try:
            response = self.model.generate_content(context)
            return response.text
        except Exception as e:
            return {"error": f"Error analyzing risk: {str(e)}"}

    def _calculate_monthly_spending(self, transactions):
        monthly_totals = {}
        for t in transactions:
            date = datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
            month_key = date.strftime('%Y-%m')
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + t['amount']
        return dict(sorted(monthly_totals.items()))
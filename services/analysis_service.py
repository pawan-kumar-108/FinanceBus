import google.generativeai as genai
from config import Config

class AnalysisService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_spending(self, transactions):
        spending_summary = self._prepare_spending_summary(transactions)
        monthly_totals = self._prepare_monthly_totals(transactions)
        
        prompt = f"""
        As a financial advisor, analyze this spending data:
        
        Monthly spending totals (in Rs.):
        {monthly_totals}
        
        Category-wise spending (in Rs.):
        {spending_summary}
        
        Provide:
        1. A detailed analysis of monthly spending patterns and trends
        2. Category-wise breakdown and insights
        3. Specific recommendations for reducing expenses in high-spending categories
        4. Potential savings opportunities based on the spending patterns
        5. Actionable steps for better financial management
        
        Format the response in a clear, structured manner with proper headings and bullet points.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

    def chat_response(self, message, transactions):
        spending_summary = self._prepare_spending_summary(transactions)
        monthly_totals = self._prepare_monthly_totals(transactions)
        
        prompt = f"""
        Context: 
        User's monthly spending (in Rs.): {monthly_totals}
        Category-wise spending (in Rs.): {spending_summary}
        
        User question: {message}
        
        Provide personalized financial advice based on their spending patterns and specific question.
        Make sure to reference relevant spending data in your response and provide actionable suggestions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _prepare_spending_summary(self, transactions):
        category_totals = {}
        for transaction in transactions:
            # Handle both Transaction objects and dictionaries
            if isinstance(transaction, dict):
                category = transaction['category']
                amount = transaction['amount']
            else:
                category = transaction.category
                amount = transaction.amount
                
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount
        return category_totals

    def _prepare_monthly_totals(self, transactions):
        monthly_totals = {}
        for transaction in transactions:
            # Handle both Transaction objects and dictionaries
            if isinstance(transaction, dict):
                date = transaction['date']
                amount = transaction['amount']
                if isinstance(date, str):
                    from datetime import datetime
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            else:
                date = transaction.date
                amount = transaction.amount
                
            month_key = date.strftime('%Y-%m')
            if month_key in monthly_totals:
                monthly_totals[month_key] += amount
            else:
                monthly_totals[month_key] = amount
        return dict(sorted(monthly_totals.items()))
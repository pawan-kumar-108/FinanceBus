import google.generativeai as genai
from config import Config

class AnalysisService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_spending(self, transactions):
        # Prepare transaction data for analysis
        spending_summary = self._prepare_spending_summary(transactions)
        
        # Create prompt for Gemini
        prompt = f"""
        As a financial advisor, analyze this spending data:
        {spending_summary}
        
        Provide:
        1. Specific recommendations for reducing expenses after finding hidden patterns in the transactions
        2. Areas of unnecessary spending that can be cut down
        
        Format the response in a clear, structured manner. All transaction data are in Indian Rupee represented as Rs.

        Also, let the user know based on the spending pattern, is the user eligible to invest in stock or SIP or Mutual funds.

        Answer all the questions in crisp points.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def chat_response(self, message, transactions):
        spending_summary = self._prepare_spending_summary(transactions)
        
        prompt = f"""
        Context: User's spending summary: {spending_summary}
        
        User question: {message}
        
        Provide financial advice based on their spending patterns and question. Don't deviate from the question asked!Consider all payments in Rupees written as Rs.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def _prepare_spending_summary(self, transactions):
        category_totals = {}
        for transaction in transactions:
            category = transaction['category']
            amount = transaction['amount']
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount
                
        return category_totals

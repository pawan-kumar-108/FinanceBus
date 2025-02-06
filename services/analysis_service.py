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
        1. A detailed analysis of spending patterns (existing expenses are in Rupees written as Rs.)
        2. Specific recommendations for reducing expenses 
        3. Areas of unnecessary spending
        4. Potential savings opportunities
        
        Format the response in a clear, structured manner.
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

# services/goal_analysis_service.py
import google.generativeai as genai
from datetime import datetime
from config import Config

# services/goal_analysis_service.py
import google.generativeai as genai
from datetime import datetime
from config import Config

class GoalAnalysisService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_short_term_goal(self, goal_data, transactions, emergency_fund):
        # Format the date properly before using it
        formatted_start_date = self._format_date(goal_data['start_date'])
        goal_data['start_date'] = formatted_start_date

        prompt = f"""
        As a financial advisor, analyze if this short-term financial goal is achievable:
        
        Goal Details:
        - Name: {goal_data['name']}
        - Total Amount Needed: Rs. {goal_data['total_amount']}
        - Already Saved: Rs. {goal_data['due_amount']}
        - Timeframe: {goal_data['timeframe']} months
        - Start Date: {formatted_start_date}
        
        User's Financial Context:
        - Emergency Fund: Rs. {emergency_fund}
        - Past Transaction Summary: {self._summarize_transactions(transactions)}
        
        Provide:
        1. Clear YES/NO on goal achievability
        2. Brief explanation (max 3 points)
        3. Monthly saving target needed
        4. Specific action steps to achieve the goal
        
        Keep the response concise and actionable.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_long_term_goal(self, goal_data, transactions, emergency_fund):
        # Format the date properly before using it
        formatted_start_date = self._format_date(goal_data['start_date'])
        goal_data['start_date'] = formatted_start_date

        prompt = f"""
        Analyze this long-term financial goal's feasibility:
        
        Goal Details:
        - Name: {goal_data['name']}
        - Target Amount: Rs. {goal_data['total_amount']}
        - Current Progress: Rs. {goal_data['due_amount']}
        - Timeline: {goal_data['timeframe']} years
        - Start Date: {formatted_start_date}
        
        Financial Context:
        - Emergency Fund: Rs. {emergency_fund}
        - Transaction History: {self._summarize_transactions(transactions)}
        
        Provide only:
        1. Completion percentage prediction
        2. Two key recommendations
        3. Monthly investment needed
        
        Keep analysis under 100 words.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_loan_feasibility(self, loan_data, transactions):
        prompt = f"""
        Analyze this loan application:
        
        Loan Details:
        - Name: {loan_data['name']}
        - Principal: Rs. {loan_data['principal_amount']}
        - Interest Rate: {loan_data['interest_rate']}%
        - Tenure: {loan_data['tenure']} years
        
        Transaction History: {self._summarize_transactions(transactions)}
        
        Provide only:
        1. Monthly EMI amount
        2. Three-step action plan
        3. Key requirements/documents needed
        4. Risk assessment (one line)
        
        Format as bullet points, keep it brief.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def _format_date(self, date_str):
        """
        Format date string to ensure it's in correct ISO format with proper padding
        """
        try:
            if isinstance(date_str, str):
                # Split into date and time parts
                if 'T' in date_str:
                    date_part, time_part = date_str.split('T')
                else:
                    date_part = date_str
                    time_part = "00:00:00.000Z"

                # Split date part and pad with zeros where needed
                year, month, day = date_part.split('-')
                month = month.zfill(2)  # Ensure month is 2 digits
                day = day.zfill(2)      # Ensure day is 2 digits
                
                # Reconstruct ISO format string
                formatted_date = f"{year}-{month}-{day}T{time_part}"
                
                # Validate the formatted date
                datetime.fromisoformat(formatted_date.replace('Z', '+00:00'))
                return formatted_date
            
            return date_str
        except Exception as e:
            raise ValueError(f"Invalid date format: {date_str}. Please use YYYY-MM-DD format.")

    def _summarize_transactions(self, transactions):
        # Calculate monthly averages for spending and income
        monthly_totals = {}
        for t in transactions:
            try:
                date = t.get('date')
                if isinstance(date, str):
                    date = datetime.fromisoformat(self._format_date(date).replace('Z', '+00:00'))
                elif isinstance(date, datetime):
                    date = date
                else:
                    date = datetime.utcnow()

                month_key = date.strftime('%Y-%m')
                amount = float(t['amount'])
                
                if month_key not in monthly_totals:
                    monthly_totals[month_key] = {'spending': 0, 'income': 0}
                    
                if t.get('category') == 'Income':
                    monthly_totals[month_key]['income'] += amount
                else:
                    monthly_totals[month_key]['spending'] += amount
            except Exception as e:
                print(f"Error processing transaction date: {e}")
                continue
        
        # Calculate averages
        total_months = len(monthly_totals)
        if total_months == 0:
            return "No transaction history available"
            
        avg_monthly_spending = sum(m['spending'] for m in monthly_totals.values()) / total_months
        avg_monthly_income = sum(m['income'] for m in monthly_totals.values()) / total_months
        
        return f"Average Monthly Income: Rs. {avg_monthly_income:.2f}, Average Monthly Spending: Rs. {avg_monthly_spending:.2f}"

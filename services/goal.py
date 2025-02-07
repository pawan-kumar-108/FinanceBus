# services/goal_analysis_service.py
import google.generativeai as genai
from datetime import datetime
import re
from config import Config

class GoalAnalysisService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_short_term_goal(self, goal_data, transactions, emergency_fund):
        try:
            # Validate and sanitize input data
            self._validate_goal_data(goal_data)
            
            # Format the date properly before using it
            formatted_start_date = self._format_date(goal_data['start_date'])
            
            # Convert numeric values to float
            total_amount = float(goal_data['total_amount'])
            due_amount = float(goal_data['due_amount'])
            emergency_fund = float(emergency_fund)
            timeframe = int(goal_data['timeframe'])

            prompt = f"""
            As a financial advisor, analyze if this short-term financial goal is achievable:
            
            Goal Details:
            - Name: {goal_data['name']}
            - Total Amount Needed: Rs. {total_amount}
            - Already Saved: Rs. {due_amount}
            - Timeframe: {timeframe} months
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
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error analyzing short-term goal: {str(e)}")

    def analyze_long_term_goal(self, goal_data, transactions, emergency_fund):
        try:
            # Validate and sanitize input data
            self._validate_goal_data(goal_data)
            
            # Format the date properly before using it
            formatted_start_date = self._format_date(goal_data['start_date'])
            
            # Convert numeric values to float
            total_amount = float(goal_data['total_amount'])
            due_amount = float(goal_data['due_amount'])
            emergency_fund = float(emergency_fund)
            timeframe = int(goal_data['timeframe'])

            prompt = f"""
            Analyze this long-term financial goal's feasibility:
            
            Goal Details:
            - Name: {goal_data['name']}
            - Target Amount: Rs. {total_amount}
            - Current Progress: Rs. {due_amount}
            - Timeline: {timeframe} years
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
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error analyzing long-term goal: {str(e)}")

    def analyze_loan_feasibility(self, loan_data, transactions):
        try:
            # Validate loan data
            self._validate_loan_data(loan_data)
            
            # Convert numeric values
            principal = float(loan_data['principal_amount'])
            interest_rate = float(loan_data['interest_rate'])
            tenure = int(loan_data['tenure'])

            prompt = f"""
            Analyze this loan application:
            
            Loan Details:
            - Name: {loan_data['name']}
            - Principal: Rs. {principal}
            - Interest Rate: {interest_rate}%
            - Tenure: {tenure} years
            
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
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error analyzing loan feasibility: {str(e)}")

    def _validate_goal_data(self, goal_data):
        """Validate goal data inputs"""
        required_fields = ['name', 'total_amount', 'due_amount', 'timeframe', 'start_date']
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in goal_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
        # Validate numeric fields
        try:
            float(goal_data['total_amount'])
            float(goal_data['due_amount'])
            int(goal_data['timeframe'])
        except ValueError:
            raise ValueError("Invalid numeric values provided")
            
        # Validate name
        if not goal_data['name'] or not isinstance(goal_data['name'], str):
            raise ValueError("Invalid goal name")

    def _validate_loan_data(self, loan_data):
        """Validate loan data inputs"""
        required_fields = ['name', 'principal_amount', 'interest_rate', 'tenure']
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in loan_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
        # Validate numeric fields
        try:
            float(loan_data['principal_amount'])
            float(loan_data['interest_rate'])
            int(loan_data['tenure'])
        except ValueError:
            raise ValueError("Invalid numeric values provided")
            
        # Validate name
        if not loan_data['name'] or not isinstance(loan_data['name'], str):
            raise ValueError("Invalid loan name")

    def _format_date(self, date_input):
        """Format date string to ensure it's in correct ISO format with proper padding"""
        try:
            if isinstance(date_input, datetime):
                return date_input.isoformat()

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
                return f"{year}-{month}-{day}T{time_part}"

            raise ValueError("Invalid date format")
        except Exception as e:
            raise ValueError(f"Error formatting date: {str(e)}")

    def _summarize_transactions(self, transactions):
        """Summarize transaction history with error handling"""
        try:
            # Calculate monthly averages for spending and income
            monthly_totals = {}
            for t in transactions:
                try:
                    # Get and format the date
                    date = t.get('date')
                    if isinstance(date, str):
                        formatted_date = self._format_date(date)
                        date = datetime.fromisoformat(formatted_date)
                    elif isinstance(date, datetime):
                        date = date
                    else:
                        continue

                    month_key = date.strftime('%Y-%m')
                    amount = float(t['amount'])
                    
                    if month_key not in monthly_totals:
                        monthly_totals[month_key] = {'spending': 0, 'income': 0}
                        
                    if t.get('category') == 'Income':
                        monthly_totals[month_key]['income'] += amount
                    else:
                        monthly_totals[month_key]['spending'] += amount
                except Exception as e:
                    print(f"Error processing transaction: {e}")
                    continue
            
            # Calculate averages
            total_months = len(monthly_totals)
            if total_months == 0:
                return "No transaction history available"
                
            avg_monthly_spending = sum(m['spending'] for m in monthly_totals.values()) / total_months
            avg_monthly_income = sum(m['income'] for m in monthly_totals.values()) / total_months
            
            return f"Average Monthly Income: Rs. {avg_monthly_income:.2f}, Average Monthly Spending: Rs. {avg_monthly_spending:.2f}"
        except Exception as e:
            return "Error summarizing transactions"

from datetime import datetime
import google.generativeai as genai
from config import Config

class RiskAnalysisService:
    def analyze_risk(self, transactions, savings):
        if not transactions:
            return {"error": "No transaction data available"}
            
        try:
            # Calculate key metrics
            monthly_spending = self._calculate_monthly_spending(transactions)
            avg_monthly_spend = sum(monthly_spending.values()) / len(monthly_spending) if monthly_spending else 0
            total_spent = sum(float(t['amount']) for t in transactions)
            
            # Calculate risk score (1-10)
            risk_score = self._calculate_risk_score(avg_monthly_spend, savings)
            
            # Calculate months to bankruptcy
            months_to_bankruptcy = self._calculate_bankruptcy_timeline(savings, avg_monthly_spend)
            
            return {
                "risk_score": risk_score,
                "months_to_bankruptcy": months_to_bankruptcy
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _calculate_risk_score(self, avg_monthly_spend, savings):
        if avg_monthly_spend <= 0:
            return 1
            
        # Months of savings coverage
        months_coverage = savings / avg_monthly_spend
        
        # Risk increases as months of coverage decreases
        if months_coverage >= 12:  # 1 year or more of savings
            risk = 1
        elif months_coverage >= 6:  # 6-12 months of savings
            risk = 3
        elif months_coverage >= 3:  # 3-6 months of savings
            risk = 5
        elif months_coverage >= 1:  # 1-3 months of savings
            risk = 7
        else:  # Less than 1 month of savings
            risk = 10
            
        return int(risk)

    def _calculate_bankruptcy_timeline(self, savings, avg_monthly_spend):
        if avg_monthly_spend <= 0:
            return float('inf')  # No risk of bankruptcy if no spending
            
        # Simple calculation: savings divided by monthly spend
        months = int(savings / avg_monthly_spend)
        
        # Return at least 1 month if there's any spending
        return max(1, months)

    def _calculate_monthly_spending(self, transactions):
        monthly_totals = {}
        for t in transactions:
            try:
                date = t.get('date')
                if isinstance(date, str):
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                month_key = date.strftime('%Y-%m')
                amount = float(t['amount'])
                monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
            except Exception as e:
                print(f"Error processing transaction: {e}")
                continue
        return dict(sorted(monthly_totals.items()))

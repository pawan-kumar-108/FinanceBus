from datetime import datetime
import pandas as pd

class VisualizationService:
    @staticmethod
    def prepare_spending_over_time(transactions):
        if not transactions:
            return {
                'datasets': [{
                    'data': []
                }]
            }

        df = pd.DataFrame([{
            'date': t.date,
            'amount': t.amount
        } for t in transactions])
        
        # Group by date and sum amounts
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
        
        # Sort by date and create data points
        daily_spending = daily_spending.sort_index()
        
        return {
            'datasets': [{
                'data': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'amount': float(amount)
                    }
                    for date, amount in daily_spending.items()
                ]
            }]
        }

    @staticmethod
    def prepare_category_distribution(transactions):
        if not transactions:
            return {
                'datasets': [{
                    'data': []
                }]
            }

        # Calculate category totals
        category_totals = {}
        for t in transactions:
            if t.category in category_totals:
                category_totals[t.category] += t.amount
            else:
                category_totals[t.category] = t.amount
        
        return {
            'datasets': [{
                'data': [
                    {
                        'category': category,
                        'value': float(amount)
                    }
                    for category, amount in category_totals.items()
                ]
            }]
        }

    @staticmethod
    def prepare_monthly_trend(transactions):
        if not transactions:
            return {
                'datasets': [{
                    'data': []
                }]
            }

        df = pd.DataFrame([{
            'date': t.date,
            'amount': t.amount
        } for t in transactions])
        
        # Group by month and sum amounts
        monthly_spending = df.groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum()
        
        # Sort by date
        monthly_spending = monthly_spending.sort_index()
        
        return {
            'datasets': [{
                'data': [
                    {
                        'month': month,
                        'amount': float(amount)
                    }
                    for month, amount in monthly_spending.items()
                ]
            }]
        }
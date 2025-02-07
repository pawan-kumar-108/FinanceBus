from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from models.transaction import Transaction
from services.analysis_service import AnalysisService
from services.visualization_service import VisualizationService
from config import Config

from services.risk_analysis import RiskAnalysisService
from pymongo import MongoClient

from flask import render_template_string

app = Flask(__name__)
CORS(app)

#mongo k inititialization k liye!!
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DB_NAME]
transactions_collection = db["transactions"]

# Initialize services
analysis_service = AnalysisService()
visualization_service = VisualizationService()

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({"categories": Config.CATEGORIES})

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'category', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate category
    if data['category'] not in Config.CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400
    
    # Format date
    try:
        if 'date' in data and data['date']:
            # If date is provided, ensure it's properly formatted
            date_str = data['date']
            if isinstance(date_str, str):
                # Split into date and time parts
                parts = date_str.split('T')
                if len(parts) > 1:
                    date_part = parts[0]
                    time_part = parts[1]
                    
                    # Pad date components with zeros
                    year, month, day = date_part.split('-')
                    month = month.zfill(2)
                    day = day.zfill(2)
                    
                    # Reconstruct ISO format string
                    date = f"{year}-{month}-{day}T{time_part}"
                else:
                    date = datetime.utcnow().isoformat()
            else:
                date = datetime.utcnow().isoformat()
        else:
            date = datetime.utcnow().isoformat()
    except Exception:
        date = datetime.utcnow().isoformat()
    
    # Create transaction document
    transaction = {
        "name": data['name'],
        "category": data['category'],
        "amount": float(data['amount']),
        "description": data.get('description'),
        "date": date
    }
    
    transactions_collection.insert_one(transaction)
    
    # Fetch recent transactions
    recent_transactions = list(transactions_collection.find().sort("date", -1).limit(10))
    for transaction in recent_transactions:
        transaction["_id"] = str(transaction["_id"])
    
    return jsonify({
        "message": "Transaction added successfully",
        "recent_transactions": recent_transactions
    })


@app.route('/api/analysis')
def get_analysis():
    try:
        # Get transactions directly from MongoDB
        transactions = list(transactions_collection.find())
        
        # Convert MongoDB ObjectId to string and prepare transactions for analysis
        transaction_dicts = []
        for t in transactions:
            t['_id'] = str(t['_id'])  # Convert ObjectId to string
            
            # Handle date conversion with proper error handling
            try:
                if isinstance(t.get('date'), str):
                    # First, standardize the date format
                    # Replace any potential single-digit dates with leading zeros
                    date_str = t['date']
                    parts = date_str.split('T')
                    if len(parts) > 1:
                        date_part = parts[0]
                        time_part = parts[1]
                        
                        # Split date part and pad with zeros if needed
                        year, month, day = date_part.split('-')
                        month = month.zfill(2)  # Ensure month is 2 digits
                        day = day.zfill(2)      # Ensure day is 2 digits
                        
                        # Reconstruct the ISO format string
                        standardized_date = f"{year}-{month}-{day}T{time_part}"
                        t['date'] = datetime.fromisoformat(standardized_date)
                elif isinstance(t.get('date'), datetime):
                    pass  # Keep datetime objects as is
                else:
                    # If date is missing or in unknown format, use current time
                    t['date'] = datetime.utcnow()
            except Exception as date_error:
                print(f"Date parsing error for transaction {t['_id']}: {date_error}")
                # Set to current time if parsing fails
                t['date'] = datetime.utcnow()
            
            transaction_dicts.append(t)
        
        # Get analysis from the analysis service
        analysis = analysis_service.analyze_spending(transaction_dicts)
        
        return jsonify({
            "analysis": analysis,
            "transaction_count": len(transaction_dicts)
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # For debugging
        return jsonify({"error": str(e)}), 500
    

# @app.route('/api/chat', methods=['POST'])
# def chat_with_advisor():
#     data = request.json
#     if 'message' not in data:
#         return jsonify({"error": "Message is required"}), 400
    
#     transactions = list(transactions_collection.find())
#     for transaction in transactions:
#         transaction["_id"] = str(transaction["_id"])
    
#     response = analysis_service.chat_response(data['message'], transactions)
    
#     return jsonify({
#         "response": response
#     })

@app.route('/api/chat', methods=['POST'])
def chat_with_advisor():
    try:
        data = request.json
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        transactions = list(transactions_collection.find())
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        # Use the already initialized service instance
        response = analysis_service.chat_response(data['message'], transactions)
        
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/risk-analysis', methods=['POST'])
def analyze_financial_risk():
    try:
        data = request.json
        if 'savings' not in data:
            return jsonify({"error": "Current savings amount is required"}), 400
            
        transactions = list(transactions_collection.find())
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        risk_service = RiskAnalysisService()
        analysis = risk_service.analyze_risk(transactions, float(data['savings']))
        
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    
#only for testing purpose, will not be used in production setting!!
@app.route('/test/visualizations', methods=['GET'])
def test_visualizations():
    transactions = Transaction.get_transactions()
    visualizations = visualization_service.generate_spending_graphs(transactions)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visualization Test</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            .chart { width: 100%; height: 500px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div id="monthlyTrend" class="chart"></div>
        <div id="categoryDistribution" class="chart"></div>
        <div id="dailySpending" class="chart"></div>
        
        <script>
            const graphs = {{ graphs|safe }};
            
            // Monthly Trend
            if (graphs.monthly_trend) {
                const monthlyData = JSON.parse(graphs.monthly_trend);
                Plotly.newPlot('monthlyTrend', monthlyData.data, monthlyData.layout);
            }
            
            // Category Distribution
            if (graphs.category_distribution) {
                const categoryData = JSON.parse(graphs.category_distribution);
                Plotly.newPlot('categoryDistribution', categoryData.data, categoryData.layout);
            }
            
            // Daily Spending
            if (graphs.daily_spending) {
                const dailyData = JSON.parse(graphs.daily_spending);
                Plotly.newPlot('dailySpending', dailyData.data, dailyData.layout);
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template, graphs=visualizations)

if __name__ == '__main__':
    app.run(debug=True)

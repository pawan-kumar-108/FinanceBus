from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    DATA_FILE = 'data/transactions.json'
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = "test/users/transactions"
    CATEGORIES = [
        'Rent', 'Food', 'Transportation', 'Entertainment', 
        'Utilities', 'Shopping', 'Healthcare', 'Education',
        'Savings', 'Other'
    ]


# models/transaction.py
from datetime import datetime
from bson import ObjectId
from config import Config
from pymongo import MongoClient

class Transaction:
    def __init__(self, name, category, amount, date=None, description=None, _id=None):
        self.name = name
        self.category = category
        self.amount = float(amount)
        self.date = date if date else datetime.utcnow()
        self.description = description
        self._id = str(_id) if _id else None

    @staticmethod
    def get_all():
        client = MongoClient(Config.MONGODB_URI)
        db = client[Config.DB_NAME]
        transactions = list(db.transactions.find())
        
        # Convert MongoDB documents to Transaction objects
        transaction_list = []
        for t in transactions:
            transaction_list.append({
                'name': t.get('name'),
                'category': t.get('category'),
                'amount': float(t.get('amount', 0)),
                'date': t.get('date'),
                'description': t.get('description'),
                '_id': str(t.get('_id'))
            })
        
        client.close()
        return transaction_list

    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'amount': self.amount,
            'date': self.date,
            'description': self.description,
            '_id': self._id
        }

    @staticmethod
    def from_dict(data):
        return Transaction(
            name=data.get('name'),
            category=data.get('category'),
            amount=data.get('amount'),
            date=data.get('date'),
            description=data.get('description'),
            _id=data.get('_id')
        )
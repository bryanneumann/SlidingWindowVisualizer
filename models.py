from app import db
from datetime import datetime


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 0-5 stars
    feedback = db.Column(db.Text, nullable=True)  # Optional anonymous feedback
    user_ip = db.Column(db.String(45), nullable=True)  # Store IP for basic analytics (IPv4/IPv6)
    user_agent = db.Column(db.String(500), nullable=True)  # Browser info for analytics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}: {self.rating} stars>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat()
        }
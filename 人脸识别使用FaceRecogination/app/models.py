from datetime import datetime
from app import db

class UnknownFace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    face_location = db.Column(db.String(255))
    duration = db.Column(db.Float)  # 存储为浮点数
    
    def __repr__(self):
        return f'<UnknownFace {self.timestamp}>'
    
    @property
    def formatted_duration(self):
        """返回格式化的持续时间"""
        return f"{self.duration:.2f}" if self.duration else "0.00"
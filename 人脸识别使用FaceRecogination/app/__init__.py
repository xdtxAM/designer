from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import click

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.routes import main
    app.register_blueprint(main)
    
    # 注册自定义命令
    @app.cli.command('initdb')
    def initdb_command():
        """初始化数据库"""
        click.echo('正在初始化数据库...')
        db.create_all()
        click.echo('数据库初始化完成！')
    
    @app.cli.command('dropdb')
    def dropdb_command():
        """删除数据库"""
        click.echo('正在删除数据库...')
        db.drop_all()
        click.echo('数据库已删除！')
    
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # 添加 session 密钥
    
    return app
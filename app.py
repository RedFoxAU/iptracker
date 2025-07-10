from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
db = SQLAlchemy(app)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    hostname = db.Column(db.String(100), nullable=True)
    port = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    services = Service.query.order_by(Service.created_at.desc()).all()
    return render_template('index.html', services=services)

@app.route('/add', methods=['POST'])
def add_service():
    if request.method == 'POST':
        ip = request.form.get('ip', '').strip()
        hostname = request.form.get('hostname', '').strip()
        port = request.form.get('port', '').strip()
        service = request.form.get('service', '').strip()
        
        if not ip or not port or not service:
            flash('Please fill in all required fields (IP, Port, and Service)', 'error')
            return redirect(url_for('index'))
        
        try:
            port = int(port)
            if port < 1 or port > 65535:
                flash('Port must be between 1 and 65535', 'error')
                return redirect(url_for('index'))
        except ValueError:
            flash('Port must be a valid number', 'error')
            return redirect(url_for('index'))
        
        new_service = Service(ip=ip, hostname=hostname, port=port, service=service)
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_service(id):
    if request.method == 'POST':
        service = Service.query.get_or_404(id)
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    service = Service.query.get_or_404(id)
    
    if request.method == 'POST':
        service.ip = request.form['ip']
        service.hostname = request.form.get('hostname', '')
        service.port = request.form['port']
        service.service = request.form['service']
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', service=service)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5003, debug=True)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from flask_login import current_user, login_required
from datetime import datetime
import app
import app.instance
from app.models import Report, SalesData
from app import db

UPLOAD_FOLDER = 'app/uploads'
routes = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'csv'}

@routes.route("/")
def home():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'sales-report' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files.get('sales-report')
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(os.path.dirname(file_path))
            
            file.save(file_path)
            
            # Create a new report entry for the user
            report = Report(
                user_id=current_user.id,
                file_path=file_path,
                report_name=filename
            )
            db.session.add(report)
            
            # Set the newly uploaded report as active
            for r in current_user.reports:
                r.is_active = False
            report.is_active = True
            
            try:
                db.session.commit()
                flash('File successfully uploaded and report created', 'success')
                return redirect(url_for('routes.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'An unexpected error occurred: {str(e)}', 'error')
    
    return render_template('upload.html')

@routes.route('/dashboard')
@login_required
def dashboard():
    selected_report_id = None
    
    if request.method == 'POST':
        selected_report_id = request.form.get('selected_report_id')

    if not selected_report_id:
        active_report = next((report for report in current_user.reports if report.is_active), None)
        if active_report:
            selected_report_id = active_report.id

    active_report = Report.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not active_report:
        flash('No active report found. Please upload a report.', 'error')
        return redirect(url_for('routes.upload_file'))
    
    # Load the CSV file
    df = pd.read_csv(active_report.file_path)
    
    # Ensure required columns exist
    required_columns = {'date', 'product_id', 'customer_id', 'quantity', 'total_amount'}
    if not required_columns.issubset(df.columns):
        flash('The active report is missing required columns', 'error')
        return redirect(url_for('routes.upload_file'))
    
    # Generate visualizations
    bar_chart = px.bar(df, x='date', y='total_amount', title='Monthly Sales')
    line_chart = px.line(df, x='date', y='total_amount', title='Sales Trends')
    pie_chart = px.pie(df, names='product_id', values='total_amount', title='Product Category Distribution')
    
    return render_template('dashboard.html', 
                           selected_report_id=selected_report_id,
                           bar_chart=bar_chart.to_html(full_html=False), 
                           line_chart=line_chart.to_html(full_html=False), 
                           pie_chart=pie_chart.to_html(full_html=False))

@routes.route('/performance')
@login_required
def performance():
    selected_report_id = None
    
    if request.method == 'POST':
        selected_report_id = request.form.get('selected_report_id')

    if not selected_report_id:
        active_report = next((report for report in current_user.reports if report.is_active), None)
        if active_report:
            selected_report_id = active_report.id

    active_report = Report.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not active_report:
        flash('No active report found. Please upload a report.', 'error')
        return redirect(url_for('routes.upload_file'))
    
    # Load the CSV file
    df = pd.read_csv(active_report.file_path)

    total_sales = df['total_amount'].sum()
    average_sales = df['total_amount'].mean()
    min_value = df['total_amount'].min()
    max_value = df['total_amount'].max()
    
    top_selling_products = df.groupby('product_id')['total_amount'].sum().sort_values(ascending=False).head(10)
    
    total_sales = f"{total_sales:.3f}"
    average_sales = f"{average_sales:.3f}"
    max_value = f"{max_value:.3f}"
    min_value = f"{min_value:.3f}"
    
    return render_template('performance.html',
                           max_value=max_value,
                           min_value=min_value,
                           total_sales=total_sales,
                           average_sales=average_sales,
                           top_selling_products=top_selling_products.to_dict())

@routes.route('/insights')
@login_required
def insights():
    selected_report_id = None
    
    if request.method == 'POST':
        selected_report_id = request.form.get('selected_report_id')

    if not selected_report_id:
        active_report = next((report for report in current_user.reports if report.is_active), None)
        if active_report:
            selected_report_id = active_report.id

    active_report = Report.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not active_report:
        flash('No active report found. Please upload a report.', 'error')
        return redirect(url_for('routes.upload_file'))
    
    # Load the CSV file
    df = pd.read_csv(active_report.file_path)

    purchase_frequency = df['date'].value_counts().sort_index()
    purchase_frequency_chart = px.bar(purchase_frequency, x=purchase_frequency.index, y=purchase_frequency.values, title='Purchase Frequency')
    
    return render_template('insights.html', purchase_frequency_chart=purchase_frequency_chart.to_html(full_html=False))

@routes.route('/trends')
@login_required
def trends():
    selected_report_id = None
    
    if request.method == 'POST':
        selected_report_id = request.form.get('selected_report_id')

    if not selected_report_id:
        active_report = next((report for report in current_user.reports if report.is_active), None)
        if active_report:
            selected_report_id = active_report.id

    active_report = Report.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not active_report:
        flash('No active report found. Please upload a report.', 'error')
        return redirect(url_for('routes.upload_file'))
    
    # Load the CSV file
    df = pd.read_csv(active_report.file_path)
    
    df['date'] = pd.to_datetime(df['date'])
    df['date_ordinal'] = df['date'].apply(lambda x: x.toordinal())
    
    X = df[['date_ordinal']]
    y = df['total_amount']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    trend_chart = px.scatter(x=X_test['date_ordinal'], y=y_test, title='Sales Trends')
    trend_chart.add_scatter(x=X_test['date_ordinal'], y=predictions, mode='lines', name='Trend Prediction')
    
    return render_template('trends.html', trend_chart=trend_chart.to_html(full_html=False))

@routes.route('/switch_report/<int:report_id>', methods=['POST'])
@login_required
def switch_report(report_id):
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first()
    if not report:
        flash('Report not found or you do not have permission to access it', 'error')
        return redirect(url_for('routes.dashboard'))
    
    # Deactivate all other reports
    for r in current_user.reports:
        r.is_active = False
    
    # Activate selected report
    report.is_active = True
    
    try:
        db.session.commit()
        flash('Switched to the selected report', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('routes.dashboard'))

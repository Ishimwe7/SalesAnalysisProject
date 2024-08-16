from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from flask_login import login_required
from datetime import datetime
import app
import app.instance
from app.models import SalesData
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
            
            try:
                data = pd.read_csv(file_path)
                
                # Validate CSV columns
                required_columns = {'date', 'product_id', 'customer_id','quantity','total_amount'}
                if not required_columns.issubset(data.columns):
                    flash('CSV file is missing required columns', 'error')
                    return redirect(request.url)
                
                # Process and save data
                for _, row in data.iterrows():
                    try:
                        date_object = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    except ValueError:
                        flash(f"Invalid date format in row: {row['date']}", 'error')
                        return redirect(request.url)
                    new_record = SalesData(
                        date=date_object,
                        product_id=row['product_id'],
                        customer_id=row['customer_id'],
                        quantity=row['quantity'],
                        total_amount=row['total_amount']
                    )
                    db.session.add(new_record)
                db.session.commit()
                
                flash('File successfully uploaded and processed', 'success')
                return redirect(url_for('routes.home'))
            
            except pd.errors.EmptyDataError:
                flash('The file is empty', 'error')
            except pd.errors.ParserError:
                flash('Error parsing the file', 'error')
            except Exception as e:
                flash(f'An unexpected error occurred: {str(e)}', 'error')
            
            # Handle exceptions and errors
            db.session.rollback()
        else:
            flash('Invalid file format. Only CSV files are allowed.', 'error')
    
    return render_template('upload.html')

@routes.route('/dashboard')
@login_required
def dashboard():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product_id,d.customer_id,d.quantity, d.total_amount) for d in sales_data], columns=['date', 'product_id', 'customer_id', 'quantity', 'total_amount'])
    bar_chart = px.bar(df, x='date', y='total_amount', title='Monthly Sales')
    line_chart = px.line(df, x='date', y='total_amount', title='Sales Trends')
    pie_chart = px.pie(df, names='product_id', values='total_amount', title='Product Category Distribution')
    return render_template('dashboard.html', bar_chart=bar_chart.to_html(full_html=False), line_chart=line_chart.to_html(full_html=False), pie_chart=pie_chart.to_html(full_html=False))

@routes.route('/performance')
@login_required
def performance():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product_id, d.customer_id, d.quantity, d.total_amount) for d in sales_data], columns=['date', 'product_id', 'customer_id', 'quantity','total_amount'])
    total_sales = df['total_amount'].sum()
    average_sales = df['total_amount'].mean()
    min_value = df['total_amount'].min()
    max_value = df['total_amount'].max()
    top_selling_products = df.groupby('product_id')['total_amount'].sum().sort_values(ascending=False).head(10)
    total_sales = f"{total_sales:.3f}"
    average_sales = f"{average_sales:.3f}"
    max_value = f"{max_value:.3f}"
    min_value = f"{min_value:.3f}"
    return render_template('performance.html',max_value=max_value,min_value=min_value, total_sales=total_sales, average_sales=average_sales, top_selling_products=top_selling_products.to_dict())

@routes.route('/insights')
@login_required
def insights():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product_id, d.customer_id, d.quantity, d.total_amount) for d in sales_data], columns=['date', 'product_id','customer_id', 'quantity', 'total_amount'])
    purchase_frequency = df['date'].value_counts().sort_index()
    purchase_frequency_chart = px.bar(purchase_frequency, x=purchase_frequency.index, y=purchase_frequency.values, title='Purchase Frequency')
    return render_template('insights.html', purchase_frequency_chart=purchase_frequency_chart.to_html(full_html=False))

@routes.route('/trends')
@login_required
def trends():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product_id, d.customer_id, d.quantity, d.total_amount) for d in sales_data], columns=['date', 'product_id','customer_id', 'quantity', 'total_amount'])
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

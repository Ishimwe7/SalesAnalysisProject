# from flask import Flask
# from flask import render_template
# import os
# from flask import Flask, request, redirect, url_for, render_template, flash
# from werkzeug.utils import secure_filename
# import pandas as pd
# import plotly.express as px
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from flask_login import login_required

# from app.models import SalesData
# from app import db

# app = Flask(__name__)
# ALLOWED_EXTENSIONS = {'csv'}

# @app.route("/")
# def home():
#     return render_template('home.html')


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/uploadFeck', methods=['GET', 'POST'])
# def upload_fileFeck():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.instance_path, 'uploads', filename))
#             # Read the file and store in the database
#             data = pd.read_csv(os.path.join(app.instance_path, 'uploads', filename))
#             # TODO: Store data in the database
#             flash('File successfully uploaded and processed')
#             return redirect(url_for('home'))
#     return render_template('upload.html')


# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.instance_path, 'uploads', filename))
#             data = pd.read_csv(os.path.join(app.instance_path, 'uploads', filename))

#             # Insert data into the database
#             for index, row in data.iterrows():
#                 new_record = SalesData(
#                     date=row['date'],
#                     product=row['product'],
#                     quantity=row['quantity'],
#                     price=row['price'],
#                     total=row['total']
#                 )
#                 db.session.add(new_record)
#             db.session.commit()
            
#             flash('File successfully uploaded and processed')
#             return redirect(url_for('home'))
#     return render_template('upload.html')


# @app.route('/dashboard')
# @login_required
# def dashboard():
#     sales_data = SalesData.query.all()
#     df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])
    
#     bar_chart = px.bar(df, x='date', y='total', title='Monthly Sales')
#     line_chart = px.line(df, x='date', y='total', title='Sales Trends')
#     pie_chart = px.pie(df, names='product', values='total', title='Product Category Distribution')

#     return render_template('dashboard.html', bar_chart=bar_chart.to_html(full_html=False), line_chart=line_chart.to_html(full_html=False), pie_chart=pie_chart.to_html(full_html=False))

# @app.route('/performance')
# def performance():
#     sales_data = SalesData.query.all()
#     df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])
    
#     total_sales = df['total'].sum()
#     average_sales = df['total'].mean()
#     top_selling_products = df.groupby('product')['total'].sum().sort_values(ascending=False).head(10)

#     return render_template('performance.html', total_sales=total_sales, average_sales=average_sales, top_selling_products=top_selling_products.to_dict())


# @app.route('/insights')
# def insights():
#     sales_data = SalesData.query.all()
#     df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])

#     purchase_frequency = df['date'].value_counts().sort_index()
#     purchase_frequency_chart = px.bar(purchase_frequency, x=purchase_frequency.index, y=purchase_frequency.values, title='Purchase Frequency')

#     return render_template('insights.html', purchase_frequency_chart=purchase_frequency_chart.to_html(full_html=False))


# @app.route('/trends')
# def trends():
#     sales_data = SalesData.query.all()
#     df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])

#     df['date'] = pd.to_datetime(df['date'])
#     df['date_ordinal'] = df['date'].apply(lambda x: x.toordinal())

#     X = df[['date_ordinal']]
#     y = df['total']

#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     predictions = model.predict(X_test)

#     trend_chart = px.scatter(x=X_test['date_ordinal'], y=y_test, title='Sales Trends')
#     trend_chart.add_scatter(x=X_test['date_ordinal'], y=predictions, mode='lines', name='Trend Prediction')

#     return render_template('trends.html', trend_chart=trend_chart.to_html(full_html=False))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from flask_login import login_required

import app
from app.models import SalesData
from app import db

routes = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'csv'}

@routes.route("/")
def home():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @routes.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.instance_path, 'uploads', filename))
#             data = pd.read_csv(os.path.join(app.instance_path, 'uploads', filename))
#             for index, row in data.iterrows():
#                 new_record = SalesData(
#                     date=row['date'],
#                     product=row['product'],
#                     quantity=row['quantity'],
#                     price=row['price'],
#                     total=row['total']
#                 )
#                 db.session.add(new_record)
#             db.session.commit()
#             flash('File successfully uploaded and processed')
#             return redirect(url_for('routes.home'))
#     return render_template('upload.html')
@routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # Check if the file is part of the request
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if a file is selected
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Validate file type
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.instance_path, 'uploads', filename)
            
            # Create upload directory if it doesn't exist
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            
            # Save file and process CSV
            file.save(file_path)
            
            try:
                data = pd.read_csv(file_path)
                
                # Validate CSV columns
                required_columns = {'date', 'product', 'quantity', 'price', 'total'}
                if not required_columns.issubset(data.columns):
                    flash('CSV file is missing required columns', 'error')
                    return redirect(request.url)
                
                # Process and save data
                for _, row in data.iterrows():
                    new_record = SalesData(
                        date=row['date'],
                        product=row['product'],
                        quantity=row['quantity'],
                        price=row['price'],
                        total=row['total']
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
    df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])
    bar_chart = px.bar(df, x='date', y='total', title='Monthly Sales')
    line_chart = px.line(df, x='date', y='total', title='Sales Trends')
    pie_chart = px.pie(df, names='product', values='total', title='Product Category Distribution')
    return render_template('dashboard.html', bar_chart=bar_chart.to_html(full_html=False), line_chart=line_chart.to_html(full_html=False), pie_chart=pie_chart.to_html(full_html=False))

@routes.route('/performance')
@login_required
def performance():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])
    total_sales = df['total'].sum()
    average_sales = df['total'].mean()
    top_selling_products = df.groupby('product')['total'].sum().sort_values(ascending=False).head(10)
    return render_template('performance.html', total_sales=total_sales, average_sales=average_sales, top_selling_products=top_selling_products.to_dict())

@routes.route('/insights')
@login_required
def insights():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])
    purchase_frequency = df['date'].value_counts().sort_index()
    purchase_frequency_chart = px.bar(purchase_frequency, x=purchase_frequency.index, y=purchase_frequency.values, title='Purchase Frequency')
    return render_template('insights.html', purchase_frequency_chart=purchase_frequency_chart.to_html(full_html=False))

@routes.route('/trends')
@login_required
def trends():
    sales_data = SalesData.query.all()
    df = pd.DataFrame([(d.date, d.product, d.quantity, d.price, d.total) for d in sales_data], columns=['date', 'product', 'quantity', 'price', 'total'])
    df['date'] = pd.to_datetime(df['date'])
    df['date_ordinal'] = df['date'].apply(lambda x: x.toordinal())
    X = df[['date_ordinal']]
    y = df['total']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    trend_chart = px.scatter(x=X_test['date_ordinal'], y=y_test, title='Sales Trends')
    trend_chart.add_scatter(x=X_test['date_ordinal'], y=predictions, mode='lines', name='Trend Prediction')
    return render_template('trends.html', trend_chart=trend_chart.to_html(full_html=False))

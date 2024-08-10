from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, User, Product, SkinCondition
from config import Config
from tensorflow.keras.models import load_model
import tensorflow as tf
from PIL import Image
import numpy as np
from load_data import get_recommendations
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Set up login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load the model once during startup
MODEL_PATH = r'C:\Users\cva\Desktop\ITSOLERA Projects\inception_resnet_v2.keras'
try:
    model = load_model(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None

# Optional: Configure TensorFlow to use only the necessary GPU memory
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError as e:
        logger.error(f"GPU memory configuration error: {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image, target_size):
    image = image.resize(target_size)
    image = np.array(image) / 255.0  # Normalize to [0,1]
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

def analyze_image(file_path):
    if model is None:
        logger.error("Model not loaded. Cannot analyze image.")
        return None
    
    try:
        image = Image.open(file_path)
        preprocessed_image = preprocess_image(image, target_size=(224, 224))
        prediction = model.predict(preprocessed_image)
        predicted_class = np.argmax(prediction, axis=1)[0]
        return predicted_class
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return None

def get_condition_and_recommendations(predicted_class):
    condition_map = {0: 'Acne', 1: 'Eczema', 2: 'Rosacea', 3: 'Carcinoma', 4: 'Keratosis', 5: 'Milia'}
    condition = condition_map.get(predicted_class, 'Unknown Condition')
    recommendations = get_recommendations(condition)
    return condition, recommendations

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            predicted_class = analyze_image(file_path)
            if predicted_class is not None:
                condition, recommendations = get_condition_and_recommendations(predicted_class)
                return render_template('home.html', skin_condition=condition, recommendations=recommendations)
            else:
                flash('Error analyzing image. Please try again.')
        else:
            flash('File type not allowed')
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
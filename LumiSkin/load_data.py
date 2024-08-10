# load_data.py
import pandas as pd
from models import db, SkinCondition, Product, product_ingredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(csv_file, app):
    with app.app_context():
        logger.info(f"Attempting to read file from: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file}")
            return
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {csv_file}")
            return

        # Clear existing data
        db.session.query(Product).delete()
        db.session.query(SkinCondition).delete()
        db.session.commit()

        for index, row in df.iterrows():
            condition_name = row['Skin Conditions']
            products = row['Recommendations'].split(';')

            # Create or get the skin condition
            condition = SkinCondition.query.filter_by(name=condition_name).first()
            if not condition:
                condition = SkinCondition(name=condition_name)
                db.session.add(condition)
                db.session.flush()

            for product_name in products:
                product_name = product_name.strip()
                if not product_name:
                    continue

                # Create or get the product
                product = Product.query.filter_by(name=product_name).first()
                if not product:
                    product = Product(name=product_name, condition_id=condition.id)
                    db.session.add(product)
        
        try:
            db.session.commit()
            logger.info("Data loaded successfully")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error occurred while loading data: {str(e)}")

def get_recommendations(condition_name):
    condition = SkinCondition.query.filter_by(name=condition_name).first()
    if condition:
        products = Product.query.filter_by(condition_id=condition.id).all()
        return [product.name for product in products]
    return []


if __name__ == "__main__":
    from app import app  # Import here only when running as a script
    csv_file = r'C:\Users\cva\Desktop\ITSOLERA Projects\skin_care_products_list.csv'
    load_data(csv_file, app)
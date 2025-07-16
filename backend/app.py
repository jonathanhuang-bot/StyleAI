from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from body_scanner import BodyScanner, BodyType
from recommendation_engine import generate_outfit_recommendations, UserPreferences, StylePreference, BudgetRange, Occasion
from product_search import ProductSearcher
# from ebay_integration import EbaySearcher  # Removed - replaced with RapidAPI

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Enable CORS so React can communicate with Flask
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
body_scanner = BodyScanner()
product_searcher = ProductSearcher()
# ebay_searcher = EbaySearcher()  # Removed - replaced with RapidAPI

@app.route('/api/hello', methods=['GET'])
def hello():
    """Test endpoint to verify Flask is working"""
    return jsonify({
        'message': 'Flask API is running!',
        'status': 'success'
    })

@app.route('/api/upload', methods=['POST'])
def upload_photos():
    """Handle photo upload and body analysis from React frontend"""
    try:
        # Check if files were sent
        if 'files' not in request.files:
            return jsonify({
                'error': 'No files provided',
                'status': 'error'
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({
                'error': 'No files selected',
                'status': 'error'
            }), 400
        
        uploaded_files = []
        analysis_results = []
        
        # Save and analyze each file
        for file in files:
            if file and file.filename:
                # Save file to uploads folder
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                uploaded_files.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath)
                })
                
                # Analyze the photo for body measurements
                analysis = body_scanner.analyze_body_shape_from_photo(filepath)
                analysis['filename'] = filename
                
                # Convert enums to strings for JSON serialization
                if analysis['success']:
                    if analysis['body_shape']:
                        analysis['body_shape'] = analysis['body_shape'].value
                    if analysis['landmarks'] and hasattr(analysis['landmarks'], 'angle'):
                        analysis['landmarks'] = {
                            'angle': analysis['landmarks'].angle.value,
                            'confidence': analysis['landmarks'].confidence,
                            'image_width': analysis['landmarks'].image_width,
                            'image_height': analysis['landmarks'].image_height
                        }
                
                analysis_results.append(analysis)
        
        # Get user preferences from form data (with defaults)
        try:
            preferences = UserPreferences(
                favorite_colors=request.form.get('favorite_colors', 'blue,black,white').split(','),
                style_preference=StylePreference(request.form.get('style_preference', 'casual')),
                budget_range=BudgetRange(request.form.get('budget_range', 'mid')),
                occasion=Occasion(request.form.get('occasion', 'everyday'))
            )
        except (ValueError, KeyError):
            # Use defaults if preferences are invalid
            preferences = UserPreferences(
                favorite_colors=['blue', 'black', 'white'],
                style_preference=StylePreference.CASUAL,
                budget_range=BudgetRange.MID,
                occasion=Occasion.EVERYDAY
            )
        
        # Generate recommendations for successfully analyzed photos
        recommendations = []
        for analysis in analysis_results:
            if analysis['success']:
                # Convert string back to BodyType enum for recommendation engine
                try:
                    body_type_enum = BodyType(analysis['body_shape'])
                    recommendation = generate_outfit_recommendations(
                        body_type_enum, 
                        preferences
                    )
                    recommendation['filename'] = analysis['filename']
                    
                    # Search for real products using RapidAPI
                    if 'outfit' in recommendation:
                        user_prefs_dict = {
                            'favorite_colors': ','.join(preferences.favorite_colors) if isinstance(preferences.favorite_colors, list) else preferences.favorite_colors,
                            'budget_range': preferences.budget_range.value
                        }
                        
                        try:
                            outfit_products = product_searcher.search_complete_outfit(
                                recommendation['outfit'], 
                                user_prefs_dict
                            )
                            recommendation['products'] = outfit_products
                            print(f"Found products for {len(outfit_products)} outfit items")
                        except Exception as e:
                            print(f"Product search error: {e}")
                            recommendation['products'] = {}
                    
                    recommendations.append(recommendation)
                except ValueError:
                    # Handle invalid body shape
                    recommendations.append({
                        'filename': analysis['filename'],
                        'error': f"Invalid body shape: {analysis['body_shape']}"
                    })
        
        return jsonify({
            'message': f'Successfully uploaded and analyzed {len(uploaded_files)} files',
            'files': uploaded_files,
            'analysis': analysis_results,
            'recommendations': recommendations,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"ERROR in upload_photos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
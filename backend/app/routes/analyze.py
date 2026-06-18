import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..services.analysis_service import AnalysisService

analyze_bp = Blueprint('analyze', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
        
    file = request.files['resume']
    jd_text = request.form.get('jd_text', '')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not jd_text.strip():
        return jsonify({'error': 'Job description is required'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Delegate entirely to the service layer
            result = AnalysisService.run_analysis(file_path, filename, jd_text)
            
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)

            return jsonify(result)

        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format'}), 400

@analyze_bp.route('/analyze/improve', methods=['POST'])
def analyze_improve():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
        
    file = request.files['resume']
    jd_text = request.form.get('jd_text', '')
    parent_id = request.form.get('parent_id')

    if not parent_id:
        return jsonify({'error': 'Parent analysis ID is required for improvement tracking'}), 400

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not jd_text.strip():
        return jsonify({'error': 'Job description is required'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Delegate entirely to the service layer, passing parent_id
            result = AnalysisService.run_analysis(file_path, filename, jd_text, parent_id=parent_id)
            
            # Since this is an improvement, compute the delta if possible
            from ..models.analysis import Analysis
            from ..extensions import db
            parent = db.session.get(Analysis, parent_id)
            delta = None
            
            if parent:
                parent_scores = parent.scores_json
                new_scores = result['scores']
                
                delta = {
                    'overall': round(new_scores['overall'] - parent_scores.get('overall', 0), 1),
                    'skill_match': round(new_scores['skill_match'] - parent_scores.get('skill_match', 0), 1),
                    'ats_compatibility': round(new_scores['ats_compatibility'] - parent_scores.get('ats_compatibility', 0), 1),
                    'quality': round(new_scores['quality'] - parent_scores.get('quality', 0), 1),
                }
                
                # Skills gained/lost
                old_skills = {s['name'].lower() for s in parent.skills_json.get('found', [])}
                new_skills = {s['name'].lower() for s in result['skills']['found']}
                
                delta['skills_gained'] = list(new_skills - old_skills)
                delta['skills_lost'] = list(old_skills - new_skills)
                delta['improved'] = bool(delta['overall'] > 0)
                
            result['delta'] = delta

            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)

            return jsonify(result)

        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format'}), 400

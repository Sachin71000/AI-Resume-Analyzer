from flask import Blueprint, request, jsonify
from ..models.analysis import Analysis

compare_bp = Blueprint('compare', __name__)

@compare_bp.route('/compare', methods=['POST'])
def compare_analyses():
    data = request.json
    ids = data.get('analysis_ids', [])
    
    if not ids or len(ids) < 2 or len(ids) > 5:
        return jsonify({'error': 'Must provide between 2 and 5 analysis IDs'}), 400
        
    analyses = Analysis.query.filter(Analysis.id.in_(ids)).order_by(Analysis.created_at.asc()).all()
    
    if len(analyses) != len(ids):
        return jsonify({'error': 'One or more analysis IDs not found'}), 404
        
    # Sort them in chronological order implicitly by having them fetched that way
    analyses_data = [a.to_full() for a in analyses]
    
    # Compute comparison between first and last in the list for deltas
    first = analyses_data[0]
    last = analyses_data[-1]
    
    score_deltas = {
        'overall': round(last['scores']['overall'] - first['scores']['overall'], 1),
        'skill_match': round(last['scores']['skill_match'] - first['scores']['skill_match'], 1),
        'ats_compatibility': round(last['scores']['ats_compatibility'] - first['scores']['ats_compatibility'], 1),
        'quality': round(last['scores']['quality'] - first['scores']['quality'], 1)
    }
    
    first_skills_names = {s['name'].lower() for s in first['skills']['found']}
    last_skills_names = {s['name'].lower() for s in last['skills']['found']}
    
    skills_gained = list(last_skills_names - first_skills_names)
    skills_lost = list(first_skills_names - last_skills_names)
    
    # Capitalize for display
    skills_gained = [s.title() for s in skills_gained]
    skills_lost = [s.title() for s in skills_lost]
    
    comparison = {
        'score_deltas': score_deltas,
        'skills_gained': skills_gained,
        'skills_lost': skills_lost,
        'improved': score_deltas['overall'] > 0
    }
    
    return jsonify({
        'analyses': analyses_data,
        'comparison': comparison
    })

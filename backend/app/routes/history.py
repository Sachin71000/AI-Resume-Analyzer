from flask import Blueprint, request, jsonify
from ..models.analysis import Analysis
from ..extensions import db

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def get_history():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    sort_by = request.args.get('sort', 'date')
    search = request.args.get('search', '').lower()

    query = Analysis.query

    if search:
        query = query.filter(Analysis.resume_filename.ilike(f'%{search}%') | Analysis.label.ilike(f'%{search}%'))

    if sort_by == 'score':
        query = query.order_by(Analysis.overall_score.desc())
    else:
        query = query.order_by(Analysis.created_at.desc())

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    items = [item.to_summary() for item in pagination.items]
    
    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })

@history_bp.route('/analysis/<id>', methods=['GET'])
def get_analysis(id):
    analysis = Analysis.query.get_or_404(id)
    return jsonify(analysis.to_full())

@history_bp.route('/analysis/<id>', methods=['DELETE'])
def delete_analysis(id):
    analysis = Analysis.query.get_or_404(id)
    db.session.delete(analysis)
    db.session.commit()
    return jsonify({'success': True})

@history_bp.route('/analyses', methods=['DELETE'])
def bulk_delete_analyses():
    data = request.json
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': 'No ids provided'}), 400
    
    Analysis.query.filter(Analysis.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True, 'deleted': len(ids)})

@history_bp.route('/analysis/<id>/label', methods=['PATCH'])
def update_label(id):
    analysis = Analysis.query.get_or_404(id)
    data = request.json
    if 'label' in data:
        analysis.label = data['label']
        db.session.commit()
    return jsonify({'success': True})

import os
from flask import Blueprint, send_file, jsonify
from ..models.analysis import Analysis
from ..services.export_service import ExportService

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/<id>', methods=['GET'])
def export_pdf(id):
    analysis = Analysis.query.get_or_404(id)
    
    try:
        pdf_path = ExportService.generate_pdf(analysis)
        
        # We can send the file as an attachment
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"analysis_{analysis.resume_filename}_{analysis.id[:8]}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500

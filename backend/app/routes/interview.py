import logging
from flask import Blueprint, request, jsonify
from ..services.interview_service import InterviewService

logger = logging.getLogger(__name__)
interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/interview/start', methods=['POST'])
def start_interview():
    """Starts a new mock interview session."""
    data = request.get_json() or {}
    analysis_id = data.get('analysis_id')
    difficulty = data.get('difficulty', 'medium')
    question_count = data.get('question_count', 10)
    include_types = data.get('question_types', ["skill", "project", "behavioral", "role"])
    target_role = data.get('target_role')

    if not analysis_id:
        return jsonify({"error": "Missing required field: analysis_id"}), 400

    try:
        res = InterviewService.start_interview_session(
            analysis_id=analysis_id,
            difficulty=difficulty,
            question_count=int(question_count),
            include_types=include_types,
            target_role=target_role
        )
        return jsonify(res), 200
    except ValueError as ve:
        logger.error(f"Value error in start_interview: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.error(f"Error in start_interview: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while starting the session."}), 500

@interview_bp.route('/interview/<session_id>/answer', methods=['POST'])
def submit_answer(session_id):
    """Submits answer for current question and gets next question."""
    data = request.get_json() or {}
    user_answer = data.get('answer', '')
    time_taken = data.get('time_taken_seconds')

    # Guard for missing/empty
    if not session_id:
        return jsonify({"error": "Missing session ID"}), 400

    try:
        res = InterviewService.submit_question_answer(
            session_id=session_id,
            user_answer=user_answer,
            time_taken_seconds=time_taken
        )
        return jsonify(res), 200
    except ValueError as ve:
        logger.error(f"Value error in submit_answer: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.error(f"Error in submit_answer: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while recording your answer."}), 500

@interview_bp.route('/interview/<session_id>/complete', methods=['POST'])
def complete_interview(session_id):
    """Marks session completed, performs batch grading, and returns report."""
    if not session_id:
        return jsonify({"error": "Missing session ID"}), 400

    try:
        res = InterviewService.evaluate_completed_session(session_id)
        return jsonify(res), 200
    except ValueError as ve:
        logger.error(f"Value error in complete_interview: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.error(f"Error in complete_interview: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during batch answer evaluation."}), 500

@interview_bp.route('/interview/<session_id>/results', methods=['GET'])
def get_results(session_id):
    """Fetches evaluation report and answers for a completed session."""
    if not session_id:
        return jsonify({"error": "Missing session ID"}), 400

    try:
        res = InterviewService.get_session_results(session_id)
        return jsonify(res), 200
    except ValueError as ve:
        logger.error(f"Value error in get_results: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.error(f"Error in get_results: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while fetching results."}), 500

@interview_bp.route('/interview/history', methods=['GET'])
def get_history():
    """Lists historical mock interviews."""
    analysis_id = request.args.get('analysis_id')
    try:
        res = InterviewService.get_interview_history(analysis_id)
        return jsonify({"items": res, "total": len(res)}), 200
    except Exception as e:
        logger.error(f"Error in get_history: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while fetching history."}), 500

@interview_bp.route('/interview/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Deletes an interview session."""
    if not session_id:
        return jsonify({"error": "Missing session ID"}), 400

    try:
        success = InterviewService.delete_interview_session(session_id)
        if success:
            return jsonify({"success": True, "message": "Session deleted successfully."}), 200
        return jsonify({"error": "Session not found."}), 404
    except Exception as e:
        logger.error(f"Error in delete_session: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while deleting the session."}), 500

"""REST API"""

from typing import Dict, Any
from datetime import date, datetime
import json
from flask import Flask, jsonify, request


def create_app(analytics_service=None):
    """Создание Flask приложения"""
    app = Flask(__name__)
    
    @app.route('/api/analytics/revenue', methods=['GET'])
    def get_revenue():
        """Получить общую выручку"""
        if analytics_service is None:
            return jsonify({'error': 'Analytics service not available'}), 503
        
        bookings = request.args.get('bookings')
        if bookings:
            try:
                bookings = json.loads(bookings)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid bookings data'}), 400
        else:
            bookings = []
        
        result = analytics_service.get_total_revenue(bookings)
        return jsonify({'total_revenue': result})
    
    @app.route('/api/analytics/cancellation-rate', methods=['GET'])
    def get_cancellation_rate():
        """Получить процент отмен"""
        if analytics_service is None:
            return jsonify({'error': 'Analytics service not available'}), 503
        
        bookings = request.args.get('bookings')
        if bookings:
            try:
                bookings = json.loads(bookings)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid bookings data'}), 400
        else:
            bookings = []
        
        result = analytics_service.get_cancellation_rate(bookings)
        return jsonify({'cancellation_rate': result})
    
    @app.route('/api/analytics/occupancy', methods=['GET'])
    def get_occupancy():
        """Получить загрузку отеля"""
        if analytics_service is None:
            return jsonify({'error': 'Analytics service not available'}), 503
        
        total_rooms = request.args.get('total_rooms', 0, type=int)
        booked_rooms = request.args.get('booked_rooms', 0, type=int)
        
        result = analytics_service.get_occupancy_rate(total_rooms, booked_rooms)
        return jsonify({'occupancy_rate': result})
    
    @app.route('/api/analytics/full-report', methods=['GET'])
    def get_full_report():
        """Получить полный отчет"""
        if analytics_service is None:
            return jsonify({'error': 'Analytics service not available'}), 503
        
        bookings = request.args.get('bookings')
        if bookings:
            try:
                bookings = json.loads(bookings)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid bookings data'}), 400
        else:
            bookings = []
        
        result = analytics_service.get_full_analytics_report(bookings)
        return jsonify(result)
    
    @app.route('/api/analytics/anomalies', methods=['GET'])
    def get_anomalies():
        """Получить аномалии"""
        if analytics_service is None:
            return jsonify({'error': 'Analytics service not available'}), 503
        
        bookings = request.args.get('bookings')
        if bookings:
            try:
                bookings = json.loads(bookings)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid bookings data'}), 400
        else:
            bookings = []
        
        result = analytics_service.detect_anomalies(bookings)
        return jsonify({'anomalies': result})
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Проверка здоровья сервиса"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    return app
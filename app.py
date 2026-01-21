from flask import Flask, render_template, jsonify, request
import scraper
import logic
from datetime import datetime

app = Flask(__name__)

# In-memory storage for results (in a real app, use a DB)
# Structure: {'date': 'YYYY-MM-DD', 'type': 'baloto'|'miloto', 'numbers': [1,2,3,4,5], 'super': 6 (optional)}
stored_results = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-results', methods=['POST'])
def fetch_results():
    global stored_results
    try:
        # Fetch fresh data
        baloto_data = scraper.get_baloto_results()
        miloto_data = scraper.get_miloto_results()
        
        # Merge with existing (avoiding duplicates based on date+type would be better, but simple append for now)
        # Simplified: Just replace or extend. Let's extend and deduplicate in logic if needed.
        # For this version, we'll assume we fetch the "latest" set.
        
        new_results = baloto_data + miloto_data
        stored_results.extend([r for r in new_results if r not in stored_results])
        
        return jsonify({'status': 'success', 'message': f'Fetched {len(new_results)} new results.', 'count': len(stored_results)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/generate-miloto', methods=['GET'])
def generate_miloto():
    # Filter for MiLoto
    miloto_history = [r for r in stored_results if r['type'] == 'miloto']
    if not miloto_history:
        return jsonify({'status': 'error', 'message': 'No data found. Fetch info first.'}), 400
    
    prediction = logic.generate_miloto_prediction(miloto_history)
    return jsonify({'status': 'success', 'prediction': prediction})

@app.route('/api/generate-baloto', methods=['GET'])
def generate_baloto():
    # Filter for Baloto
    baloto_history = [r for r in stored_results if r['type'] == 'baloto']
    if not baloto_history:
        return jsonify({'status': 'error', 'message': 'No data found. Fetch info first.'}), 400
    
    prediction = logic.generate_baloto_prediction(baloto_history)
    return jsonify({'status': 'success', 'prediction': prediction})

@app.route('/api/add-manual', methods=['POST'])
def add_manual():
    data = request.json
    # Expect: {date, type, numbers (list), super (optional)}
    try:
        new_entry = {
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'type': data['type'],
            'numbers': data['numbers'],
            'super': data.get('super_balota')
        }
        stored_results.append(new_entry)
        return jsonify({'status': 'success', 'message': 'Entry added manually.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Return raw stats for frontend visualization
    return jsonify({
        'baloto': logic.calculate_frequencies([r for r in stored_results if r['type'] == 'baloto']),
        'miloto': logic.calculate_frequencies([r for r in stored_results if r['type'] == 'miloto'])
    })


# ============================================
# PREDICTIVE ANALYTICS ENDPOINTS
# ============================================

@app.route('/api/predictive/<game_type>', methods=['GET'])
def get_predictive_data(game_type):
    """
    Returns comprehensive predictive analytics data for charts.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({
            'status': 'error',
            'message': f'No data found for {game_type}. Please fetch data first.'
        }), 400
    
    data = logic.get_comprehensive_prediction_data(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/predictive/<game_type>/hot-cold', methods=['GET'])
def get_hot_cold(game_type):
    """
    Returns hot and cold numbers analysis.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({'status': 'error', 'message': 'No data found'}), 400
    
    data = logic.calculate_hot_cold_numbers(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/predictive/<game_type>/gaps', methods=['GET'])
def get_gaps(game_type):
    """
    Returns number gaps (overdue numbers) analysis.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({'status': 'error', 'message': 'No data found'}), 400
    
    data = logic.calculate_number_gaps(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/predictive/<game_type>/trends', methods=['GET'])
def get_trends(game_type):
    """
    Returns trend analysis data.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({'status': 'error', 'message': 'No data found'}), 400
    
    data = logic.calculate_trend_analysis(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/predictive/<game_type>/pairs', methods=['GET'])
def get_pairs(game_type):
    """
    Returns pair frequency analysis.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({'status': 'error', 'message': 'No data found'}), 400
    
    data = logic.calculate_pair_frequency(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/predictive/<game_type>/sum-distribution', methods=['GET'])
def get_sum_distribution(game_type):
    """
    Returns sum distribution analysis.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({'status': 'error', 'message': 'No data found'}), 400
    
    data = logic.calculate_sum_distribution(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/predictive/<game_type>/positions', methods=['GET'])
def get_positions(game_type):
    """
    Returns position analysis data.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    
    if not history:
        return jsonify({'status': 'error', 'message': 'No data found'}), 400
    
    data = logic.calculate_position_analysis(history, game_type)
    return jsonify({'status': 'success', 'data': data})


@app.route('/api/history/<game_type>', methods=['GET'])
def get_history(game_type):
    """
    Returns historical draw data for a game type.
    """
    if game_type not in ['baloto', 'miloto']:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400
    
    history = [r for r in stored_results if r['type'] == game_type]
    sorted_history = sorted(history, key=lambda x: x.get('date', ''), reverse=True)
    
    return jsonify({
        'status': 'success',
        'data': sorted_history,
        'count': len(sorted_history)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.2')

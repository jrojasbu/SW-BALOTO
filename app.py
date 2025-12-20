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

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.2')

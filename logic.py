import random
from collections import Counter
from datetime import datetime, timedelta
import math

def calculate_frequencies(history):
    """
    Calculates the frequency of each number in the history.
    """
    if not history:
        return {'numbers': {}, 'super': {}}
    
    all_numbers = []
    all_supers = []
    
    for draw in history:
        all_numbers.extend(draw['numbers'])
        if 'super' in draw and draw['super'] is not None:
            all_supers.append(draw['super'])
            
    num_freq = dict(Counter(all_numbers))
    super_freq = dict(Counter(all_supers))
    
    return {'numbers': num_freq, 'super': super_freq}

def weighted_choice(frequencies, k, pool_range):
    """
    Selects k unique numbers from pool_range, weighted by their frequency.
    If a number is not in frequencies, it gets a base weight (e.g., 1).
    """
    population = list(pool_range)
    # Default weight 1, add frequency count to it
    weights = [frequencies.get(num, 0) + 1 for num in population]
    
    # random.choices allows replacement, we need unique. 
    # Logic: Pick one, remove from pool, re-normalize weights? 
    # Simpler: Shuffle population based on weights? 
    # Or just use numpy choice if available, but let's stick to pure python.
    
    selected = set()
    while len(selected) < k:
        # Normalize weights for current selection
        current_pop = [x for x in population if x not in selected]
        current_weights = [frequencies.get(num, 0) + 1 for x in current_pop for num in [x]] # inefficient but safe
        
        if not current_pop:
            break
            
        pick = random.choices(current_pop, weights=current_weights, k=1)[0]
        selected.add(pick)
        
    return sorted(list(selected))

def generate_miloto_prediction(history):
    freqs = calculate_frequencies(history)
    # MiLoto: 5 numbers from 1 to 39
    # "5 MAS FRECUENTES" implied user wants highly frequent ones.
    # We use weighted random to make it "ALEATORIAMENTE... MAS FRECUENTES"
    
    prediction = weighted_choice(freqs['numbers'], 5, range(1, 40))
    return {'numbers': prediction}

def generate_baloto_prediction(history):
    freqs = calculate_frequencies(history)
    # Baloto: 5 numbers (1-43) + 1 Super (1-16)
    
    numbers = weighted_choice(freqs['numbers'], 5, range(1, 44))
    
    # Super balota
    # Weighted choice for 1 item
    super_weights = [freqs['super'].get(x, 0) + 1 for x in range(1, 17)]
    super_balota = random.choices(range(1, 17), weights=super_weights, k=1)[0]
    
    return {'numbers': numbers, 'super_balota': super_balota}


# ============================================
# PREDICTIVE ANALYTICS FUNCTIONS
# ============================================

def get_time_series_data(history, game_type):
    """
    Extracts time series data for trend analysis.
    Returns data organized by date with frequency counts.
    """
    if not history:
        return {'dates': [], 'frequencies': {}}
    
    # Sort by date
    sorted_history = sorted(history, key=lambda x: x.get('date', ''))
    
    # Group by date and calculate cumulative frequencies
    dates = []
    cumulative_freq = {}
    running_total = Counter()
    
    for draw in sorted_history:
        date = draw.get('date', '')
        if date:
            dates.append(date)
            for num in draw['numbers']:
                running_total[num] += 1
            # Store snapshot of frequencies at this point
            cumulative_freq[date] = dict(running_total)
    
    return {'dates': dates, 'frequencies': cumulative_freq}


def calculate_hot_cold_numbers(history, game_type):
    """
    Identifies hot (frequently appearing) and cold (rarely appearing) numbers.
    """
    if not history:
        return {'hot': [], 'cold': [], 'neutral': []}
    
    max_num = 43 if game_type == 'baloto' else 39
    freqs = calculate_frequencies(history)
    num_freq = freqs['numbers']
    
    # Calculate average frequency
    total_draws = len(history)
    expected_freq = (total_draws * 5) / max_num  # 5 numbers per draw
    
    hot = []
    cold = []
    neutral = []
    
    for num in range(1, max_num + 1):
        freq = num_freq.get(num, 0)
        deviation = freq - expected_freq
        
        if deviation > expected_freq * 0.3:  # 30% above average
            hot.append({'number': num, 'frequency': freq, 'deviation': round(deviation, 2)})
        elif deviation < -expected_freq * 0.3:  # 30% below average
            cold.append({'number': num, 'frequency': freq, 'deviation': round(deviation, 2)})
        else:
            neutral.append({'number': num, 'frequency': freq, 'deviation': round(deviation, 2)})
    
    # Sort by frequency
    hot.sort(key=lambda x: x['frequency'], reverse=True)
    cold.sort(key=lambda x: x['frequency'])
    
    return {'hot': hot[:10], 'cold': cold[:10], 'neutral': neutral}


def calculate_number_gaps(history, game_type):
    """
    Calculates the gap (draws since last appearance) for each number.
    Useful for identifying overdue numbers.
    """
    if not history:
        return []
    
    max_num = 43 if game_type == 'baloto' else 39
    sorted_history = sorted(history, key=lambda x: x.get('date', ''), reverse=True)
    
    gaps = {}
    for num in range(1, max_num + 1):
        gaps[num] = {'number': num, 'gap': len(sorted_history), 'last_seen': None}
    
    for idx, draw in enumerate(sorted_history):
        for num in draw['numbers']:
            if gaps[num]['last_seen'] is None:
                gaps[num]['gap'] = idx
                gaps[num]['last_seen'] = draw.get('date', 'Unknown')
    
    result = list(gaps.values())
    result.sort(key=lambda x: x['gap'], reverse=True)
    
    return result


def calculate_pair_frequency(history, game_type):
    """
    Analyzes which number pairs appear together most frequently.
    """
    if not history:
        return []
    
    pair_counter = Counter()
    
    for draw in history:
        numbers = sorted(draw['numbers'])
        # Generate all pairs
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                pair = (numbers[i], numbers[j])
                pair_counter[pair] += 1
    
    # Get top 20 pairs
    top_pairs = pair_counter.most_common(20)
    
    return [{'pair': list(pair), 'frequency': freq} for pair, freq in top_pairs]


def calculate_sum_distribution(history, game_type):
    """
    Analyzes the distribution of sum totals for all draws.
    Helps identify typical sum ranges.
    """
    if not history:
        return {'distribution': [], 'average': 0, 'min': 0, 'max': 0, 'ranges': []}
    
    sums = [sum(draw['numbers']) for draw in history]
    
    # Create distribution buckets
    min_sum = min(sums)
    max_sum = max(sums)
    avg_sum = sum(sums) / len(sums)
    
    # Create 10 buckets
    bucket_size = max(1, (max_sum - min_sum) // 10)
    distribution = Counter()
    
    for s in sums:
        bucket = ((s - min_sum) // bucket_size) * bucket_size + min_sum
        distribution[bucket] += 1
    
    dist_list = [{'range_start': k, 'range_end': k + bucket_size, 'count': v}
                 for k, v in sorted(distribution.items())]
    
    # Calculate recommended ranges (middle 60% of distribution)
    sorted_sums = sorted(sums)
    lower_idx = int(len(sorted_sums) * 0.2)
    upper_idx = int(len(sorted_sums) * 0.8)
    
    return {
        'distribution': dist_list,
        'average': round(avg_sum, 2),
        'min': min_sum,
        'max': max_sum,
        'recommended_range': {
            'low': sorted_sums[lower_idx],
            'high': sorted_sums[upper_idx]
        }
    }


def calculate_trend_analysis(history, game_type):
    """
    Performs trend analysis on number frequencies over time.
    Identifies numbers with increasing or decreasing trends.
    """
    if len(history) < 5:
        return {'trending_up': [], 'trending_down': [], 'stable': []}
    
    max_num = 43 if game_type == 'baloto' else 39
    sorted_history = sorted(history, key=lambda x: x.get('date', ''))
    
    # Split into two halves for comparison
    mid = len(sorted_history) // 2
    first_half = sorted_history[:mid]
    second_half = sorted_history[mid:]
    
    first_freq = Counter()
    second_freq = Counter()
    
    for draw in first_half:
        first_freq.update(draw['numbers'])
    
    for draw in second_half:
        second_freq.update(draw['numbers'])
    
    # Normalize by number of draws
    trending_up = []
    trending_down = []
    stable = []
    
    for num in range(1, max_num + 1):
        first_rate = first_freq.get(num, 0) / max(1, len(first_half))
        second_rate = second_freq.get(num, 0) / max(1, len(second_half))
        
        change = second_rate - first_rate
        change_pct = (change / max(0.01, first_rate)) * 100 if first_rate > 0 else 100 if second_rate > 0 else 0
        
        item = {
            'number': num,
            'first_half_freq': first_freq.get(num, 0),
            'second_half_freq': second_freq.get(num, 0),
            'change_pct': round(change_pct, 1)
        }
        
        if change_pct > 30:
            trending_up.append(item)
        elif change_pct < -30:
            trending_down.append(item)
        else:
            stable.append(item)
    
    trending_up.sort(key=lambda x: x['change_pct'], reverse=True)
    trending_down.sort(key=lambda x: x['change_pct'])
    
    return {
        'trending_up': trending_up[:10],
        'trending_down': trending_down[:10],
        'stable': stable
    }


def calculate_position_analysis(history, game_type):
    """
    Analyzes which numbers appear most frequently in each position.
    """
    if not history:
        return []
    
    position_freq = [Counter() for _ in range(5)]
    
    for draw in history:
        sorted_nums = sorted(draw['numbers'])
        for pos, num in enumerate(sorted_nums):
            position_freq[pos][num] += 1
    
    result = []
    for pos in range(5):
        top_5 = position_freq[pos].most_common(5)
        result.append({
            'position': pos + 1,
            'top_numbers': [{'number': num, 'frequency': freq} for num, freq in top_5]
        })
    
    return result


def get_super_balota_analysis(history):
    """
    Specific analysis for Super Balota (Baloto only).
    """
    if not history:
        return {'frequencies': [], 'hot': [], 'cold': [], 'gaps': []}
    
    super_freq = Counter()
    last_seen = {}
    
    for idx, draw in enumerate(sorted(history, key=lambda x: x.get('date', ''), reverse=True)):
        super_num = draw.get('super')
        if super_num is not None:
            super_freq[super_num] += 1
            if super_num not in last_seen:
                last_seen[super_num] = idx
    
    # Frequencies
    freq_list = [{'number': num, 'frequency': freq} for num, freq in sorted(super_freq.items())]
    
    # Hot and cold
    avg_freq = sum(super_freq.values()) / max(1, len(super_freq))
    hot = [{'number': num, 'frequency': freq} for num, freq in super_freq.items() if freq > avg_freq * 1.2]
    cold = [{'number': num, 'frequency': freq} for num, freq in super_freq.items() if freq < avg_freq * 0.8]
    
    # Gaps
    gaps = []
    for num in range(1, 17):
        gaps.append({
            'number': num,
            'gap': last_seen.get(num, len(history)),
            'frequency': super_freq.get(num, 0)
        })
    gaps.sort(key=lambda x: x['gap'], reverse=True)
    
    return {
        'frequencies': freq_list,
        'hot': sorted(hot, key=lambda x: x['frequency'], reverse=True),
        'cold': sorted(cold, key=lambda x: x['frequency']),
        'gaps': gaps
    }


def get_comprehensive_prediction_data(history, game_type):
    """
    Aggregates all predictive analytics for a game type.
    """
    return {
        'frequency_chart': calculate_frequencies(history),
        'hot_cold': calculate_hot_cold_numbers(history, game_type),
        'gaps': calculate_number_gaps(history, game_type),
        'pairs': calculate_pair_frequency(history, game_type),
        'sum_distribution': calculate_sum_distribution(history, game_type),
        'trends': calculate_trend_analysis(history, game_type),
        'position_analysis': calculate_position_analysis(history, game_type),
        'super_analysis': get_super_balota_analysis(history) if game_type == 'baloto' else None,
        'total_draws': len(history)
    }

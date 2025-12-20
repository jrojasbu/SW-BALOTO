import random
from collections import Counter

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

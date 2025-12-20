import scraper
import logic
import sys

def verify():
    print("Verifying Scraper...")
    try:
        baloto = scraper.get_baloto_results()
        miloto = scraper.get_miloto_results()
        print(f"Scraper OK. Got {len(baloto)} Baloto and {len(miloto)} MiLoto results.")
    except Exception as e:
        print(f"Scraper FAILED: {e}")
        return False

    print("Verifying Logic...")
    try:
        data = baloto + miloto
        # Test freq calc
        freqs = logic.calculate_frequencies([r for r in data if r['type'] == 'baloto'])
        print(f"Frequencies OK. Top number count: {len(freqs['numbers'])}")
        
        # Test Prediction
        pred_b = logic.generate_baloto_prediction([r for r in data if r['type'] == 'baloto'])
        print(f"Baloto Prediction OK: {pred_b}")
        
        pred_m = logic.generate_miloto_prediction([r for r in data if r['type'] == 'miloto'])
        print(f"MiLoto Prediction OK: {pred_m}")
        
    except Exception as e:
        print(f"Logic FAILED: {e}")
        return False
        
    print("ALL SYSTEMS GO.")
    return True

if __name__ == "__main__":
    if verify():
        sys.exit(0)
    else:
        sys.exit(1)

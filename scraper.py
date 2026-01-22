import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import re

# Target URLs
BALOTO_URL = "https://baloto.com/resultados"
MILOTO_URL = "https://baloto.com/miloto/resultados/"

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}

def parse_spanish_date(date_str):
    """
    Parses Spanish date format like '19 de Enero de 2026' to 'YYYY-MM-DD'
    """
    months = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    try:
        # Clean the date string
        date_str = date_str.lower().strip()
        
        # Extract day, month, year using regex
        match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date_str)
        if match:
            day = match.group(1).zfill(2)
            month_name = match.group(2)
            year = match.group(3)
            month = months.get(month_name, '01')
            return f"{year}-{month}-{day}"
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
    
    return datetime.now().strftime("%Y-%m-%d")

def parse_numbers_from_text(text):
    """
    Extracts numbers from a result text like '04 - 06 - 20 - 28 - 42 - 11'
    Returns (main_numbers, super_balota) where super_balota may be None
    """
    # Find all numbers in the text
    numbers = re.findall(r'\d+', text)
    numbers = [int(n) for n in numbers]
    
    if len(numbers) >= 6:
        # Baloto format: 5 main numbers + 1 super balota
        return numbers[:5], numbers[5]
    elif len(numbers) == 5:
        # MiLoto format: 5 numbers only
        return numbers, None
    else:
        return numbers, None

def is_within_last_2_months(date_str):
    """
    Checks if a date string (YYYY-MM-DD) is within the last 2 months
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        two_months_ago = datetime.now() - timedelta(days=60)
        return date >= two_months_ago
    except:
        return True  # Include if we can't parse

def get_baloto_results():
    """
    Scrapes the last 2 months of Baloto results from baloto.com/resultados
    Returns a list of dicts: {'date': str, 'type': 'baloto', 'numbers': [int], 'super': int}
    """
    results = []
    print("Fetching Baloto data from baloto.com/resultados...")
    
    try:
        response = requests.get(BALOTO_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the historical results table
        # Looking for rows in the results table
        # The structure observed: table rows with SORTEO, FECHA, RESULTADO columns
        
        # Try to find result rows - they typically contain Baloto logo and numbers
        rows = soup.find_all('tr')
        
        for row in rows:
            try:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Check if this is a Baloto or Revancha row
                    sorteo_cell = cells[0].get_text(strip=True).lower()
                    
                    # Get the date
                    date_text = cells[1].get_text(strip=True)
                    date_str = parse_spanish_date(date_text)
                    
                    # Skip if older than 2 months
                    if not is_within_last_2_months(date_str):
                        continue
                    
                    # Get the numbers
                    result_text = cells[2].get_text(strip=True)
                    main_numbers, super_balota = parse_numbers_from_text(result_text)
                    
                    if len(main_numbers) >= 5:
                        result_type = 'baloto'
                        if 'revancha' in sorteo_cell:
                            result_type = 'revancha'
                        
                        results.append({
                            'date': date_str,
                            'type': result_type,
                            'numbers': sorted(main_numbers[:5]),
                            'super': super_balota
                        })
            except Exception as e:
                continue
        
        # Also try to find results in div-based layouts
        result_divs = soup.find_all(['div', 'section'], class_=re.compile(r'result|histor', re.I))
        for div in result_divs:
            # Look for date and number patterns
            text = div.get_text()
            date_matches = re.findall(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', text, re.I)
            number_matches = re.findall(r'(\d{2}\s*-\s*\d{2}\s*-\s*\d{2}\s*-\s*\d{2}\s*-\s*\d{2}(?:\s*-\s*\d{1,2})?)', text)
            
            for date_match, num_match in zip(date_matches, number_matches):
                date_str = parse_spanish_date(date_match)
                if is_within_last_2_months(date_str):
                    main_numbers, super_balota = parse_numbers_from_text(num_match)
                    if len(main_numbers) >= 5:
                        results.append({
                            'date': date_str,
                            'type': 'baloto',
                            'numbers': sorted(main_numbers[:5]),
                            'super': super_balota
                        })
        
        if results:
            print(f"Successfully fetched {len(results)} Baloto results from the website")
            # Remove duplicates based on date and type
            seen = set()
            unique_results = []
            for r in results:
                key = (r['date'], r['type'], tuple(r['numbers']))
                if key not in seen:
                    seen.add(key)
                    unique_results.append(r)
            return unique_results
            
    except requests.RequestException as e:
        print(f"Error fetching Baloto data: {e}")
    except Exception as e:
        print(f"Error parsing Baloto data: {e}")
    
    # Fallback to simulated data if scraping fails
    print("Using simulated Baloto data (scraping failed or blocked)")
    return generate_simulated_baloto_results()

def get_miloto_results():
    """
    Scrapes the last 2 months of MiLoto results from baloto.com/miloto/resultados/
    Returns a list of dicts: {'date': str, 'type': 'miloto', 'numbers': [int]}
    """
    results = []
    print("Fetching MiLoto data from baloto.com/miloto/resultados/...")
    
    try:
        response = requests.get(MILOTO_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the historical results table
        # MiLoto structure: FECHA, RESULTADO columns
        rows = soup.find_all('tr')
        
        for row in rows:
            try:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # Get the date
                    date_text = cells[0].get_text(strip=True)
                    date_str = parse_spanish_date(date_text)
                    
                    # Skip if older than 2 months
                    if not is_within_last_2_months(date_str):
                        continue
                    
                    # Get the numbers (MiLoto has no super balota)
                    result_text = cells[1].get_text(strip=True)
                    main_numbers, _ = parse_numbers_from_text(result_text)
                    
                    if len(main_numbers) >= 5:
                        results.append({
                            'date': date_str,
                            'type': 'miloto',
                            'numbers': sorted(main_numbers[:5])
                        })
            except Exception as e:
                continue
        
        # Also try to find results in div-based layouts
        result_divs = soup.find_all(['div', 'section'], class_=re.compile(r'result|histor', re.I))
        for div in result_divs:
            text = div.get_text()
            date_matches = re.findall(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', text, re.I)
            number_matches = re.findall(r'(\d{2}\s*-\s*\d{2}\s*-\s*\d{2}\s*-\s*\d{2}\s*-\s*\d{2})', text)
            
            for date_match, num_match in zip(date_matches, number_matches):
                date_str = parse_spanish_date(date_match)
                if is_within_last_2_months(date_str):
                    main_numbers, _ = parse_numbers_from_text(num_match)
                    if len(main_numbers) >= 5:
                        results.append({
                            'date': date_str,
                            'type': 'miloto',
                            'numbers': sorted(main_numbers[:5])
                        })
        
        if results:
            print(f"Successfully fetched {len(results)} MiLoto results from the website")
            # Remove duplicates
            seen = set()
            unique_results = []
            for r in results:
                key = (r['date'], tuple(r['numbers']))
                if key not in seen:
                    seen.add(key)
                    unique_results.append(r)
            return unique_results
            
    except requests.RequestException as e:
        print(f"Error fetching MiLoto data: {e}")
    except Exception as e:
        print(f"Error parsing MiLoto data: {e}")
    
    # Fallback to simulated data if scraping fails
    print("Using simulated MiLoto data (scraping failed or blocked)")
    return generate_simulated_miloto_results()

def generate_dates_last_2_months(draws_per_week=2):
    """
    Generates a list of dates for the last 2 months.
    Returns dates in descending order (most recent first).
    """
    today = datetime.now()
    two_months_ago = today - timedelta(days=60)
    
    dates = []
    current_date = today
    
    days_between_draws = 7 // draws_per_week
    
    while current_date >= two_months_ago:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date -= timedelta(days=days_between_draws)
    
    return dates

def generate_simulated_baloto_results():
    """
    Generates simulated Baloto results for the last 2 months.
    Used as fallback when scraping fails.
    """
    results = []
    dates = generate_dates_last_2_months(draws_per_week=2)
    
    for date in dates:
        # Baloto draw
        results.append({
            'date': date,
            'type': 'baloto',
            'numbers': sorted(random.sample(range(1, 44), 5)),
            'super': random.randint(1, 16)
        })
        # Revancha draw (same date)
        results.append({
            'date': date,
            'type': 'revancha',
            'numbers': sorted(random.sample(range(1, 44), 5)),
            'super': random.randint(1, 16)
        })
    
    return results

def generate_simulated_miloto_results():
    """
    Generates simulated MiLoto results for the last 2 months.
    Used as fallback when scraping fails.
    """
    results = []
    dates = generate_dates_last_2_months(draws_per_week=4)
    
    for date in dates:
        results.append({
            'date': date,
            'type': 'miloto',
            'numbers': sorted(random.sample(range(1, 40), 5))
        })
    
    return results

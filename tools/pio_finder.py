import os, json
from serpapi.google_search import GoogleSearch
from pathlib import Path
from runtime.database import get_db_conn
from datetime import datetime, UTC

WORKDIR = Path.cwd() / 'runtime'


def find_pio(department, city):
    conn = get_db_conn()
    cur = conn.cursor()
    key = (str(department) + '|' + str(city)).lower()
    cur.execute('SELECT pio_address, source_url, confidence_score FROM pio_cache WHERE key = ?', (key,))
    row = cur.fetchone()
    if row:
        return {'pio_address': row[0], 'source_url': row[1], 'confidence_score': row[2]}

    query = f'"Public Information Officer" AND RTI AND {department} AND {city} site:gov.in'
    params = {'q': query, 'api_key': os.getenv('SERPAPI_KEY'), 'num': '10'}
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get('organic_results', [])
        for r in organic:
            title = r.get('title','').lower()
            snippet = r.get('snippet','').lower()
            link = r.get('link')
            if 'public information officer' in title or 'public information officer' in snippet:
                pio_address = snippet
                cur.execute('REPLACE INTO pio_cache (key, department, city, pio_address, source_url, confidence_score, last_verified) VALUES (?,?,?,?,?,?,?)',
                            (key, department, city, pio_address, link, 0.9, datetime.now(UTC).isoformat()))
                conn.commit()
                return {'pio_address': pio_address, 'source_url': link, 'confidence_score': 0.9}
        if organic:
            top = organic[0]
            pio_address = top.get('snippet','')
            link = top.get('link')
            cur.execute('REPLACE INTO pio_cache (key, department, city, pio_address, source_url, confidence_score, last_verified) VALUES (?,?,?,?,?,?,?)',
                        (key, department, city, pio_address, link, 0.6, datetime.now(UTC).isoformat()))
            conn.commit()
            return {'pio_address': pio_address, 'source_url': link, 'confidence_score': 0.6}
    except Exception as e:
        pio_address = f'PIO, {department}, {city} (please verify)'
        cur.execute('REPLACE INTO pio_cache (key, department, city, pio_address, source_url, confidence_score, last_verified) VALUES (?,?,?,?,?,?,?)',
                    (key, department, city, pio_address, None, 0.3, datetime.now(UTC).isoformat()))
        conn.commit()
        raise e 

   
    pio_address = f'PIO, {department}, {city} (no search result, please verify)'
    cur.execute('REPLACE INTO pio_cache (key, department, city, pio_address, source_url, confidence_score, last_verified) VALUES (?,?,?,?,?,?,?)',
                (key, department, city, pio_address, None, 0.1, datetime.now(UTC).isoformat()))
    conn.commit()
    return {'pio_address': pio_address, 'source_url': None, 'confidence_score': 0.1}
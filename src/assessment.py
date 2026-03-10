import json
import os
from .scoring import calculate_dimension_score, calculate_total_score, get_readiness_level, get_detailed_recommendations

def load_questions(file_path='data/questions.json'):
    """Loads questions from the JSON file."""
    if not os.path.exists(file_path):
        # Fallback if called from different directory
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, 'questions.json') # Try different path if needed, but standard should work
        if not os.path.exists(file_path):
             file_path = 'data/questions.json'
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_assessment_v2(user_answers, lang="it", sector="General"):
    """
    Core function to calculate AI Readiness results.
    user_answers: dict {dimension_id: [scores]}
    lang: 'it' or 'en'
    sector: Industry sector for benchmarking and risk multipliers
    """
    data = load_questions()
    results = {
        'dimensions': {},
        'total_score': 0,
        'level': "",
        'recommendation': "",
        'detailed_recommendations': []
    }
    
    dimension_scores = []
    
    dimension_scores = []
    
    for dim in data['dimensions']:
        dim_id = dim['id']
        answers = user_answers.get(dim_id, [])
        
        # New: Check for Governance special scoring
        if dim_id == 'governance':
            from .scoring import calculate_governance_score_specific
            score = calculate_governance_score_specific(answers, dim, sector=sector)
        else:
            score = calculate_dimension_score(answers, dim)
            
        # Choose correct language for dimension name and description
        dim_name = dim.get('name_en', dim['name']) if lang == 'en' else dim['name']
        dim_desc = dim.get('description_en', dim.get('description', '')) if lang == 'en' else dim.get('description', '')
        
        results['dimensions'][dim_id] = {
            'name': dim_name,
            'score': score,
            'weight': dim['weight'],
            'description': dim_desc
        }
        dimension_scores.append((score, dim['weight']))
        
    results['total_score'] = calculate_total_score(dimension_scores)
    # Ensure lang is passed down
    results['level'], results['recommendation'] = get_readiness_level(results['total_score'], lang=lang)
    results['detailed_recommendations'] = get_detailed_recommendations(results, lang=lang)
    
    return results

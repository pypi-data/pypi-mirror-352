from .analyzer import AiGraphCodeScanAnalyzer
from .issues_data import issues_data

analyzers = {
    'aigraphcodescan':
        {
            'name': 'aigraphcodescan',
            'title': 'aigraphcodescan',
            'class': AiGraphCodeScanAnalyzer,
            'language': 'all',
            'issues_data': issues_data,
        },
}

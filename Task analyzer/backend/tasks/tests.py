from django.test import TestCase
from .scoring import calculate_scores, detect_cycle

class ScoringTests(TestCase):
    def test_overdue_task_has_high_score(self):
        tasks = [
            {'id': 1, 'title': 'Overdue task', 'due_date': '2020-01-01', 'estimated_hours': 2, 'importance': 5, 'dependencies': []},
            {'id': 2, 'title': 'Future task', 'due_date': '2099-01-01', 'estimated_hours': 2, 'importance': 5, 'dependencies': []}
        ]
        scored = calculate_scores(tasks)
        self.assertGreater(scored[0]['score'], scored[1]['score'])

    def test_quick_win_prioritized_in_fastest_strategy(self):
        tasks = [
            {'id': 1, 'title': 'Long task', 'due_date': None, 'estimated_hours': 20, 'importance': 6, 'dependencies': []},
            {'id': 2, 'title': 'Short task', 'due_date': None, 'estimated_hours': 0.5, 'importance': 5, 'dependencies': []}
        ]
        scored = calculate_scores(tasks, strategy='fastest')
        self.assertEqual(scored[0]['title'], 'Short task')

    def test_detect_cycle(self):
        tasks = [
            {'id': 1, 'title': 'A', 'dependencies': [2]},
            {'id': 2, 'title': 'B', 'dependencies': [3]},
            {'id': 3, 'title': 'C', 'dependencies': [1]},
        ]
        has_cycle, cycles = detect_cycle(tasks)
        self.assertTrue(has_cycle)
        self.assertTrue(len(cycles) >= 1)

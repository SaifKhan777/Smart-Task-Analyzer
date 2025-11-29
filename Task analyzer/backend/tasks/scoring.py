"""
scoring.py
Contains the scoring logic for tasks including:
- urgency scoring
- importance normalization
- effort scoring (quick wins)
- dependency scoring
- cycle detection
- strategy handling and configurable weights
"""

from datetime import date, timedelta
from collections import defaultdict, deque

DEFAULT_WEIGHTS = {
    'urgency': 0.40,
    'importance': 0.30,
    'effort': 0.20,
    'dependency': 0.10
}

def sanitize_weights(weights):
    if not weights:
        return DEFAULT_WEIGHTS.copy()
    # only accept known keys, and normalize so they sum to 1
    w = {k: float(weights.get(k, 0)) for k in DEFAULT_WEIGHTS.keys()}
    total = sum(w.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {k: v/total for k, v in w.items()}

def detect_cycle(tasks):
    """
    Detect cycle in dependencies.
    tasks: list of task dicts {id: int, dependencies: [ids]}
    Returns: (has_cycle: bool, cycles: list of lists)
    """
    graph = defaultdict(list)
    ids = set()
    for t in tasks:
        tid = t.get('id')
        ids.add(tid)
        for d in t.get('dependencies', []):
            graph[tid].append(d)

    visited = {}
    cycles = []

    def dfs(node, stack):
        visited[node] = 1  # visiting
        stack.append(node)
        for neigh in graph.get(node, []):
            if neigh not in visited:
                if dfs(neigh, stack):
                    return True
            elif visited.get(neigh) == 1:
                # found a cycle; record it
                idx = stack.index(neigh) if neigh in stack else 0
                cycles.append(stack[idx:] + [neigh])
                return True
        visited[node] = 2  # visited
        stack.pop()
        return False

    for node in ids:
        if node not in visited:
            if dfs(node, []):
                return True, cycles
    return False, cycles

def calculate_scores(tasks, weights=None, strategy='smart'):
    """
    tasks: list of dicts, each with keys:
      id (int) - optional but recommended for dependencies
      title
      due_date (date or ISO string or None)
      estimated_hours (number)
      importance (1-10)
      dependencies (list of ids)

    returns list of tasks with extra fields: score (0-100), breakdown, reason
    """
    w = sanitize_weights(weights)
    # allow strategies to override weights
    if strategy == 'fastest':
        w = {'urgency': 0.10, 'importance': 0.10, 'effort': 0.70, 'dependency': 0.10}
    elif strategy == 'impact':
        w = {'urgency': 0.10, 'importance': 0.70, 'effort': 0.10, 'dependency': 0.10}
    elif strategy == 'deadline':
        w = {'urgency': 0.80, 'importance': 0.10, 'effort': 0.05, 'dependency': 0.05}
    # else 'smart' uses provided or default

    # Normalize/prepare fields
    today = date.today()
    # build map of id to task for dependency counts
    id_to_task = {}
    for idx, t in enumerate(tasks):
        tid = t.get('id', idx+1)  # ensure id exists
        t['id'] = tid
        id_to_task[tid] = t

    # compute how many tasks each task blocks (i.e., dependents count)
    blocked_count = {tid: 0 for tid in id_to_task}
    for t in tasks:
        for dep_id in t.get('dependencies', []):
            # if dep exists, then this dep blocks this task => dep is a blocker of another task
            if dep_id in blocked_count:
                blocked_count[dep_id] += 1

    scored = []
    for t in tasks:
        # parse and normalize
        due = t.get('due_date')
        if isinstance(due, str):
            try:
                year, month, day = map(int, due.split('-'))
                due = date(year, month, day)
            except Exception:
                due = None
        est = t.get('estimated_hours', 1.0)
        try:
            est = float(est)
            if est < 0:
                est = abs(est)
        except Exception:
            est = 1.0
        importance = t.get('importance', 5)
        try:
            importance = int(importance)
        except Exception:
            importance = 5
        importance = max(1, min(10, importance))

        # URGENCY: map to 0-100
        if due is None:
            # no due date -> moderate urgency
            urgency_score = 30.0
        else:
            days_left = (due - today).days
            if days_left < 0:
                # overdue -> very high urgency; more overdue -> even higher
                # cap at 100
                urgency_score = min(100.0, 90.0 + min(10, -days_left))
            else:
                # scale: due today -> 90, in 1 day -> 80, in 7 days -> ~30, far -> ~0
                if days_left <= 1:
                    urgency_score = 90.0
                else:
                    # decaying function
                    urgency_score = max(0.0, 90.0 - (days_left * 6.0))
        # IMPORTANCE: map 1-10 -> 0-100
        importance_score = (importance - 1) / 9.0 * 100.0

        # EFFORT: small effort -> higher score (quick wins)
        # Use a softcap: tasks <=1h -> 90, <=4h -> 70, <=8h -> 50, bigger -> lower
        if est <= 1:
            effort_score = 90.0
        elif est <= 4:
            effort_score = 70.0
        elif est <= 8:
            effort_score = 50.0
        else:
            # longer tasks get lower quick-win score; but never zero
            effort_score = max(5.0, 35.0 - (est - 8) * 2.0)

        # DEPENDENCY: tasks that block more tasks -> higher priority
        dep_score = min(100.0, blocked_count.get(t['id'], 0) * 20.0)  # each blocked neighbor adds 20 capped at 100

        # Weighted sum
        score = (
            urgency_score * w['urgency'] +
            importance_score * w['importance'] +
            effort_score * w['effort'] +
            dep_score * w['dependency']
        )

        # assemble reason / breakdown
        breakdown = {
            'urgency_score': round(urgency_score, 2),
            'importance_score': round(importance_score, 2),
            'effort_score': round(effort_score, 2),
            'dependency_score': round(dep_score, 2),
            'weights': w
        }

        # simple human-readable reason
        reasons = []
        if due is None:
            reasons.append("No due date — moderate urgency")
        else:
            days_left = (due - today).days
            if days_left < 0:
                reasons.append(f"Overdue by {-days_left} day(s)")
            elif days_left == 0:
                reasons.append("Due today")
            else:
                reasons.append(f"Due in {days_left} day(s)")

        if importance >= 8:
            reasons.append("High importance")
        elif importance <= 3:
            reasons.append("Low importance")

        if est <= 1:
            reasons.append("Quick win (low effort)")
        elif est > 8:
            reasons.append("High effort")

        if blocked_count.get(t['id'], 0) > 0:
            reasons.append(f"Blocks {blocked_count[t['id']]} task(s)")

        scored.append({
            **t,
            'score': round(score, 2),
            'breakdown': breakdown,
            'reason': '; '.join(reasons) if reasons else 'Balanced factors'
        })

    # sort descending by score
    scored_sorted = sorted(scored, key=lambda x: x['score'], reverse=True)
    return scored_sorted

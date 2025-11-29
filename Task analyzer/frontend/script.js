// Simple frontend that keeps tasks in memory and calls backend analyze endpoint
const taskListEl = document.getElementById('task-list');
const taskListEmpty = document.getElementById('task-list-empty');
const tasks = []; // local list of tasks with assigned ids
let nextId = 1;

function renderTaskList() {
  taskListEl.innerHTML = '';
  if (tasks.length === 0) {
    taskListEmpty.style.display = 'block';
    return;
  }
  taskListEmpty.style.display = 'none';
  tasks.forEach(t => {
    const li = document.createElement('li');
    li.innerHTML = `<strong>${t.title}</strong> <div class="task-meta">Due: ${t.due_date || '—'} | Est: ${t.estimated_hours}h | Importance: ${t.importance} | Deps: ${t.dependencies && t.dependencies.length ? t.dependencies.join(',') : '—'}</div>`;
    taskListEl.appendChild(li);
  });
}

document.getElementById('add-task').addEventListener('click', () => {
  const title = document.getElementById('title').value.trim();
  const due_date = document.getElementById('due_date').value || null;
  const estimated_hours = parseFloat(document.getElementById('estimated_hours').value) || 1;
  const importance = parseInt(document.getElementById('importance').value) || 5;
  const depsRaw = document.getElementById('dependencies').value.trim();
  const dependencies = depsRaw ? depsRaw.split(',').map(s => parseInt(s.trim())).filter(Boolean) : [];
  if (!title) {
    alert('Title is required');
    return;
  }
  const t = {
    id: nextId++,
    title, due_date, estimated_hours, importance, dependencies
  };
  tasks.push(t);
  renderTaskList();
  // reset simple fields
  document.getElementById('title').value = '';
  document.getElementById('dependencies').value = '';
});

// Bulk JSON paste
document.getElementById('bulk-json').addEventListener('paste', (ev) => {
  // do nothing special, user will click Analyze to import
});

document.getElementById('analyze').addEventListener('click', async () => {
  const bulk = document.getElementById('bulk-json').value.trim();
  let payloadTasks = [];
  if (bulk) {
    try {
      const parsed = JSON.parse(bulk);
      if (!Array.isArray(parsed)) throw new Error('JSON must be an array');
      // attach ids if missing
      parsed.forEach(t => {
        if (!t.id) t.id = nextId++;
        payloadTasks.push(t);
      });
    } catch (e) {
      alert('Invalid JSON: ' + e.message);
      return;
    }
  }
  // include in-memory tasks
  payloadTasks = payloadTasks.concat(tasks);

  if (payloadTasks.length === 0) {
    alert('Add tasks or paste JSON first.');
    return;
  }

  const strategy = document.getElementById('strategy').value;

  const payload = { tasks: payloadTasks, strategy };

  // show loading
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = '<div class="muted">Analyzing...</div>';

  try {
    const res = await fetch('/api/tasks/analyze/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (!res.ok) {
      resultsDiv.innerHTML = `<div class="muted">Error: ${JSON.stringify(json)}</div>`;
      return;
    }
    renderResults(json.tasks);
    // also fetch suggestions
    const sres = await fetch('/api/tasks/suggest/?n=3');
    const sjson = await sres.json();
    if (sres.ok) {
      renderSuggestions(sjson.suggestions);
    }
  } catch (err) {
    resultsDiv.innerHTML = `<div class="muted">Network error: ${err.message}</div>`;
  }
});

function renderResults(list) {
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = '';
  list.forEach(t => {
    const card = document.createElement('div');
    card.className = 'result-card ' + priorityClass(t.score);
    card.innerHTML = `<div style="display:flex;justify-content:space-between"><strong>${t.title}</strong><div>Score: ${t.score}</div></div>
      <div class="task-meta">Due: ${t.due_date || '—'} | Est: ${t.estimated_hours}h | Importance: ${t.importance}</div>
      <div style="margin-top:8px"><em>${t.reason}</em></div>
      <details style="margin-top:8px"><summary>Breakdown</summary><pre>${JSON.stringify(t.breakdown, null, 2)}</pre></details>`;
    resultsDiv.appendChild(card);
  });
}

function renderSuggestions(suggestions) {
  const sdiv = document.getElementById('suggestions');
  sdiv.innerHTML = '';
  suggestions.forEach(s => {
    const el = document.createElement('div');
    el.className = 'result-card ' + priorityClass(s.score);
    el.innerHTML = `<strong>${s.title}</strong> — Score: ${s.score}<div class="task-meta">${s.why}</div>`;
    sdiv.appendChild(el);
  });
}

function priorityClass(score) {
  if (score >= 70) return 'priority-high';
  if (score >= 40) return 'priority-med';
  return 'priority-low';
}

renderTaskList();

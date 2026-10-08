// Live progress for the cache dashboard: polls while a background job is active.
(() => {
  const dashboard = document.getElementById('cacheDashboard');
  if (!dashboard) return;

  const POLL_MS = 4000;
  const cards = dashboard.querySelectorAll('[data-cache-job]');

  const doneKey = {entities: 'processed', vocabulary: 'successful'};

  const updateCard = (card, job) => {
    const key = card.dataset.cacheJob;
    const done = job[doneKey[key]];
    const values = {...job, done, state: card.dataset.stateLabels
      ? JSON.parse(card.dataset.stateLabels)[job.state] : job.state};
    card.querySelectorAll('[data-job-field]').forEach((element) => {
      const value = values[element.dataset.jobField];
      element.textContent = value === '' || value === undefined ? '—' : value;
    });
    const progress = card.querySelector('[data-job-progress]');
    progress.max = job.total || 1;
    progress.value = done;
    card.dataset.jobActive = ['queued', 'running'].includes(job.state);
  };

  const poll = async () => {
    try {
      const response = await fetch(dashboard.dataset.statusUrl);
      if (!response.ok) throw new Error(response.status);
      const status = await response.json();
      cards.forEach((card) => updateCard(card, status[card.dataset.cacheJob]));
    } catch (error) {
      console.warn('Cache status unavailable', error);
    }
    schedule();
  };

  const schedule = () => {
    const active = [...cards].some((card) => card.dataset.jobActive === 'true');
    if (active) setTimeout(poll, POLL_MS);
  };

  schedule();
})();

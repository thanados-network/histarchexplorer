/**
 * Histarchexplorer - Modern About Page Controller
 * Handles animated KPI counters, team role/search filtering, and interactive entity detail modals.
 */

(() => {
  /**
   * Extract the localized display label from a ConfigEntity localized dictionary.
   */
  function bestLabel(obj) {
    if (!obj) return '';
    if (obj.display && typeof obj.display.label === 'string') {
      return obj.display.label;
    }
    for (const val of Object.values(obj)) {
      if (typeof val === 'string' && val.trim()) {
        return val;
      }
    }
    return '';
  }

  /**
   * Compute up to two uppercase initials from a name string.
   */
  function getInitials(name) {
    const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return '?';
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  }

  /**
   * Animate a single numeric counter element from 0 to its data-target value.
   */
  function animateCounter(counter) {
    if (counter.dataset.animated === 'true') return;
    counter.dataset.animated = 'true';

    const target = Number(counter.dataset.target || 0);
    if (!target || Number.isNaN(target)) {
      counter.textContent = '0';
      return;
    }

    const duration = 750;
    const steps = 40;
    const increment = target / steps;
    let current = 0;

    const tick = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(tick);
      }
      counter.textContent = Math.floor(current).toLocaleString();
    }, duration / steps);
  }

  /**
   * Initialize KPI counter animations using IntersectionObserver.
   */
  function setupCounters() {
    const counters = document.querySelectorAll('.vcounter-number');
    if (!counters.length) return;

    if ('IntersectionObserver' in window) {
      const scrollRoot = document.querySelector('.page-wrapper');
      const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            obs.unobserve(entry.target);
          }
        });
      }, {
        root: scrollRoot || null,
        threshold: 0.15
      });

      counters.forEach(counter => observer.observe(counter));
    } else {
      counters.forEach(counter => animateCounter(counter));
    }
  }

  /**
   * Setup interactive role filter pills and quick search for team members.
   */
  function setupTeamFilter() {
    const roleButtons = document.querySelectorAll('.team-role-filter-btn');
    const searchInput = document.getElementById('teamSearchInput');
    const teamCols = document.querySelectorAll('.about-team-col');
    const emptyState = document.getElementById('teamFilterEmpty');

    if (!teamCols.length) return;

    let activeRole = 'all';
    let searchQuery = '';

    const applyFilter = () => {
      let visibleCount = 0;
      teamCols.forEach(col => {
        const rolesRaw = col.getAttribute('data-roles') || '';
        const rolesList = rolesRaw.split('|').filter(Boolean);
        const searchText = (col.getAttribute('data-search') || '').toLowerCase();

        const matchesRole = activeRole === 'all' || rolesList.includes(activeRole);
        const matchesSearch = !searchQuery || searchText.includes(searchQuery);
        const isVisible = matchesRole && matchesSearch;

        col.classList.toggle('d-none', !isVisible);
        if (isVisible) visibleCount += 1;
      });

      if (emptyState) {
        emptyState.classList.toggle('d-none', visibleCount > 0);
      }
    };

    roleButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        roleButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeRole = btn.getAttribute('data-role') || 'all';
        applyFilter();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        searchQuery = searchInput.value.trim().toLowerCase();
        applyFilter();
      });
    }
  }

  /**
   * Build a metadata row item for the entity modal.
   */
  function createMetaItem(iconClass, labelText, valueNode) {
    const col = document.createElement('div');
    col.className = 'col-sm-6';

    const card = document.createElement('div');
    card.className = 'p-3 rounded-3 bg-body-tertiary h-100 d-flex align-items-start gap-3';

    const iconWrap = document.createElement('div');
    iconWrap.className = 'text-primary fs-5 lh-1 mt-1';
    const icon = document.createElement('i');
    icon.className = `bi ${iconClass}`;
    iconWrap.appendChild(icon);

    const contentWrap = document.createElement('div');
    contentWrap.className = 'overflow-hidden';

    const labelDiv = document.createElement('div');
    labelDiv.className = 'text-muted small fw-semibold text-uppercase tracking-wider mb-1';
    labelDiv.textContent = labelText;

    contentWrap.appendChild(labelDiv);
    contentWrap.appendChild(valueNode);

    card.appendChild(iconWrap);
    card.appendChild(contentWrap);
    col.appendChild(card);
    return col;
  }

  /**
   * Populate and render the shared #entityModal for a given entity ID.
   */
  function renderEntityModal(entityId, elements, i18n) {
    const entityData = window.ENTITY_DATA || {};
    const projectSlugs = window.PROJECT_SLUGS || {};
    const entity = entityData[entityId];
    if (!entity) return;

    const name = bestLabel(entity.name);
    elements.label.textContent = name;

    if (elements.badge) {
      const badgeText = entity.acronym || String(entity.class_name || '').replace('-', ' ');
      elements.badge.textContent = badgeText;
      elements.badge.classList.toggle('d-none', !badgeText);
    }

    // Render avatar or logo
    elements.image.textContent = '';
    if (entity.image) {
      const img = document.createElement('img');
      img.src = entity.image;
      img.alt = name;
      img.className = entity.class_name === 'person'
        ? 'about-modal-avatar rounded-circle shadow-sm'
        : 'about-modal-logo img-fluid';
      elements.image.appendChild(img);
    } else if (entity.class_name === 'person') {
      const placeholder = document.createElement('div');
      placeholder.className = 'about-avatar-placeholder about-avatar-placeholder--lg mx-auto shadow-sm';
      placeholder.textContent = getInitials(name);
      elements.image.appendChild(placeholder);
    }

    // Description
    const desc = entity.description?.display?.label || '';
    elements.description.innerHTML = desc;
    elements.description.classList.toggle('d-none', !desc);

    // Metadata cards (Website, Email, ORCID, Address)
    elements.meta.textContent = '';
    const metaFragment = document.createDocumentFragment();
    let hasMeta = false;

    if (entity.website) {
      hasMeta = true;
      const link = document.createElement('a');
      link.href = entity.website;
      link.target = '_blank';
      link.rel = 'noopener';
      link.className = 'text-decoration-none fw-medium text-break d-inline-flex align-items-center gap-1';
      link.textContent = entity.website;
      const extIcon = document.createElement('i');
      extIcon.className = 'bi bi-box-arrow-up-right small';
      link.appendChild(extIcon);
      metaFragment.appendChild(createMetaItem('bi-globe2', i18n.website, link));
    }

    if (entity.email) {
      hasMeta = true;
      const mailLink = document.createElement('a');
      mailLink.href = `mailto:${entity.email}`;
      mailLink.className = 'text-decoration-none fw-medium text-break';
      mailLink.textContent = entity.email;
      metaFragment.appendChild(createMetaItem('bi-envelope', i18n.email, mailLink));
    }

    if (entity.orcid_id) {
      hasMeta = true;
      const cleanOrcid = entity.orcid_id.trim().replace(/\s/g, '');
      const orcidLink = document.createElement('a');
      orcidLink.href = `https://orcid.org/${cleanOrcid}`;
      orcidLink.target = '_blank';
      orcidLink.rel = 'noopener';
      orcidLink.className = 'text-decoration-none fw-medium d-inline-flex align-items-center gap-1';
      orcidLink.textContent = cleanOrcid;
      const extIcon = document.createElement('i');
      extIcon.className = 'bi bi-box-arrow-up-right small';
      orcidLink.appendChild(extIcon);
      metaFragment.appendChild(createMetaItem('bi-person-badge', i18n.orcid, orcidLink));
    }

    const addressLabel = entity.address?.display?.label || '';
    if (addressLabel) {
      hasMeta = true;
      const addrSpan = document.createElement('div');
      addrSpan.className = 'small text-body';
      addrSpan.innerHTML = addressLabel.replace(/\n/g, '<br>');
      metaFragment.appendChild(createMetaItem('bi-geo-alt', i18n.address, addrSpan));
    }

    if (hasMeta) {
      const row = document.createElement('div');
      row.className = 'row g-3 mb-3';
      row.appendChild(metaFragment);
      elements.meta.appendChild(row);
    }

    // Relations / Affiliations list
    elements.links.textContent = '';
    if (Array.isArray(entity.links) && entity.links.length > 0) {
      const divider = document.createElement('hr');
      divider.className = 'my-3 opacity-25';
      elements.links.appendChild(divider);

      const heading = document.createElement('h6');
      heading.className = 'fw-bold text-uppercase small text-muted tracking-wider mb-3';
      heading.textContent = i18n.relations;
      elements.links.appendChild(heading);

      const listGroup = document.createElement('div');
      listGroup.className = 'd-flex flex-column gap-2';

      entity.links.forEach(link => {
        const roleLabel = link.role?.display?.label || '';
        const propLabel = link.config_property?.display?.label || '';
        const endName = bestLabel(link.end_name);
        const targetId = link.end_id;
        const targetEntity = entityData[targetId];

        const itemRow = document.createElement('div');
        itemRow.className =
          'p-2 px-3 rounded-3 border bg-body-tertiary d-flex flex-wrap ' +
          'justify-content-between align-items-center gap-2';

        const leftCol = document.createElement('div');
        leftCol.className = 'd-flex align-items-center gap-2';

        const icon = document.createElement('i');
        if (targetEntity?.class_name === 'person') {
          icon.className = 'bi bi-person text-primary';
        } else if (targetEntity?.class_name === 'institution') {
          icon.className = 'bi bi-building text-primary';
        } else {
          icon.className = 'bi bi-diagram-3 text-primary';
        }
        leftCol.appendChild(icon);

        if (targetId in projectSlugs) {
          const slug = projectSlugs[targetId];
          const projLink = document.createElement('a');
          projLink.href = slug ? `/about/${slug}` : '/about';
          projLink.className = 'fw-semibold text-body text-decoration-none about-modal-entity-link';
          projLink.textContent = endName;
          leftCol.appendChild(projLink);
        } else if (targetEntity) {
          const switchBtn = document.createElement('button');
          switchBtn.type = 'button';
          switchBtn.className =
            'btn btn-link p-0 fw-semibold text-body text-decoration-none text-start about-modal-entity-link';
          switchBtn.textContent = endName;
          switchBtn.addEventListener('click', () => {
            renderEntityModal(targetId, elements, i18n);
          });
          leftCol.appendChild(switchBtn);
        } else {
          const nameSpan = document.createElement('span');
          nameSpan.className = 'fw-semibold text-body';
          nameSpan.textContent = endName;
          leftCol.appendChild(nameSpan);
        }

        itemRow.appendChild(leftCol);

        const badgeLabel = roleLabel || propLabel;
        if (badgeLabel) {
          const roleBadge = document.createElement('span');
          roleBadge.className = 'badge bg-primary-subtle text-primary rounded-pill';
          roleBadge.textContent = badgeLabel;
          itemRow.appendChild(roleBadge);
        }

        listGroup.appendChild(itemRow);
      });

      elements.links.appendChild(listGroup);
    }
  }

  /**
   * Setup click listeners for all elements opening #entityModal.
   */
  function setupEntityModal() {
    const modalEl = document.getElementById('entityModal');
    if (!modalEl) return;

    const elements = {
      label: document.getElementById('entityModalLabel'),
      badge: document.getElementById('entityModalBadge'),
      image: document.getElementById('entityModalImage'),
      description: document.getElementById('entityModalDescription'),
      meta: document.getElementById('entityModalMeta'),
      links: document.getElementById('entityModalLinks')
    };

    if (!elements.label || !elements.image || !elements.description || !elements.meta || !elements.links) {
      return;
    }

    const i18n = {
      website: modalEl.getAttribute('data-label-website') || 'Website',
      email: modalEl.getAttribute('data-label-email') || 'Email',
      orcid: modalEl.getAttribute('data-label-orcid') || 'ORCID',
      address: modalEl.getAttribute('data-label-address') || 'Address',
      relations: modalEl.getAttribute('data-label-relations') || 'Relations'
    };

    document.querySelectorAll("[data-bs-target='#entityModal']").forEach(trigger => {
      trigger.addEventListener('click', () => {
        const id = trigger.getAttribute('data-id');
        if (id) {
          renderEntityModal(id, elements, i18n);
        }
      });
    });
  }

  function initAboutPage() {
    setupCounters();
    setupTeamFilter();
    setupEntityModal();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAboutPage);
  } else {
    initAboutPage();
  }
})();

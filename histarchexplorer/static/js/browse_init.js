(function () {
    const configScripts = document.querySelectorAll(
        'script.browse-tab-config[type="application/json"]:not([data-initialized])');
    configScripts.forEach(configEl => {
        configEl.setAttribute('data-initialized', 'true');

        let cfg = {};
        try {
            cfg = JSON.parse(configEl.textContent || '{}');
        } catch (_e) {
            return;
        }

        const tabName = cfg.tabName || '';
        if (cfg.subunits) {
            window.typeTreeData = cfg.typeTreeData || {};
            window.viewClasses = cfg.viewClasses || {};
            window.data = cfg.subunitData || {entities: []};
            window.getEntitiesForTab = function () {
                const validClasses = [
                    'place', 'feature', 'stratigraphic_unit',
                    'artifact', 'human_remains'];
                return (window.data.entities || []).filter(
                    entity => validClasses.includes(entity.class));
            };

            (window.data.entities || []).forEach(entity => {
                entity.beginDBP = calculateTimeBP(entity.begin);
                entity.endDBP = calculateTimeBP(entity.end);
                if (entity.begin) {
                    entity.beginString = makeLocalDate(entity.begin).localdate;
                }
                if (entity.end) {
                    entity.endString = makeLocalDate(entity.end).localdate;
                }
                entity.all = [
                    entity.description, entity.class, entity.type, entity.name]
                    .filter(v => v !== null && v !== undefined && v !== '')
                    .map(v => String(v).replace(/[\r\n]+/g, ' '))
                    .join(' ');
            });
        }

        const predefinedFilters = cfg.predefinedFilters;
        const menu = document.getElementById(`${tabName}-presets-menu`);
        if (!menu || !Array.isArray(predefinedFilters) ||
            predefinedFilters.length === 0) {
            return;
        }
        const dropdown = document.getElementById(`${tabName}-presets-dropdown`);
        if (dropdown) dropdown.classList.remove('d-none');

        const badge = document.getElementById(`${tabName}-preset-badge`);
        const badgeLabel = document.getElementById(
            `${tabName}-preset-badge-label`);
        const badgeClose = document.getElementById(
            `${tabName}-preset-badge-close`);

        function showBadge(label) {
            badgeLabel.textContent = label;
            badge.classList.remove('d-none', 'opacity-50');
            badge.classList.add('d-inline-flex', 'btn-outline-secondary');
        }

        function markBadgeModified() {
            if (badge.classList.contains('d-none')) return;
            badge.classList.add('opacity-50');
        }

        function hideBadge() {
            badge.classList.add('d-none');
            badge.classList.remove(
                'd-inline-flex', 'btn-outline-secondary', 'opacity-50');
        }

        window.hideBadgeFns = window.hideBadgeFns || {};
        window.hideBadgeFns[tabName] = hideBadge;
        window.showBadgeFns = window.showBadgeFns || {};
        window.showBadgeFns[tabName] = showBadge;

        function applyPresetSelection(preset) {
            if (!preset) return;
            const tabsInPreset = (
                Array.isArray(preset.tabs) && preset.tabs.length > 0)
                ? preset.tabs
                : tabsToLoad;

            tabsToLoad.forEach(tab => {
                const isVisible = tabsInPreset.includes(tab);
                document.querySelectorAll(`.to-remove-${tab}`).forEach(el => {
                    el.classList.toggle('d-none', !isVisible);
                });
            });

            const fns = window.applyPresetFns || {};
            tabsInPreset.forEach(tab => {
                if (typeof fns[tab] === 'function') fns[tab](preset);
            });

            const activeLink = document.querySelector(
                '#nav-sidebar .nav-link.active');
            const activeTab = activeLink
                ? activeLink.id.replace(/^tab-/, '')
                : null;
            if (activeTab && !tabsInPreset.includes(activeTab)) {
                const firstLink = document.getElementById(
                    `tab-${tabsInPreset[0]}`);
                if (firstLink) firstLink.click();
            }

            const showFns = window.showBadgeFns || {};
            Object.values(showFns).forEach(fn => fn(preset.label));
        }

        window.activatePresetById = function (presetId) {
            const preset = predefinedFilters.find(
                p => String(p.id) === String(presetId));
            if (preset) applyPresetSelection(preset);
        };

        window.resetAllToInitial = function resetAllToInitial() {
            tabsToLoad.forEach(tab => {
                document.querySelectorAll(`.to-remove-${tab}`).forEach(el => {
                    el.classList.remove('d-none');
                });
            });
            const fns = window.resetFilterFns || {};
            tabsToLoad.forEach(tab => {
                if (typeof fns[tab] === 'function') fns[tab]();
            });
            const hideFns = window.hideBadgeFns || {};
            Object.values(hideFns).forEach(fn => fn());
        };

        if (badgeClose) {
            badgeClose.addEventListener('click', window.resetAllToInitial);
        }

        document.addEventListener(
            `${tabName}-filter-changed`, markBadgeModified);

        predefinedFilters.forEach(preset => {
            const li = document.createElement('li');
            const btn = document.createElement('button');
            btn.className = 'dropdown-item d-flex align-items-center gap-2';
            btn.type = 'button';
            btn.title = preset.description || '';

            if (preset.icon && preset.icon.type === 'css') {
                const icon = document.createElement('i');
                icon.className = preset.icon.value.includes('bi ')
                    ? preset.icon.value : `bi ${preset.icon.value}`;
                btn.appendChild(icon);
            } else if (preset.icon && preset.icon.type === 'img') {
                const img = document.createElement('img');
                img.src = `/static/images/icons/${preset.icon.value}`;
                img.alt = '';
                img.classList.add('preset-icon');
                btn.appendChild(img);
            }

            const label = document.createElement('span');
            label.textContent = preset.label;
            btn.appendChild(label);

            btn.addEventListener('click', () => {
                applyPresetSelection(preset);
            });

            li.appendChild(btn);
            menu.appendChild(li);
        });
    });
})();

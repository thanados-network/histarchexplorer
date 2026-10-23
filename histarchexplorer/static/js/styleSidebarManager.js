/**
 * StyleSidebarManager.js
 * Manages the style sidebar functionality for map layers in different tabs.
 * Refactored from inline template scripts to a reusable class.
 */

if (typeof StyleSidebarManager === 'undefined') {
    class StyleSidebarManager {
        constructor(tabName, map, data, classList) {
            this.tabName = tabName;
            this.map = map;
            this.data = data;
            this.classList = classList;

            this.hiddenLayerTypes = new Set();
            this.hiddenTypes = new Set();
            this.hiddenClasses = new Set();

            this.multiCurrentLayerType = null;

            this.defaultStyles = {
                Polygon: { fillColor: '#008888', outlineColor: '#004747', outlineWidth: 1.5, opacity: 0.5 },
                LineString: { color: '#008888', lineWidth: 2.5, opacity: 1 },
                Point: { color: '#008888', radius: 7, strokeColor: '#ffffff', strokeWidth: 1.5 }
            };

            this.currentStyles = JSON.parse(JSON.stringify(this.defaultStyles));
            this.multiSharedOpts = JSON.parse(JSON.stringify(this.defaultStyles));

            this.multiTypeColors = { Point: {}, Polygon: {}, LineString: {} };
            this.multiClassColors = { Point: {}, Polygon: {}, LineString: {} };

            this.layerDefs = [
                {
                    type: 'Point', label: 'Point',
                    layers: [`${this.tabName}-layer-circle`, `${this.tabName}-layer-representative-points`],
                    svg: ''
                },
                {
                    type: 'Polygon', label: 'Polygon',
                    layers: [`${this.tabName}-layer-fill`, `${this.tabName}-layer-outline`],
                    svg: ''
                },
                {
                    type: 'LineString', label: 'LineString',
                    layers: [`${this.tabName}-layer-line`],
                    svg: ''
                }
            ];

            this.cachedAllFeatures = [];
            this.cachedFilteredFeatures = [];
            this.debouncedRefreshTimeout = null;

            this.init();
        }

        init() {
            this.setupEventListeners();
            // Initial SVG generation
            this.layerDefs.forEach(def => {
                def.svg = this.makeMultiLayerSvg(def.type, this.getInitialMode());
            });
            
            // Expose instance-specific functions to window for backward compatibility and easy access
            window[`initLayerStyle${this.tabName}`] = () => this.initLayerStyle();
            window[`applyMultiColor${this.tabName}`] = (mode, type) => this.applyMultiColor(mode, type);
            window[`updateOverview${this.tabName}`] = () => this.updateOverview();
            window[`updateLayerList${this.tabName}`] = () => this.updateLayerList();
            window[`openStyleSidebar${this.tabName}`] = () => this.open();
            window[`closeStyleSidebar${this.tabName}`] = () => this.close();
            window[`toggleStyleSidebar${this.tabName}`] = () => this.toggle();
            
            // Auto-open on large screens
            if (window.innerWidth >= 1200) {
                setTimeout(() => {
                    const activeLink = document.querySelector('#nav-sidebar .nav-link.active');
                    const activeTab = activeLink ? activeLink.id.replace(/^tab-/, '') : null;
                    const viewBtn = document.getElementById(`${this.tabName}-map-btn`);
                    const isMapView = viewBtn && viewBtn.classList.contains('active');

                    if (activeTab === this.tabName && isMapView) {
                        this.open();
                    }
                }, 1000);
            }
        }

        getInitialMode() {
            const sel = document.getElementById(`multi-color-select-${this.tabName}`);
            if (sel && sel.value) return sel.value;
            const hasTree = this.data.treeData && Object.keys(this.data.treeData).length > 0;
            return hasTree ? 'type' : 'class';
        }

        setupEventListeners() {
            const closeBtn = document.getElementById(`style-sidebar-close-${this.tabName}`);
            if (closeBtn) closeBtn.onclick = () => this.close();

            const backdrop = document.getElementById(`style-sidebar-backdrop-${this.tabName}`);
            if (backdrop) backdrop.onclick = () => this.close();

            const modal = document.getElementById(`layer-style-modal-${this.tabName}`);
            if (modal) {
                modal.addEventListener('show.bs.modal', () => {
                    const layerType = modal.dataset.layerType || null;
                    if (layerType) {
                        this.multiCurrentLayerType = layerType;
                        const titleEl = modal.querySelector('.modal-title');
                        if (titleEl) titleEl.textContent = 'Options – ' + layerType;
                        this.buildMultiSharedOpts(layerType);
                    }
                });
                modal.addEventListener('hidden.bs.modal', () => {
                    this.multiCurrentLayerType = null;
                });
            }
        }

        toggle() {
            const sidebar = document.getElementById(`style-sidebar-${this.tabName}`);
            if (!sidebar) return;
            sidebar.classList.toggle('open');

            const toggleBtn = document.querySelector('.style-sidebar-ctrl-btn');
            if (toggleBtn) {
                const container = toggleBtn.closest('.maplibregl-ctrl');
                if (container) {
                    container.classList.toggle('d-none', sidebar.classList.contains('open'));
                }
            }

            setTimeout(() => { if (this.map) this.map.resize(); }, 350);
        }

        open() {
            const sidebar = document.getElementById(`style-sidebar-${this.tabName}`);
            if (sidebar && !sidebar.classList.contains('open')) this.toggle();
        }

        close() {
            const sidebar = document.getElementById(`style-sidebar-${this.tabName}`);
            if (sidebar && sidebar.classList.contains('open')) this.toggle();
        }

        /**
         * Map Styling and Filtering
         */

        applyLayerVisibility() {
            const m = this.map;
            if (!m) return;
            const mode = this.getInitialMode();

            this.layerDefs.forEach(def => {
                const isLayerVisible = !this.hiddenLayerTypes.has(def.type);
                const visibility = isLayerVisible ? 'visible' : 'none';

                def.layers.forEach(layerId => {
                    if (!m.getLayer(layerId)) return;
                    m.setLayoutProperty(layerId, 'visibility', visibility);

                    if (isLayerVisible) {
                        const filter = this.buildFilter(layerId, mode);
                        try {
                            m.setFilter(layerId, filter.length > 1 ? filter : null);
                        } catch (e) {
                            console.error(`Error setting filter for ${layerId}`, filter, e);
                        }
                    }
                });
            });

            ['Point', 'Polygon', 'LineString'].forEach(t => {
                this.applyMultiColor(mode, t);
            });
        }

        buildFilter(layerId, mode) {
            let baseFilter = null;
            if (layerId.indexOf('layer-circle') !== -1) {
                baseFilter = ['all', ['==', '$type', 'Point'], ['!has', 'representative'], ['!has', 'original_geom_type']];
            } else if (layerId.indexOf('layer-representative-points') !== -1) {
                baseFilter = ['all', ['==', '$type', 'Point'], ['has', 'representative']];
            } else if (layerId.indexOf('layer-fill') !== -1 || layerId.indexOf('layer-outline') !== -1) {
                baseFilter = ['==', '$type', 'Polygon'];
            } else if (layerId.indexOf('layer-line') !== -1) {
                baseFilter = ['==', '$type', 'LineString'];
            }

            let filter = ['all'];
            if (baseFilter) {
                if (baseFilter[0] === 'all') {
                    for (let i = 1; i < baseFilter.length; i++) filter.push(baseFilter[i]);
                } else {
                    filter.push(baseFilter);
                }
            }

            if (mode === 'class' && this.hiddenClasses.size > 0) {
                const valid = [...this.hiddenClasses].filter(c => c != null);
                if (valid.length > 0) filter.push(['!in', 'class', ...valid]);
            } else if (mode === 'type' && this.hiddenTypes.size > 0) {
                const hiddenEids = [];
                if (this.data && this.data.tableData) {
                    this.data.tableData.forEach(e => {
                        if (e.id && e.type_id && this.hiddenTypes.has(String(e.type_id))) hiddenEids.push(Number(e.id));
                    });
                }
                if (hiddenEids.length > 0) filter.push(['!in', 'id', ...hiddenEids]);
            }
            return filter;
        }

        applyMultiColor(modeArg, typeArg) {
            let type = typeArg || this.multiCurrentLayerType;
            if (!type) {
                const modal = document.getElementById(`layer-style-modal-${this.tabName}`);
                if (modal && modal.dataset.layerType) type = modal.dataset.layerType;
            }
            if (!type) return;

            const mode = modeArg || this.getInitialMode();
            const m = this.map;
            if (!m) return;
            const s = this.multiSharedOpts[type];
            let colorExpr = '#888888';

            if (mode === 'class') {
                let colors = this.multiClassColors[type];
                if (!colors || Object.keys(colors).length === 0) {
                    this.buildMultiClassList(type);
                    colors = this.multiClassColors[type];
                }
                const classes = Object.keys(colors);
                if (classes.length > 0) {
                    colorExpr = ['match', ['get', 'class']];
                    classes.forEach(cls => colorExpr.push(cls, colors[cls]));
                    colorExpr.push('#888888');
                }
            } else if (mode === 'type') {
                let colors = this.multiTypeColors[type];
                if (!colors || Object.keys(colors).length === 0) {
                    this.buildMultiTypeList(type);
                    colors = this.multiTypeColors[type];
                }
                const eidMatches = [];
                if (this.data && this.data.tableData) {
                    this.data.tableData.forEach(e => {
                        if (e.id && e.type_id && colors[String(e.type_id)]) {
                            eidMatches.push(e.id, colors[String(e.type_id)]);
                        }
                    });
                }
                if (eidMatches.length > 0) {
                    colorExpr = ['match', ['get', 'id'], ...eidMatches, '#888888'];
                }
            }

            this.applyPaintProperties(type, colorExpr, s);
        }

        applyPaintProperties(type, colorExpr, s) {
            const m = this.map;
            if (!m) return;
            try {
                if (type === 'Polygon') {
                    if (m.getLayer(`${this.tabName}-layer-fill`)) {
                        m.setPaintProperty(`${this.tabName}-layer-fill`, 'fill-color', colorExpr);
                        m.setPaintProperty(`${this.tabName}-layer-fill`, 'fill-opacity', s.opacity ?? 0.5);
                    }
                    if (m.getLayer(`${this.tabName}-layer-outline`)) {
                        m.setPaintProperty(`${this.tabName}-layer-outline`, 'line-color', s.outlineColor ?? '#004747');
                        m.setPaintProperty(`${this.tabName}-layer-outline`, 'line-width', s.outlineWidth ?? 1.5);
                    }
                } else if (type === 'LineString') {
                    if (m.getLayer(`${this.tabName}-layer-line`)) {
                        m.setPaintProperty(`${this.tabName}-layer-line`, 'line-color', colorExpr);
                        m.setPaintProperty(`${this.tabName}-layer-line`, 'line-width', s.lineWidth ?? 2.5);
                        m.setPaintProperty(`${this.tabName}-layer-line`, 'line-opacity', s.opacity ?? 1);
                    }
                } else if (type === 'Point') {
                    [`${this.tabName}-layer-circle`, `${this.tabName}-layer-representative-points`].forEach(lid => {
                        if (m.getLayer(lid)) {
                            m.setPaintProperty(lid, 'circle-color', colorExpr);
                            m.setPaintProperty(lid, 'circle-radius', s.radius ?? 7);
                            m.setPaintProperty(lid, 'circle-stroke-color', s.strokeColor ?? '#ffffff');
                            m.setPaintProperty(lid, 'circle-stroke-width', s.strokeWidth ?? 1.5);
                            m.setPaintProperty(lid, 'circle-opacity', s.opacity ?? 1);
                            m.setPaintProperty(lid, 'circle-stroke-opacity', s.opacity ?? 1);
                        }
                    });
                }
            } catch (e) {
                console.error(`Error updating paint props for ${type}`, e);
            }
        }

        /**
         * SVG Generation
         */

        makeMultiSvg(type, color, cls = null) {
            const s = { opacity: 1, strokeWidth: 1.5, radius: 6, strokeColor: '#ffffff', outlineColor: '#004747', outlineWidth: 1 };
            if (type === 'Polygon') {
                return `<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <rect x="2" y="4" width="16" height="12" rx="1" fill="${color}" fill-opacity="${s.opacity}" 
                    stroke="${s.outlineColor}" stroke-width="${s.outlineWidth}"/></svg>`;
            } else if (type === 'LineString') {
                return `<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="2,16 7,6 13,12 18,4" fill="none" stroke="${color}" stroke-width="${s.strokeWidth + 1}" 
                    stroke-linejoin="round" stroke-linecap="round"/></svg>`;
            } else {
                return `<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="10" cy="10" r="${s.radius}" fill="${color}" stroke="${s.strokeColor}" stroke-width="${s.strokeWidth}"/></svg>`;
            }
        }

        makeMultiLayerSvg(type, mode) {
            const s = { strokeWidth: 1.5, radius: 7, strokeColor: '#ffffff', outlineColor: '#004747', outlineWidth: 1 };
            let colors = [];
            if (mode === 'type') colors = Object.values(this.multiTypeColors[type]);
            else colors = Object.values(this.multiClassColors[type]);

            const c0 = colors[0] || '#008888';
            const c1 = colors[1] || '#888800';

            if (type === 'Polygon') {
                return `<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <rect x="2" y="4" width="12" height="8" rx="1" fill="${c0}" fill-opacity="1" stroke="${s.outlineColor}" stroke-width="${s.outlineWidth}"/>
                    <rect x="6" y="8" width="12" height="8" rx="1" fill="${c1}" fill-opacity="1" stroke="${s.outlineColor}" stroke-width="${s.outlineWidth}"/></svg>`;
            } else if (type === 'LineString') {
                return `<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="2,16 10,6 18,16" fill="none" stroke="${c0}" stroke-width="${s.strokeWidth + 1}" stroke-linejoin="round" stroke-linecap="round"/>
                    <polyline points="2,10 10,4 18,10" fill="none" stroke="${c1}" stroke-width="${s.strokeWidth + 1}" stroke-linejoin="round" stroke-linecap="round"/></svg>`;
            } else {
                return `<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="6" cy="10" r="5" fill="${c0}" stroke="${s.strokeColor}" stroke-width="${s.strokeWidth}"/>
                    <circle cx="14" cy="10" r="5" fill="${c1}" stroke="${s.strokeColor}" stroke-width="${s.strokeWidth}"/></svg>`;
            }
        }

        /**
         * UI Listeners & Updates
         */

        debouncedRefresh() {
            if (this.debouncedRefreshTimeout) clearTimeout(this.debouncedRefreshTimeout);
            this.debouncedRefreshTimeout = setTimeout(() => {
                this.refreshMultiClassList();
                this.applyMultiColor();
            }, 100);
        }

        refreshLayerListSvg(type) {
            const mode = this.getInitialMode();
            const def = this.layerDefs.find(d => d.type === type);
            if (!def) return;

            def.svg = this.makeMultiLayerSvg(type, mode);
            const list = document.getElementById(`layer-list-${this.tabName}`);
            if (!list) return;
            
            list.querySelectorAll('.layer-info-btn').forEach(span => {
                const lbl = span.querySelector('span.flex-grow-1');
                if (lbl && lbl.textContent === def.label) {
                    const svgWrapper = span.querySelector('span.flex-shrink-0');
                    if (svgWrapper) svgWrapper.innerHTML = def.svg;
                }
            });
        }

        updateOverview() {
            const pane = document.getElementById(`pane-overview-${this.tabName}`);
            if (!pane) return;
            const counts = { Point: 0, Polygon: 0, LineString: 0 };
            this.cachedFilteredFeatures.forEach(f => {
                counts[this.getGeomCategory(f.geometry.type)]++;
            });

            const fragment = document.createDocumentFragment();
            const table = document.createElement('table');
            table.className = 'table table-sm table-borderless small mb-0';
            const tbody = document.createElement('tbody');

            this.layerDefs.forEach(def => {
                const tr = document.createElement('tr');
                const tdGeom = document.createElement('td');
                tdGeom.innerHTML = `<span class="me-2">${def.svg}</span>${def.label}`;
                const tdCount = document.createElement('td');
                tdCount.className = 'text-end text-muted';
                tdCount.textContent = counts[def.type];
                tr.appendChild(tdGeom);
                tr.appendChild(tdCount);
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            fragment.appendChild(table);
            pane.innerHTML = '';
            pane.appendChild(fragment);
        }

        getGeomCategory(geomType) {
            if (geomType === 'Polygon' || geomType === 'MultiPolygon') return 'Polygon';
            if (geomType === 'LineString' || geomType === 'MultiLineString') return 'LineString';
            return 'Point';
        }

        updateLayerList() {
            const list = document.getElementById(`layer-list-${this.tabName}`);
            if (!list) return;
            list.innerHTML = '';

            this.layerDefs.forEach(def => {
                const li = document.createElement('li');
                li.className = 'mb-2';
                const isVisible = !this.hiddenLayerTypes.has(def.type);

                const row = document.createElement('div');
                row.className = 'd-flex align-items-center gap-2';

                const cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.className = 'form-check-input';
                cb.checked = isVisible;
                cb.onchange = (e) => {
                    e.stopPropagation();
                    if (cb.checked) this.hiddenLayerTypes.delete(def.type);
                    else this.hiddenLayerTypes.add(def.type);
                    this.applyLayerVisibility();
                };

                const btn = document.createElement('span');
                btn.className = 'layer-info-btn d-flex align-items-center flex-grow-1 p-1 rounded border';
                btn.style.cursor = 'pointer';
                btn.onclick = () => {
                    const modalEl = document.getElementById(`layer-style-modal-${this.tabName}`);
                    if (modalEl) {
                        modalEl.dataset.layerType = def.type;
                        const modal = new bootstrap.Modal(modalEl);
                        modal.show();
                    }
                };

                btn.innerHTML = `
                    <span class="flex-shrink-0 me-2">${def.svg}</span>
                    <span class="flex-grow-1 small">${def.label}</span>
                    <i class="bi bi-gear flex-shrink-0 text-muted small"></i>
                `;

                const legendToggle = document.createElement('button');
                legendToggle.className = 'btn btn-link btn-sm p-0 text-decoration-none';
                legendToggle.innerHTML = '<i class="bi bi-chevron-down"></i>';
                legendToggle.onclick = () => {
                    const legend = document.getElementById(`layer-legend-${this.tabName}-${def.type}`);
                    if (legend) {
                        legend.classList.toggle('d-none');
                        legendToggle.querySelector('i').classList.toggle('bi-chevron-down');
                        legendToggle.querySelector('i').classList.toggle('bi-chevron-up');
                        if (!legend.classList.contains('d-none')) {
                            const mode = this.getInitialMode();
                            if (mode === 'type') this.buildMultiTypeList(def.type, legend);
                            else this.buildMultiClassList(def.type, legend);
                        }
                    }
                };

                row.appendChild(cb);
                row.appendChild(btn);
                row.appendChild(legendToggle);
                li.appendChild(row);

                const legendDiv = document.createElement('div');
                legendDiv.id = `layer-legend-${this.tabName}-${def.type}`;
                legendDiv.className = 'ms-4 mt-1 d-none';
                li.appendChild(legendDiv);

                list.appendChild(li);
            });
        }

        initLayerStyle() {
            const hasTree = this.data.treeData && Object.keys(this.data.treeData).length > 0;
            const hasClasses = this.classList && this.classList.length >= 1;
            if (!hasTree && !hasClasses) return;

            const mode = hasTree ? 'type' : 'class';
            ['Point', 'Polygon', 'LineString'].forEach(t => {
                const hasGeom = this.cachedAllFeatures.some(f => this.getGeomCategory(f.geometry.type) === t);
                if (!hasGeom) return;

                this.multiCurrentLayerType = t;
                if (mode === 'type') {
                    this.buildMultiTypeList(t);
                    this.applyMultiColor('type');
                } else {
                    this.buildMultiClassList(t);
                    this.applyMultiColor('class');
                }

                const legend = document.getElementById(`layer-legend-${this.tabName}-${t}`);
                if (legend && !legend.classList.contains('d-none')) {
                    if (mode === 'type') this.buildMultiTypeList(t, legend);
                    else this.buildMultiClassList(t, legend);
                }
            });

            this.applyLayerVisibility();
            const modalEl = document.getElementById(`layer-style-modal-${this.tabName}`);
            if (modalEl && !modalEl.classList.contains('show')) {
                this.multiCurrentLayerType = null;
            }
        }

        buildMultiTypeList(type, targetList = null) {
            const colors = this.multiTypeColors[type];
            const tree = this.data.treeData;
            if (!tree) return;

            const typeList = [];
            const processNode = (node) => {
                const hasGeom = this.cachedAllFeatures.some(f => 
                    f.properties.type_id == node.id && this.getGeomCategory(f.geometry.type) === type
                );
                if (hasGeom) typeList.push(node);
                if (node.children) node.children.forEach(processNode);
            };
            Object.values(tree).forEach(processNode);

            if (targetList) targetList.innerHTML = '';
            const fragment = document.createDocumentFragment();

            typeList.forEach((t, idx) => {
                const sid = String(t.id);
                if (!colors[sid]) colors[sid] = this.getColor(idx, typeList.length);
                
                if (targetList) {
                    const item = this.createLegendItem('type', sid, t.name, colors[sid], (checked) => {
                        if (checked) this.hiddenTypes.delete(sid);
                        else this.hiddenTypes.add(sid);
                        this.applyLayerVisibility();
                    }, type);
                    fragment.appendChild(item);
                }
            });
            if (targetList) targetList.appendChild(fragment);
        }

        buildMultiClassList(type, targetList = null) {
            const colors = this.multiClassColors[type];
            const classes = this.classList;
            if (!classes) return;

            const filteredClasses = classes.filter(cls => 
                this.cachedAllFeatures.some(f => 
                    f.properties.class === cls && this.getGeomCategory(f.geometry.type) === type
                )
            );

            if (targetList) targetList.innerHTML = '';
            const fragment = document.createDocumentFragment();

            filteredClasses.forEach((cls, idx) => {
                if (!colors[cls]) colors[cls] = this.getColor(idx, filteredClasses.length);
                
                if (targetList) {
                    const item = this.createLegendItem('class', cls, cls, colors[cls], (checked) => {
                        if (checked) this.hiddenClasses.delete(cls);
                        else this.hiddenClasses.add(cls);
                        this.applyLayerVisibility();
                    }, type);
                    fragment.appendChild(item);
                }
            });
            if (targetList) targetList.appendChild(fragment);
        }

        createLegendItem(mode, id, label, color, onCheck, type) {
            const div = document.createElement('div');
            div.className = 'd-flex align-items-center gap-2 mb-1';
            
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.className = 'form-check-input';
            const isHidden = (mode === 'type' ? this.hiddenTypes : this.hiddenClasses).has(id);
            cb.checked = !isHidden;
            cb.onchange = (e) => { e.stopPropagation(); onCheck(cb.checked); };
            
            const svgWrap = document.createElement('span');
            svgWrap.className = 'position-relative d-inline-block';
            svgWrap.style.width = '20px';
            svgWrap.style.height = '20px';
            svgWrap.innerHTML = this.makeMultiSvg(type, color);
            
            const picker = document.createElement('input');
            picker.type = 'color';
            picker.className = 'position-absolute top-0 start-0 w-100 h-100 opacity-0';
            picker.style.cursor = 'pointer';
            picker.value = color;
            picker.oninput = (e) => {
                e.stopPropagation();
                const newColor = picker.value;
                if (mode === 'type') this.multiTypeColors[type][id] = newColor;
                else this.multiClassColors[type][id] = newColor;
                const svg = svgWrap.querySelector('svg');
                if (svg) svg.outerHTML = this.makeMultiSvg(type, newColor);
                this.applyMultiColor(mode, type);
            };
            picker.onchange = () => {
                this.debouncedRefresh();
                this.refreshLayerListSvg(type);
            };
            
            svgWrap.appendChild(picker);
            
            const lbl = document.createElement('span');
            lbl.className = 'small text-truncate';
            lbl.textContent = label;
            
            div.appendChild(cb);
            div.appendChild(svgWrap);
            div.appendChild(lbl);
            return div;
        }

        refreshMultiClassList() {
            const types = ['Point', 'Polygon', 'LineString'];
            types.forEach(t => {
                const legend = document.getElementById(`layer-legend-${this.tabName}-${t}`);
                if (legend && !legend.classList.contains('d-none')) {
                    const mode = this.getInitialMode();
                    if (mode === 'type') this.buildMultiTypeList(t, legend);
                    else this.buildMultiClassList(t, legend);
                }
            });
        }

        getColor(idx, total) {
            const hue = (idx * (360 / Math.max(total, 1))) % 360;
            return `hsl(${hue}, 70%, 50%)`;
        }

        buildMultiSharedOpts(type) {
            const container = document.getElementById(`multi-shared-opts-${this.tabName}`);
            if (!container) return;
            container.innerHTML = '';
            if (!type) return;

            const s = this.multiSharedOpts[type];
            const fragment = document.createDocumentFragment();

            if (type === 'Polygon') {
                fragment.appendChild(this.makeColorRow('Outline Color', 'outlineColor', s.outlineColor, (v) => { s.outlineColor = v; this.debouncedRefresh(); }));
                fragment.appendChild(this.makeRangeRow('Outline Width', 'outlineWidth', s.outlineWidth, 0, 10, 0.5, (v) => { s.outlineWidth = v; this.debouncedRefresh(); }));
                fragment.appendChild(this.makeRangeRow('Opacity', 'opacity', s.opacity, 0, 1, 0.05, (v) => { s.opacity = v; this.debouncedRefresh(); }));
            } else if (type === 'LineString') {
                fragment.appendChild(this.makeRangeRow('Line Width', 'lineWidth', s.lineWidth, 0.5, 20, 0.5, (v) => { s.lineWidth = v; this.debouncedRefresh(); }));
                fragment.appendChild(this.makeRangeRow('Opacity', 'opacity', s.opacity, 0, 1, 0.05, (v) => { s.opacity = v; this.debouncedRefresh(); }));
            } else if (type === 'Point') {
                fragment.appendChild(this.makeRangeRow('Radius', 'radius', s.radius, 1, 50, 1, (v) => { s.radius = v; this.debouncedRefresh(); }));
                fragment.appendChild(this.makeColorRow('Stroke Color', 'strokeColor', s.strokeColor, (v) => { s.strokeColor = v; this.debouncedRefresh(); }));
                fragment.appendChild(this.makeRangeRow('Stroke Width', 'strokeWidth', s.strokeWidth, 0, 10, 0.5, (v) => { s.strokeWidth = v; this.debouncedRefresh(); }));
                fragment.appendChild(this.makeRangeRow('Opacity', 'opacity', s.opacity ?? 1, 0, 1, 0.05, (v) => { s.opacity = v; this.debouncedRefresh(); }));
            }
            container.appendChild(fragment);
        }

        makeColorRow(label, key, value, onChange) {
            const div = document.createElement('div');
            div.className = 'mb-3';
            div.innerHTML = `<label class="form-label small fw-semibold mb-1">${label}</label>`;
            const input = document.createElement('input');
            input.type = 'color';
            input.className = 'form-control form-control-color w-100';
            input.value = value;
            input.oninput = () => onChange(input.value);
            div.appendChild(input);
            return div;
        }

        makeRangeRow(label, key, value, min, max, step, onChange) {
            const div = document.createElement('div');
            div.className = 'mb-3';
            div.innerHTML = `<label class="form-label small fw-semibold mb-1">${label}</label>`;
            const group = document.createElement('div');
            group.className = 'd-flex align-items-center gap-2';
            const range = document.createElement('input');
            range.type = 'range';
            range.className = 'form-range flex-grow-1';
            range.min = min; range.max = max; range.step = step; range.value = value;
            const num = document.createElement('input');
            num.type = 'number';
            num.className = 'form-control form-control-sm';
            num.style.width = '4rem';
            num.min = min; num.max = max; num.step = step; num.value = value;
            
            range.oninput = () => { num.value = range.value; onChange(Number(range.value)); };
            num.oninput = () => { range.value = num.value; onChange(Number(num.value)); };
            
            group.appendChild(range);
            group.appendChild(num);
            div.appendChild(group);
            return div;
        }
    }

    window.StyleSidebarManager = StyleSidebarManager;
}

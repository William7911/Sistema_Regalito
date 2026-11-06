(function () {
    'use strict';

    const MAX_RESULTS = 8;

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function normalize(value) {
        return String(value == null ? '' : value)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function attachProductSuggestions(options) {
        const input = options && options.input;
        const list = options && options.list;

        if (!input || !list || typeof options.getItems !== 'function') {
            return null;
        }

        const minChars = Number.isFinite(options.minChars) ? options.minChars : 2;
        const debounceMs = Number.isFinite(options.debounceMs) ? options.debounceMs : 220;
        const emptyText = options.emptyText || 'Sin coincidencias.';

        let items = [];
        let activeIndex = -1;
        let timer = null;
        let requestSeq = 0;
        let suppress = false;

        if (!list.id) {
            list.id = 'product-suggestions-' + Math.random().toString(36).slice(2, 8);
        }

        input.setAttribute('role', 'combobox');
        input.setAttribute('aria-autocomplete', 'list');
        input.setAttribute('aria-expanded', 'false');
        input.setAttribute('aria-controls', list.id);
        list.setAttribute('role', 'listbox');

        function hide() {
            clearTimeout(timer);
            timer = null;
            requestSeq += 1;
            activeIndex = -1;
            list.classList.add('d-none');
            list.innerHTML = '';
            input.setAttribute('aria-expanded', 'false');
            input.removeAttribute('aria-activedescendant');
        }

        function markActive(index) {
            activeIndex = index;
            const nodes = list.querySelectorAll('.product-suggestion-item');
            nodes.forEach(function (node, i) {
                const selected = i === index;
                node.classList.toggle('is-active', selected);
                node.setAttribute('aria-selected', selected ? 'true' : 'false');
            });
            const current = nodes[index];
            if (current && current.id) {
                input.setAttribute('aria-activedescendant', current.id);
            } else {
                input.removeAttribute('aria-activedescendant');
            }
        }

        function render() {
            if (!items.length) {
                list.innerHTML = '<div class="product-suggestion-empty">' + escapeHtml(emptyText) + '</div>';
            } else {
                list.innerHTML = items.map(function (item, index) {
                    const sublabel = item.sublabel
                        ? '<span class="product-suggestion-sub">' + escapeHtml(item.sublabel) + '</span>'
                        : '';
                    const meta = item.meta
                        ? '<span class="product-suggestion-meta">' + escapeHtml(item.meta) + '</span>'
                        : '';
                    return '<div class="product-suggestion-item' + (index === activeIndex ? ' is-active' : '') + '"'
                        + ' id="' + list.id + '-opt-' + index + '"'
                        + ' role="option"'
                        + ' aria-selected="' + (index === activeIndex ? 'true' : 'false') + '"'
                        + ' data-index="' + index + '">'
                        + '<span class="product-suggestion-main">'
                        + '<span class="product-suggestion-name">' + escapeHtml(item.label) + '</span>'
                        + sublabel
                        + '</span>'
                        + meta
                        + '</div>';
                }).join('');
            }
            list.classList.remove('d-none');
            input.setAttribute('aria-expanded', 'true');
            if (activeIndex >= 0) {
                markActive(activeIndex);
            }
        }

        function select(index) {
            const item = items[index];
            if (!item) {
                return;
            }
            suppress = true;
            input.value = item.value == null ? '' : item.value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            hide();
            if (typeof options.onSelect === 'function') {
                options.onSelect(item, input);
            }
            suppress = false;
        }

        async function refresh(term) {
            const seq = ++requestSeq;
            let result = [];
            try {
                result = await options.getItems(term);
            } catch (error) {
                result = [];
            }
            if (seq !== requestSeq) {
                return;
            }
            items = Array.isArray(result) ? result.slice(0, MAX_RESULTS) : [];
            activeIndex = -1;
            render();
        }

        function schedule() {
            if (suppress) {
                return;
            }
            const term = normalize(input.value);
            clearTimeout(timer);
            timer = null;
            requestSeq += 1;
            if (term.length < minChars) {
                items = [];
                hide();
                return;
            }
            timer = setTimeout(function () {
                refresh(term);
            }, debounceMs);
        }

        input.addEventListener('input', schedule);

        input.addEventListener('focus', function () {
            if (normalize(input.value).length >= minChars) {
                schedule();
            }
        });

        input.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                hide();
                return;
            }
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
                if (list.classList.contains('d-none')) {
                    if (normalize(input.value).length >= minChars) {
                        event.preventDefault();
                        refresh(normalize(input.value));
                    }
                    return;
                }
                if (!items.length) {
                    return;
                }
                event.preventDefault();
                const step = event.key === 'ArrowDown' ? 1 : -1;
                let next = activeIndex + step;
                if (next < 0) next = items.length - 1;
                if (next >= items.length) next = 0;
                markActive(next);
                return;
            }
            if (event.key === 'Enter') {
                if (!list.classList.contains('d-none') && items.length) {
                    event.preventDefault();
                    const target = activeIndex >= 0 ? activeIndex : (items.length === 1 ? 0 : -1);
                    if (target >= 0) {
                        select(target);
                        return;
                    }
                }
                if (typeof options.onSubmit === 'function') {
                    event.preventDefault();
                    hide();
                    options.onSubmit(input.value, input);
                }
                return;
            }
            if (event.key === 'Tab') {
                hide();
            }
        });

        list.addEventListener('mousedown', function (event) {
            const node = event.target.closest('.product-suggestion-item');
            if (!node) {
                return;
            }
            event.preventDefault();
            select(Number(node.getAttribute('data-index')));
        });

        document.addEventListener('click', function (event) {
            if (event.target === input || list.contains(event.target)) {
                return;
            }
            hide();
        });

        return {
            refresh: function () {
                refresh(normalize(input.value));
            },
            hide: hide
        };
    }

    window.attachProductSuggestions = attachProductSuggestions;
})();

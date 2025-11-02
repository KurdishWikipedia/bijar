document.addEventListener('DOMContentLoaded', function() {
    // Create formatters once for performance
    const indoArabicFormatter = new Intl.NumberFormat('ar-IQ');
    const dateTimeFormatter = new Intl.DateTimeFormat('ckb-IQ', { dateStyle: 'short', timeStyle: 'short' });

    // --- Element Selectors ---
    const tableBody = document.getElementById('words-table-body');
    const searchInput = document.getElementById('search-input');
    const tableHeaders = document.querySelectorAll('#words-table th[data-sort]');
    const rowsPerPageSelect = document.getElementById('rows-per-page');
    const bottomPaginationWrapper = document.getElementById('bottom-pagination-wrapper');
    const entriesInfo = document.getElementById('entries-info');

    // --- State Variables ---
    let allWords = [];
    let currentSort = { column: 'request_count', direction: 'desc' };
    let rowsPerPage = parseInt(rowsPerPageSelect.value, 10);
    let currentPage = 1;

    // --- Initial Loading State ---
    tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">دراوەکان بار دەکرێن...</td></tr>`;

    function renderTable(data) {
        if (data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">ھیچ وشەیەک نەدۆزرایەوە.</td></tr>`;
            return;
        }
        tableBody.innerHTML = data.map(item => `
            <tr data-status="${item.status}">
                <td>${item.word}</td>
                <td>${indoArabicFormatter.format(item.request_count)}</td>
                <td>${item.status_kurdish}</td>
                <td>${dateTimeFormatter.format(new Date(item.first_seen))}</td>
                <td>${dateTimeFormatter.format(new Date(item.last_updated))}</td>
            </tr>
        `).join('');
    }
    
    //  Update "Showing X to Y of Z" text
    function updateEntriesInfo(totalItems, startIndex, endIndex) {
        if (totalItems === 0) {
            entriesInfo.innerHTML = '';
            return;
        }
        const start = indoArabicFormatter.format(startIndex + 1);
        const end = indoArabicFormatter.format(Math.min(endIndex, totalItems));
        const total = indoArabicFormatter.format(totalItems);
        entriesInfo.innerHTML = `پیشاندانی ${start} تا ${end} وشە لە کۆی گشتیی ${total} وشە`;
    }

    // Advanced pagination function with Previous/Next and ellipsis
    function renderPagination(totalItems) {
        const pageCount = Math.ceil(totalItems / rowsPerPage);
        let html = '';

        if (pageCount > 1) {
            html += '<ul class="pagination">';
            // Previous button
            html += `<li class="${currentPage === 1 ? 'disabled' : ''}"><a href="#" data-page="${currentPage - 1}">پێشوو</a></li>`;

            let pages = [];
            if (pageCount <= 7) { // Show all pages if 7 or less
                for (let i = 1; i <= pageCount; i++) pages.push(i);
            } else { // Handle ellipsis logic
                pages.push(1);
                if (currentPage > 3) pages.push('...');
                
                let start = Math.max(2, currentPage - 1);
                let end = Math.min(pageCount - 1, currentPage + 1);
                for (let i = start; i <= end; i++) pages.push(i);

                if (currentPage < pageCount - 2) pages.push('...');
                pages.push(pageCount);
            }
            
            pages.forEach(p => {
                if (p === '...') {
                    html += `<li class="disabled"><span>...</span></li>`;
                } else {
                    html += `<li class="${p === currentPage ? 'active' : ''}"><a href="#" data-page="${p}">${indoArabicFormatter.format(p)}</a></li>`;
                }
            });
            
            // Next button
            html += `<li class="${currentPage === pageCount ? 'disabled' : ''}"><a href="#" data-page="${currentPage + 1}">دواتر</a></li>`;
            html += '</ul>';
        }
        bottomPaginationWrapper.innerHTML = html;
    }

    function filterAndPaginate() {
        const filter = searchInput.value.toLowerCase();
        const filtered = allWords.filter(item => item.word.toLowerCase().includes(filter));
        const sorted = sortData(filtered);

        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        const paginatedData = sorted.slice(startIndex, endIndex);

        renderTable(paginatedData);
        updateEntriesInfo(sorted.length, startIndex, endIndex);
        renderPagination(sorted.length);
    }

    // --- Helper Functions ---
    function sortData(data) { return data.sort((a, b) => { let valA = a[currentSort.column]; let valB = b[currentSort.column]; if (currentSort.column.includes('date') || currentSort.column.includes('seen')) { valA = new Date(valA); valB = new Date(valB); } if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1; if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1; return 0; }); }
    function updateSortIndicators() { tableHeaders.forEach(th => { th.classList.remove('sort-asc', 'sort-desc'); if (th.dataset.sort === currentSort.column) { th.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc'); } }); }

    // --- Event Listeners ---
    searchInput.addEventListener('input', () => { currentPage = 1; filterAndPaginate(); });
    rowsPerPageSelect.addEventListener('change', () => { rowsPerPage = parseInt(rowsPerPageSelect.value, 10); currentPage = 1; filterAndPaginate(); });
    tableHeaders.forEach(header => { header.addEventListener('click', () => { const column = header.dataset.sort; const newDirection = currentSort.column === column && currentSort.direction === 'desc' ? 'asc' : 'desc'; currentSort = { column, direction: newDirection }; currentPage = 1; filterAndPaginate(); updateSortIndicators(); }); });
    bottomPaginationWrapper.addEventListener('click', function(e) { if (e.target.tagName === 'A' && !e.target.parentElement.classList.contains('disabled')) { e.preventDefault(); currentPage = parseInt(e.target.dataset.page, 10); filterAndPaginate(); } });
    
    // --- Initial Fetch ---
    fetch('/api/get_requested_words').then(res => res.json()).then(data => { allWords = data; filterAndPaginate(); updateSortIndicators(); }).catch(err => { tableBody.innerHTML = `<tr><td colspan="5">ھەڵەیەک لە کاتی بارکردنی دراوەکە ڕووی دا: ${err.message}</td></tr>`; });
});
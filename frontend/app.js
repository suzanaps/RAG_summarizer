// CONFIGURATION
const API_BASE_URL = 'http://localhost:8000';

// APP STATE
let state = {
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    files: [],
    selectedIds: new Set(),
    searchQuery: '',
    pagination: {
        page: 1,
        limit: 10,
        total: 0
    },
    isLoading: false
};

// DOM ELEMENTS
const dom = {
    authSection: document.getElementById('auth-section'),
    dashboardSection: document.getElementById('dashboard-section'),
    
    // Auth Forms
    loginForm: document.getElementById('login-form'),
    signupForm: document.getElementById('signup-form'),
    toSignupLink: document.getElementById('to-signup'),
    toLoginLink: document.getElementById('to-login'),
    authSubtitle: document.getElementById('auth-subtitle-text'),
    
    // Profile
    sidebarUserEmail: document.getElementById('sidebar-user-email'),
    userAvatarInitials: document.getElementById('user-avatar-initials'),
    logoutBtn: document.getElementById('logout-btn'),
    
    // Drag & Drop Upload
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    progressBar: document.getElementById('upload-progress-bar'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    
    // List & Controls
    searchInput: document.getElementById('search-input'),
    filesListBody: document.getElementById('files-list-body'),
    emptyState: document.getElementById('empty-state'),
    loadingState: document.getElementById('loading-state'),
    selectAllCheckbox: document.getElementById('select-all-checkbox'),
    
    // Pagination
    prevPageBtn: document.getElementById('prev-page-btn'),
    nextPageBtn: document.getElementById('next-page-btn'),
    pageIndicator: document.getElementById('page-indicator-text'),
    limitSelect: document.getElementById('limit-select'),
    paginationInfoText: document.getElementById('pagination-info-text'),
    
    // Floating Selection Bar
    selectionBar: document.getElementById('selection-bar'),
    selectedCountBadge: document.getElementById('selected-count-badge'),
    actionSummaryBtn: document.getElementById('action-summary-btn'),
    clearSelectionBtn: document.getElementById('clear-selection-btn'),
    
    // Toasts
    toastContainer: document.getElementById('toast-container')
};

// -------------------------------------------------------------
// TOAST NOTIFICATIONS
// -------------------------------------------------------------
function showToast(message, type = 'success', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // SVG icons based on type
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === 'error') {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    } else {
        iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
    }

    toast.innerHTML = `${iconSvg}<span>${message}</span>`;
    dom.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-closing');
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, duration);
}

// -------------------------------------------------------------
// ROUTING & VIEW UPDATES
// -------------------------------------------------------------
function updateView() {
    if (state.token) {
        dom.authSection.classList.add('hidden');
        dom.dashboardSection.classList.remove('hidden');
        
        // Update User Details
        if (state.user && state.user.email) {
            dom.sidebarUserEmail.textContent = state.user.email;
            dom.userAvatarInitials.textContent = state.user.email.substring(0, 2).toUpperCase();
        }
        
        // Load initial files
        fetchFiles();
    } else {
        dom.dashboardSection.classList.add('hidden');
        dom.authSection.classList.remove('hidden');
        resetForms();
    }
}

function resetForms() {
    dom.loginForm.reset();
    dom.signupForm.reset();
    toggleAuthForm('login');
}

function toggleAuthForm(formName) {
    if (formName === 'login') {
        dom.loginForm.classList.remove('hidden');
        dom.loginForm.classList.add('active');
        dom.signupForm.classList.add('hidden');
        dom.signupForm.classList.remove('active');
        dom.authSubtitle.textContent = 'Faça login para gerenciar seus documentos PDF';
    } else {
        dom.signupForm.classList.remove('hidden');
        dom.signupForm.classList.add('active');
        dom.loginForm.classList.add('hidden');
        dom.loginForm.classList.remove('active');
        dom.authSubtitle.textContent = 'Crie uma conta para começar';
    }
}

// -------------------------------------------------------------
// SECURE API CLIENT
// -------------------------------------------------------------
async function apiPost(endpoint, body, needsAuth = false) {
    const headers = { 'Content-Type': 'application/json' };
    if (needsAuth && state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body)
    });
    
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Ocorreu um erro no servidor.');
    }
    return data;
}

async function apiGet(endpoint, needsAuth = true) {
    const headers = {};
    if (needsAuth && state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers
    });
    
    if (response.status === 401) {
        logout();
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
    }
    
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Erro ao carregar dados.');
    }
    return data;
}

// -------------------------------------------------------------
// AUTHENTICATION FLOW
// -------------------------------------------------------------
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const spinner = dom.loginForm.querySelector('.btn-spinner');
    
    try {
        spinner.classList.remove('hidden');
        const data = await apiPost('/auth/login', { email, password });
        
        state.token = data.access_token;
        state.user = data.user;
        
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));
        
        showToast('Login efetuado com sucesso!');
        updateView();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        spinner.classList.add('hidden');
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;
    const spinner = dom.signupForm.querySelector('.btn-spinner');
    
    if (password !== confirmPassword) {
        showToast('As senhas não coincidem.', 'error');
        return;
    }
    
    try {
        spinner.classList.remove('hidden');
        const data = await apiPost('/auth/register', { email, password });
        
        state.token = data.access_token;
        state.user = data.user;
        
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));
        
        showToast('Cadastro realizado com sucesso!');
        updateView();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        spinner.classList.add('hidden');
    }
}

function logout() {
    state.token = null;
    state.user = null;
    state.files = [];
    state.selectedIds.clear();
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    showToast('Sessão encerrada.');
    updateView();
    updateSelectionBar();
}

// -------------------------------------------------------------
// FILE LISTING, PAGINATION AND SELECTIONS
// -------------------------------------------------------------
async function fetchFiles() {
    if (state.isLoading) return;
    
    state.isLoading = true;
    dom.loadingState.classList.remove('hidden');
    dom.emptyState.classList.add('hidden');
    dom.filesListBody.innerHTML = '';
    
    try {
        const data = await apiGet(`/documents?page=${state.pagination.page}&limit=${state.pagination.limit}`);
        state.files = data.items;
        state.pagination.total = data.total;
        
        renderFilesList();
        renderPagination();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        state.isLoading = false;
        dom.loadingState.classList.add('hidden');
    }
}

function formatBytes(bytes, decimals = 2) {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function renderFilesList() {
    let filteredFiles = state.files;
    if (state.searchQuery) {
        filteredFiles = state.files.filter(f => f.filename.toLowerCase().includes(state.searchQuery.toLowerCase()));
    }
    
    if (filteredFiles.length === 0) {
        dom.emptyState.classList.remove('hidden');
        dom.selectAllCheckbox.checked = false;
        return;
    }
    
    dom.emptyState.classList.add('hidden');
    
    let allCheckedOnPage = true;
    
    filteredFiles.forEach(file => {
        const isChecked = state.selectedIds.has(file.id);
        if (!isChecked) allCheckedOnPage = false;
        
        const row = document.createElement('tr');
        row.className = isChecked ? 'selected' : '';
        row.dataset.id = file.id;
        
        row.innerHTML = `
            <td class="col-checkbox">
                <div class="checkbox-container">
                    <input type="checkbox" class="file-checkbox" ${isChecked ? 'checked' : ''}>
                </div>
            </td>
            <td class="col-name">
                <div class="file-name-cell">
                    <svg class="file-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"></path>
                        <path d="M14 2V8H20"></path>
                    </svg>
                    <span>${escapeHtml(file.filename)}</span>
                </div>
            </td>
            <td class="col-date">${formatDate(file.upload_date)}</td>
            <td class="col-size">${formatBytes(file.size_bytes)}</td>
            <td class="col-actions">
                <div class="action-buttons">
                    <button class="btn-action btn-download" title="Visualizar/Baixar PDF">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                    </button>
                </div>
            </td>
        `;
        
        const checkbox = row.querySelector('.file-checkbox');
        checkbox.addEventListener('change', () => toggleFileSelection(file.id, checkbox.checked));
        
        row.querySelector('.btn-download').addEventListener('click', (e) => {
            e.stopPropagation();
            downloadFile(file.id, file.filename);
        });
        
        dom.filesListBody.appendChild(row);
    });
    
    dom.selectAllCheckbox.checked = allCheckedOnPage && filteredFiles.length > 0;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderPagination() {
    const start = (state.pagination.page - 1) * state.pagination.limit + 1;
    const end = Math.min(start + state.files.length - 1, state.pagination.total);
    
    dom.pageIndicator.textContent = state.pagination.page;
    dom.prevPageBtn.disabled = state.pagination.page <= 1;
    dom.nextPageBtn.disabled = end >= state.pagination.total;
    
    if (state.pagination.total === 0) {
        dom.paginationInfoText.textContent = 'Mostrando 0-0 de 0 arquivos';
    } else {
        dom.paginationInfoText.textContent = `Mostrando ${start}-${end} de ${state.pagination.total} arquivos`;
    }
}

function toggleFileSelection(fileId, isSelected) {
    if (isSelected) {
        state.selectedIds.add(fileId);
    } else {
        state.selectedIds.delete(fileId);
    }
    
    // Update individual row selection state
    const row = dom.filesListBody.querySelector(`tr[data-id="${fileId}"]`);
    if (row) {
        row.className = isSelected ? 'selected' : '';
        const checkbox = row.querySelector('.file-checkbox');
        if (checkbox) checkbox.checked = isSelected;
    }
    
    // Update master checkbox state
    const checkboxes = Array.from(dom.filesListBody.querySelectorAll('.file-checkbox'));
    dom.selectAllCheckbox.checked = checkboxes.length > 0 && checkboxes.every(cb => cb.checked);
    
    updateSelectionBar();
}

function toggleSelectAll(isSelected) {
    state.files.forEach(file => {
        toggleFileSelection(file.id, isSelected);
    });
}

function clearSelection() {
    state.selectedIds.clear();
    dom.selectAllCheckbox.checked = false;
    Array.from(dom.filesListBody.querySelectorAll('.file-checkbox')).forEach(cb => {
        cb.checked = false;
    });
    Array.from(dom.filesListBody.querySelectorAll('tr')).forEach(tr => {
        tr.classList.remove('selected');
    });
    updateSelectionBar();
}

function updateSelectionBar() {
    const count = state.selectedIds.size;
    dom.selectedCountBadge.textContent = count;
    
    if (count > 0) {
        dom.selectionBar.classList.remove('hidden');
    } else {
        dom.selectionBar.classList.add('hidden');
    }
}

// -------------------------------------------------------------
// DOWNLOAD FILE SECURELY
// -------------------------------------------------------------
async function downloadFile(fileId, filename) {
    try {
        const response = await fetch(`${API_BASE_URL}/documents/${fileId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${state.token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('Acesso negado. Você não tem permissão para acessar este arquivo.');
            }
            if (response.status === 404) {
                throw new Error('Arquivo não encontrado no servidor.');
            }
            throw new Error('Erro ao baixar arquivo.');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showToast('Download do arquivo iniciado.');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// -------------------------------------------------------------
// FILE UPLOAD PROCESS (DRAG & DROP)
// -------------------------------------------------------------
async function uploadFile(file) {
    if (file.type !== 'application/pdf') {
        showToast('Formato de arquivo inválido. Apenas arquivos PDF são permitidos.', 'error');
        return;
    }
    
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showToast('O tamanho do arquivo excede o limite de 50MB.', 'error');
        return;
    }
    
    dom.progressBar.classList.remove('hidden');
    dom.progressFill.style.transform = 'scaleX(0)';
    dom.progressText.textContent = 'Preparando envio...';
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', `${API_BASE_URL}/documents/upload`);
        xhr.setRequestHeader('Authorization', `Bearer ${state.token}`);
        
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total);
                dom.progressFill.style.transform = `scaleX(${percentComplete})`;
                dom.progressText.textContent = `Enviando... ${Math.round(percentComplete * 100)}%`;
            }
        };
        
        const responsePromise = new Promise((resolve, reject) => {
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    let errMsg = 'Erro no envio.';
                    try {
                        const res = JSON.parse(xhr.responseText);
                        errMsg = res.detail || errMsg;
                    } catch (e) {}
                    reject(new Error(errMsg));
                }
            };
            xhr.onerror = () => reject(new Error('Erro de conexão com o servidor.'));
        });
        
        xhr.send(formData);
        
        await responsePromise;
        
        showToast('Arquivo enviado com sucesso!');
        state.pagination.page = 1;
        fetchFiles();
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        setTimeout(() => {
            dom.progressBar.classList.add('hidden');
            dom.fileInput.value = '';
        }, 1000);
    }
}

// -------------------------------------------------------------
// EVENT BINDINGS
// -------------------------------------------------------------
function initEvents() {
    // Auth navigation
    dom.toSignupLink.addEventListener('click', (e) => { e.preventDefault(); toggleAuthForm('signup'); });
    dom.toLoginLink.addEventListener('click', (e) => { e.preventDefault(); toggleAuthForm('login'); });
    
    // Forms submit
    dom.loginForm.addEventListener('submit', handleLogin);
    dom.signupForm.addEventListener('submit', handleSignup);
    dom.logoutBtn.addEventListener('click', logout);
    
    // Pagination controls
    dom.prevPageBtn.addEventListener('click', () => {
        if (state.pagination.page > 1) {
            state.pagination.page--;
            fetchFiles();
        }
    });
    
    dom.nextPageBtn.addEventListener('click', () => {
        state.pagination.page++;
        fetchFiles();
    });
    
    dom.limitSelect.addEventListener('change', (e) => {
        state.pagination.limit = parseInt(e.target.value);
        state.pagination.page = 1;
        fetchFiles();
    });
    
    // Selection events
    dom.selectAllCheckbox.addEventListener('change', (e) => {
        toggleSelectAll(e.target.checked);
    });
    
    dom.clearSelectionBtn.addEventListener('click', clearSelection);
    
    dom.actionSummaryBtn.addEventListener('click', () => {
        const selectedIds = Array.from(state.selectedIds);
        showToast(`Resumos integrados solicitados para arquivos IDs: ${selectedIds.join(', ')}.`, 'info');
    });
    
    // Local search filter
    dom.searchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        dom.filesListBody.innerHTML = '';
        renderFilesList();
    });
    
    // Drag and drop zone actions
    dom.dropZone.addEventListener('click', () => dom.fileInput.click());
    
    dom.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dom.dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dom.dropZone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dom.dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dom.dropZone.classList.remove('dragover');
        }, false);
    });
    
    dom.dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }, false);
}

// APP STARTUP
document.addEventListener('DOMContentLoaded', () => {
    initEvents();
    updateView();
});

/* =========================================================
   Papelaria SGC - Cliente JavaScript da API
   - Armazena tokens no localStorage
   - Adiciona automaticamente o header Authorization
   - Faz refresh transparente de token quando expirado
   ========================================================= */

const API = (() => {

    const KEY_ACCESS  = 'sgc_access';
    const KEY_REFRESH = 'sgc_refresh';
    const KEY_USER    = 'sgc_user';
    const BASE = '/api';

    // ---------- Storage ----------
    const setTokens = (access, refresh) => {
        if (access)  localStorage.setItem(KEY_ACCESS, access);
        if (refresh) localStorage.setItem(KEY_REFRESH, refresh);
    };
    const setUser  = (u) => localStorage.setItem(KEY_USER, JSON.stringify(u));
    const getAccess  = () => localStorage.getItem(KEY_ACCESS);
    const getRefresh = () => localStorage.getItem(KEY_REFRESH);
    const getUser    = () => {
        try { return JSON.parse(localStorage.getItem(KEY_USER)); }
        catch { return null; }
    };
    const isAuthenticated = () => !!getAccess();
    const isAdmin = () => (getUser() || {}).perfil === 'ADMIN';

    const clear = () => {
        localStorage.removeItem(KEY_ACCESS);
        localStorage.removeItem(KEY_REFRESH);
        localStorage.removeItem(KEY_USER);
    };

    // ---------- Núcleo HTTP ----------
    async function http(path, { method='GET', body=null, isRetry=false } = {}) {
        const headers = { 'Content-Type': 'application/json' };
        const token = getAccess();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const res = await fetch(`${BASE}${path}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });

        // Token expirado → tenta refresh uma vez
        if (res.status === 401 && !isRetry && getRefresh()) {
            const ok = await refresh();
            if (ok) return http(path, { method, body, isRetry: true });
            clear();
            window.location.href = '/login/';
            return Promise.reject('Sessão expirada.');
        }

        if (res.status === 204) return null;

        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            const erro = data.erro || data.detail
                          || `Erro HTTP ${res.status}`;
            const e = new Error(erro);
            e.status = res.status; e.data = data;
            throw e;
        }
        return data;
    }

    async function refresh() {
        try {
            const res = await fetch(`${BASE}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: getRefresh() }),
            });
            if (!res.ok) return false;
            const data = await res.json();
            setTokens(data.access, data.refresh);
            return true;
        } catch { return false; }
    }

    // ---------- Auth ----------
    async function login(username, password) {
        const data = await http('/auth/login/', {
            method: 'POST',
            body: { username, password },
        });
        setTokens(data.access, data.refresh);
        if (data.usuario) setUser(data.usuario);
        return data;
    }

    async function logout() {
        const refresh = getRefresh();
        try {
            if (refresh) await http('/auth/logout/',
                { method: 'POST', body: { refresh } });
        } catch { /* ignora */ }
        clear();
        window.location.href = '/login/';
    }

    // ---------- Endpoints ----------
    const clientes = {
        listar:    (busca) => http(`/clientes/${busca ? `?busca=${encodeURIComponent(busca)}` : ''}`),
        obter:     (id)    => http(`/clientes/${id}/`),
        criar:     (d)     => http('/clientes/', { method: 'POST', body: d }),
        atualizar: (id, d) => http(`/clientes/${id}/`, { method: 'PUT', body: d }),
        remover:   (id)    => http(`/clientes/${id}/`, { method: 'DELETE' }),
    };

    const produtos = {
        listar:    (busca) => http(`/produtos/${busca ? `?busca=${encodeURIComponent(busca)}` : ''}`),
        obter:     (id)    => http(`/produtos/${id}/`),
        criar:     (d)     => http('/produtos/', { method: 'POST', body: d }),
        atualizar: (id, d) => http(`/produtos/${id}/`, { method: 'PUT', body: d }),
        remover:   (id)    => http(`/produtos/${id}/`, { method: 'DELETE' }),
        estoqueBaixo: ()   => http('/produtos/estoque-baixo/'),
    };

    const vendas = {
        listar:    (filtros = {}) => {
            const qs = new URLSearchParams(filtros).toString();
            return http(`/vendas/${qs ? `?${qs}` : ''}`);
        },
        obter:     (id) => http(`/vendas/${id}/`),
        criar:     (d)  => http('/vendas/', { method: 'POST', body: d }),
        cancelar:  (id) => http(`/vendas/${id}/cancelar/`, { method: 'POST' }),
        porPeriodo: (di, df) => http('/vendas/por-periodo/',
            { method: 'POST', body: { data_inicio: di, data_fim: df } }),
    };

    const relatorios = {
        porPeriodo: (di, df) => http('/relatorios/por-periodo/',
            { method: 'POST', body: { data_inicio: di, data_fim: df } }),
        porCliente: (id) => http(`/relatorios/por-cliente/${id}/`),
        anual:      (ano) => http(`/relatorios/anual/?ano=${ano}`),
        topProdutos:(n=10) => http(`/relatorios/top-produtos/?limite=${n}`),
    };

    return {
        login, logout, isAuthenticated, isAdmin, getUser,
        clientes, produtos, vendas, relatorios,
    };
})();

// ---------- Helpers globais ----------
function toast(msg, type='success') {
    const cont = document.querySelector('.toast-container') ||
        (() => {
            const c = document.createElement('div');
            c.className = 'toast-container';
            document.body.appendChild(c);
            return c;
        })();
    const cls = { success: 'bg-success', danger: 'bg-danger',
                  warning: 'bg-warning text-dark', info: 'bg-primary' }[type] || 'bg-primary';
    const el = document.createElement('div');
    el.className = `toast align-items-center text-white ${cls} border-0 show`;
    el.role = 'alert';
    el.innerHTML = `<div class="d-flex">
        <div class="toast-body">${msg}</div>
        <button class="btn-close btn-close-white me-2 m-auto"
                onclick="this.closest('.toast').remove()"></button></div>`;
    cont.appendChild(el);
    setTimeout(() => el.remove(), 4000);
}

function confirma(msg) { return window.confirm(msg); }
function formatarBRL(v) {
    return Number(v).toLocaleString('pt-BR',
        { style: 'currency', currency: 'BRL' });
}
function formatarData(d) {
    if (!d) return '-';
    const dt = new Date(d);
    return dt.toLocaleString('pt-BR');
}

// Redirect automático se não autenticado em páginas protegidas
function exigeLogin() {
    if (!API.isAuthenticated()) window.location.href = '/login/';
}
function exigeAdmin() {
    if (!API.isAdmin()) {
        toast('Acesso restrito a administradores.', 'danger');
        setTimeout(() => window.location.href = '/dashboard/', 1500);
    }
}

// static/js/script.js
const API_BASE = window.location.origin || "http://127.0.0.1:5005";

function saveToken(t){ localStorage.setItem("access_token", t); }
function getToken(){ return localStorage.getItem("access_token"); }
function removeToken(){ localStorage.removeItem("access_token"); }
function saveName(n){ localStorage.setItem("login_name", n); }
function getName(){ return localStorage.getItem("login_name"); }

function showAlert(msg){ alert(msg); }
function setDebug(msg){
  const el = document.getElementById("debugArea");
  if(el) el.textContent = msg;
}

/* ---------- REGISTER ---------- */
async function handleRegister(e){
  e.preventDefault();
  const nama = document.getElementById("nama").value.trim();
  const password = document.getElementById("password").value;
  if(!nama || !password){ showAlert("Nama & password wajib"); return; }
  try{
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ nama, password })
    });
    const data = await res.json().catch(()=>null);
    console.log("register", res.status, data);
    if(!res.ok){ showAlert(data?.msg || `Registrasi gagal (${res.status})`); return; }
    showAlert(data?.msg || "Registrasi berhasil");
    e.target.reset();
  }catch(err){ console.error(err); showAlert("Kesalahan jaringan saat registrasi"); }
}

/* ---------- LOGIN -> simpan token & redirect ke dashboard ---------- */
async function handleLogin(e){
  e.preventDefault();
  const nama = document.getElementById("loginNama").value.trim();
  const password = document.getElementById("loginPassword").value;
  if(!nama || !password){ showAlert("Nama & password wajib"); return; }

  try{
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ nama, password })
    });
    const data = await res.json().catch(()=>null);
    console.log("login", res.status, data);
    if(!res.ok){ showAlert(data?.msg || `Login gagal (${res.status})`); return; }
    const token = data?.access_token || data?.token;
    if(!token){ showAlert("Token tidak dikembalikan server"); return; }

    saveToken(token);
    saveName(nama);
    // redirect ke dashboard page (backend akan serve template)
    window.location.href = `${window.location.origin}/dashboard`;
  }catch(err){
    console.error(err);
    showAlert("Kesalahan jaringan saat login");
  }
}

/* ---------- HELPERS ---------- */
function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  return String(text).replace(/[&<>"']/g, function(m) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m];
  });
}

function buildRowHtml(u){
  return `
    <tr data-user-id="${u.id}">
      <td>${u.id ?? ""}</td>
      <td class="col-nama">${escapeHtml(u.nama ?? "")}</td>
      <td class="col-umur">${u.umur ?? ""}</td>
      <td class="col-alamat">${escapeHtml(u.alamat ?? "")}</td>
      <td>
        <button class="btn btn-secondary btn-sm btn-edit" data-id="${u.id}">Edit</button>
        <button class="btn btn-danger btn-sm btn-delete" data-id="${u.id}">Hapus</button>
      </td>
    </tr>
  `;
}

/* ---------- DASHBOARD: fetch users, delete ---------- */
async function fetchUsers(withAuth=true){
  const tbody = document.querySelector("#tabelUser tbody");
  if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Memuat…</td></tr>";

  const headers = {"Content-Type":"application/json"};
  if(withAuth){
    const token = getToken();
    if(!token){ showAlert("Token tidak ditemukan. Silakan login lagi."); if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Tidak ada token</td></tr>"; return; }
    headers["Authorization"] = "Bearer " + token;
  }

  try{
    const res = await fetch(`${API_BASE}/api/users`, { method: "GET", headers });
    const data = await res.json().catch(()=>null);
    console.log("fetch users", res.status, data);
    if(!res.ok){ const msg = data?.msg || `Gagal (${res.status})`; if(tbody) tbody.innerHTML = `<tr><td colspan='5'>${msg}</td></tr>`; setDebug(msg); return; }
    const users = Array.isArray(data) ? data : (data?.users || []);
    if(!users.length){ if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Tidak ada data user.</td></tr>"; return; }

    if(tbody){
      tbody.innerHTML = users.map(u => buildRowHtml(u)).join("");
    }
    setDebug('Daftar user dimuat: ' + users.length);
  }catch(err){
    console.error("fetchUsers error", err);
    if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Kesalahan jaringan</td></tr>";
    setDebug("Kesalahan jaringan saat fetch users");
  }
}

async function deleteUser(id){
  if(!confirm(`Hapus user id=${id}?`)) return;
  const token = getToken();
  if(!token){ showAlert("Silakan login"); return; }
  try{
    const res = await fetch(`${API_BASE}/api/users/${id}`, {
      method: "DELETE",
      headers: { "Content-Type":"application/json", "Authorization":"Bearer " + token }
    });
    const data = await res.json().catch(()=>null);
    console.log("delete", res.status, data);
    if(!res.ok){ showAlert(data?.msg || `Gagal hapus (${res.status})`); setDebug(JSON.stringify(data)); return; }
    showAlert("User dihapus");
    fetchUsers(true);
  }catch(err){ console.error(err); showAlert("Kesalahan jaringan saat hapus"); }
}

/* ---------- EDIT: get single user, update ---------- */
async function getUser(id){
  const headers = {"Content-Type":"application/json"};
  const token = getToken();
  if(token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(`${API_BASE}/api/users/${id}`, { method: "GET", headers });
  if(!res.ok){
    const txt = await res.text().catch(()=>null);
    throw new Error(`Gagal ambil user (${res.status}) ${txt||''}`);
  }
  return await res.json();
}

async function updateUserApi(id, payload){
  const headers = {"Content-Type":"application/json"};
  const token = getToken();
  if(token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(`${API_BASE}/api/users/${id}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload)
  });
  const data = await res.json().catch(()=>null);
  if(!res.ok) throw new Error(data?.msg || data?.error || `Gagal update (${res.status})`);
  return data;
}

/* ---------- Generic init to hook forms/buttons on both pages ---------- */
document.addEventListener("DOMContentLoaded", ()=>{
  // register page
  const reg = document.getElementById("registerForm");
  if(reg) reg.addEventListener("submit", handleRegister);

  // login page
  const login = document.getElementById("loginForm");
  if(login) login.addEventListener("submit", handleLogin);

  // dashboard page buttons
  const getBtn = document.getElementById("getUsers");
  if(getBtn) getBtn.addEventListener("click", ()=>fetchUsers(true));
  const getBtnNo = document.getElementById("getUsersNoAuth");
  if(getBtnNo) getBtnNo.addEventListener("click", ()=>fetchUsers(false));

  const logoutBtn = document.getElementById("logoutBtn");
  if(logoutBtn) logoutBtn.addEventListener("click", ()=>{
    removeToken(); localStorage.removeItem("login_name"); window.location.href = "/";
  });

  // delegated table events (edit, delete) - supports server-side rendered rows or dynamic rows
  const tbody = document.querySelector("#tabelUser tbody");
  if(tbody){
    tbody.addEventListener("click", async (ev)=>{
      // Edit button (class btn-edit)
      const editBtn = ev.target.closest(".btn-edit");
      if(editBtn){
        const id = editBtn.dataset.id;
        if(!id) return;
        try{
          const data = await getUser(id);
          const user = data.user ?? data;
          document.getElementById("editUserId").value = user.id;
          document.getElementById("editNama").value = user.nama ?? "";
          document.getElementById("editUmur").value = user.umur ?? "";
          document.getElementById("editAlamat").value = user.alamat ?? "";
          const errEl = document.getElementById("editError");
          if(errEl){ errEl.style.display = "none"; errEl.textContent = ""; }

          // show bootstrap modal
          const editModalEl = document.getElementById('editUserModal');
          if(typeof bootstrap !== 'undefined' && editModalEl){
            const m = new bootstrap.Modal(editModalEl);
            m.show();
          }
        }catch(err){
          console.error("getUser error", err);
          setDebug(err.message || 'Gagal ambil user');
          showAlert("Gagal mengambil data user: " + (err.message || ""));
        }
        return;
      }

      // Delete button (support both btn-delete and btn-hapus)
      const delBtn = ev.target.closest(".btn-delete, .btn-hapus");
      if(delBtn){
        const id = delBtn.dataset.id;
        if(!id) return;
        deleteUser(id);
        return;
      }
    });
  }

  // handle submit edit form
  const editForm = document.getElementById("editUserForm");
  if(editForm){
    editForm.addEventListener("submit", async (ev)=>{
      ev.preventDefault();
      const id = document.getElementById("editUserId").value;
      const payload = {
        nama: document.getElementById("editNama").value.trim(),
        umur: document.getElementById("editUmur").value ? Number(document.getElementById("editUmur").value) : null,
        alamat: document.getElementById("editAlamat").value.trim()
      };

      if(!payload.nama){
        const errEl = document.getElementById("editError");
        if(errEl){ errEl.textContent = "Nama wajib diisi."; errEl.style.display = "block"; }
        return;
      }

      try{
        const result = await updateUserApi(id, payload);
        // update row in DOM: try classes first, otherwise fallback to td indices
        const tr = document.querySelector(`tr[data-user-id="${id}"]`);
        if(tr){
          const namaCell = tr.querySelector('.col-nama');
          const umurCell = tr.querySelector('.col-umur');
          const alamatCell = tr.querySelector('.col-alamat');

          if(namaCell) namaCell.textContent = payload.nama;
          if(umurCell) umurCell.textContent = payload.umur ?? "";
          if(alamatCell) alamatCell.textContent = payload.alamat;
          // fallback: try index-based
          if(!namaCell || !umurCell || !alamatCell){
            const tds = tr.querySelectorAll('td');
            if(tds.length >= 4){
              if(!namaCell) tds[1].textContent = payload.nama;
              if(!umurCell) tds[2].textContent = payload.umur ?? "";
              if(!alamatCell) tds[3].textContent = payload.alamat;
            }
          }
        } else {
          // if no row found, fallback: refetch
          fetchUsers(true);
        }

        // hide modal
        const editModalEl = document.getElementById('editUserModal');
        if(typeof bootstrap !== 'undefined' && editModalEl){
          const inst = bootstrap.Modal.getInstance(editModalEl) || new bootstrap.Modal(editModalEl);
          inst.hide();
        }

        setDebug('User berhasil diperbarui.');
        showAlert(result?.msg || 'Perubahan disimpan');
      }catch(err){
        console.error("update error", err);
        const errEl = document.getElementById("editError");
        if(errEl){ errEl.textContent = err.message || 'Gagal memperbarui'; errEl.style.display = "block"; }
        setDebug(err.message || 'Gagal update');
      }
    });
  }

  // on dashboard load: set header & auto fetch
  if(window.location.pathname === "/dashboard"){
    const nameEl = document.getElementById("welcomeName");
    const tokenEl = document.getElementById("tokenShort");
    if(nameEl) nameEl.textContent = getName() || "";
    const token = getToken();
    if(token && tokenEl) tokenEl.textContent = "Bearer " + token.slice(0,40) + "…";
    // auto fetch
    fetchUsers(Boolean(token));
  }
});

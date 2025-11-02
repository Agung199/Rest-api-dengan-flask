// static/js/script.js
const API_BASE = window.location.origin || "http://127.0.0.1:5005";

function showAlert(msg) { alert(msg); }
function saveToken(t){ localStorage.setItem("access_token", t); }
function getToken(){ return localStorage.getItem("access_token"); }
function removeToken(){ localStorage.removeItem("access_token"); }

// tampilkan token di tokenBox (opsional)
function updateTokenUI(){
  const box = document.getElementById("tokenBox");
  const logoutBtn = document.getElementById("logoutBtn");
  const token = getToken();
  if(box){
    if(token){ box.style.display = "block"; box.textContent = "Bearer " + token.slice(0,40) + "…"; }
    else { box.style.display = "none"; box.textContent = ""; }
  }
  if(logoutBtn) logoutBtn.style.display = token ? "inline-block" : "none";
}

/* REGISTER & LOGIN (safety: check response and log) */
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
    console.log("register response:", res.status, data);
    if(!res.ok) { showAlert(data?.msg || `Registrasi gagal (${res.status})`); return; }
    showAlert(data?.msg || "Registrasi berhasil");
    e.target.reset();
  }catch(err){ console.error("register error:", err); showAlert("Error jaringan"); }
}

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
    console.log("login response:", res.status, data);
    if(!res.ok){ showAlert(data?.msg || `Login gagal (${res.status})`); return; }
    // ambil token dari beberapa kemungkinan key
    const token = data?.access_token || data?.token || data?.accessToken || null;
    if(!token){ showAlert("Login sukses tapi token tidak ditemukan di response"); return; }
    saveToken(token);
    updateTokenUI();
    showAlert("Login berhasil");
    e.target.reset();
  }catch(err){ console.error("login error:", err); showAlert("Error jaringan login"); }
}

/* FETCH USERS and RENDER TABLE */
function clearTable(){
  const tbody = document.querySelector("#tabelUser tbody");
  if(tbody) tbody.innerHTML = "";
}
function renderUsersToTable(users){
  const tbody = document.querySelector("#tabelUser tbody");
  if(!tbody) return console.warn("tabelUser tbody tidak ditemukan");
  tbody.innerHTML = "";
  users.forEach(u=>{
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${u.id ?? ""}</td>
      <td>${u.nama ?? ""}</td>
      <td>${u.umur ?? ""}</td>
      <td>${u.alamat ?? ""}</td>
      <td>
        <button class="btn btn-sm btn-danger btn-delete" data-id="${u.id}">Hapus</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Fetch with (optional) token
async function fetchUsers(withAuth=true){
  const tbody = document.querySelector("#tabelUser tbody");
  if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Memuat…</td></tr>";

  const headers = {"Content-Type":"application/json"};
  if(withAuth){
    const token = getToken();
    if(!token){
      showAlert("Token tidak ada — login dulu atau klik tombol tanpa token");
      if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Tidak ada token.</td></tr>";
      return;
    }
    headers["Authorization"] = "Bearer " + token;
  }

  try{
    const res = await fetch(`${API_BASE}/api/users`, { method: "GET", headers });
    const data = await res.json().catch(()=>null);
    console.log("fetch users response:", res.status, data);
    if(!res.ok){
      // server mungkin mengembalikan {msg: "..."} atau sesuatu
      const msg = data?.msg || `Gagal mengambil users (status ${res.status})`;
      if(tbody) tbody.innerHTML = `<tr><td colspan='5'>${msg}</td></tr>`;
      showAlert(msg);
      return;
    }
    // server bisa mengembalikan array langsung atau {users:[...]}
    const users = Array.isArray(data) ? data : (data?.users || []);
    if(!users.length) {
      if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Tidak ada data user.</td></tr>";
      return;
    }
    renderUsersToTable(users);
  }catch(err){
    console.error("fetchUsers error:", err);
    if(tbody) tbody.innerHTML = "<tr><td colspan='5'>Kesalahan jaringan.</td></tr>";
    showAlert("Kesalahan jaringan saat memuat data user.");
  }
}

/* DELETE USER (per-row) */
async function deleteUser(id){
  if(!confirm(`Hapus user id=${id}?`)) return;
  const token = getToken();
  if(!token){ showAlert("Login diperlukan untuk menghapus"); return; }

  try{
    const res = await fetch(`${API_BASE}/api/users/${id}`, {
      method: "DELETE",
      headers: { "Content-Type":"application/json", "Authorization":"Bearer " + token }
    });
    const data = await res.json().catch(()=>null);
    console.log("delete response:", res.status, data);
    if(!res.ok){ showAlert(data?.msg || `Gagal hapus (status ${res.status})`); return; }
    showAlert("User dihapus");
    fetchUsers(true);
  }catch(err){ console.error("delete error:", err); showAlert("Kesalahan jaringan saat hapus"); }
}

/* Hook up events */
document.addEventListener("DOMContentLoaded", ()=>{
  // forms
  const reg = document.getElementById("registerForm");
  if(reg) reg.addEventListener("submit", handleRegister);

  const login = document.getElementById("loginForm");
  if(login) login.addEventListener("submit", handleLogin);

  // show users buttons
  const btn = document.getElementById("getUsers");
  if(btn) btn.addEventListener("click", ()=>fetchUsers(true));

  const btnNo = document.getElementById("getUsersNoAuth");
  if(btnNo) btnNo.addEventListener("click", ()=>fetchUsers(false));

  // logout button
  const logoutBtn = document.getElementById("logoutBtn");
  if(logoutBtn) logoutBtn.addEventListener("click", ()=>{ removeToken(); updateTokenUI(); showAlert("Logout"); });

  // delegate delete button pada tbody
  const tbody = document.querySelector("#tabelUser tbody");
  if(tbody){
    tbody.addEventListener("click", (ev)=>{
      const btn = ev.target.closest(".btn-delete");
      if(!btn) return;
      const id = btn.dataset.id;
      deleteUser(id);
    });
  }

  updateTokenUI();
});

const API_AUTH = "http://<IP_PUBLICA_EC2>:8001/api/v1";
const API_RESIDENTS = "http://<IP_PUBLICA_EC2>:8002/api/v1";
const API_PAYMENTS = "http://<IP_PUBLICA_EC2>:8003/api/v1";

let currentUser = null;
let selectedReceipts = [];

function showSection(sectionId) {
    document.querySelectorAll('main > section').forEach(s => s.classList.add('hidden'));
    document.getElementById(sectionId).classList.remove('hidden');
}

function togglePasswordVisibility() {
    const passInput = document.getElementById('login-pass');
    passInput.type = passInput.type === 'password' ? 'text' : 'password';
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-user').value;
    const password = document.getElementById('login-pass').value;

    try {
        const response = await fetch(`${API_AUTH}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username_or_email: username, password: password })
        });

        const data = await response.json();
        if (response.ok) {
            currentUser = data.user;
            document.getElementById('user-session').innerHTML = `
                <span>Bienvenido, <strong>${currentUser.full_name}</strong> (${currentUser.role})</span>
                <button onclick="logout()" class="btn-secondary">Cerrar Sesión</button>
            `;
            alert(`Acceso correcto. Bienvenido ${currentUser.full_name}`);
            if (currentUser.role === 'Residente') {
                loadReceipts(currentUser.id);
                showSection('payments-section');
            } else {
                showSection('home-section');
            }
        } else {
            alert(data.detail || 'Error en las credenciales');
        }
    } catch (err) {
        alert('Error conectando al servidor de autenticación');
    }
});

async function loadReceipts(residentId) {
    const res = await fetch(`${API_PAYMENTS}/receipts/${residentId}`);
    const receipts = await res.json();
    const container = document.getElementById('receipts-list');
    container.innerHTML = '';

    receipts.forEach(r => {
        container.innerHTML += `
            <div class="receipt-item">
                <input type="checkbox" value="${r.id}" data-amount="${r.total}" onchange="updateTotal()">
                <div>
                    <strong>Periodo: ${r.period}</strong> - Vence: ${r.due_date}<br>
                    <small>Ordinario: S/${r.ordinary} | Reserva: S/${r.reserve_fund} | Multa: S/${r.fine}</small>
                </div>
                <div><strong>S/ ${r.total.toFixed(2)}</strong></div>
            </div>
        `;
    });
}

function updateTotal() {
    let total = 0;
    selectedReceipts = [];
    document.querySelectorAll('#receipts-list input[type="checkbox"]:checked').forEach(cb => {
        total += parseFloat(cb.getAttribute('data-amount'));
        selectedReceipts.push(parseInt(cb.value));
    });
    document.getElementById('total-to-pay').innerText = total.toFixed(2);
}

function logout() {
    currentUser = null;
    window.location.reload();
}
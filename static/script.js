// === Cierre de mensajes flash después de unos segundos ===
document.addEventListener('DOMContentLoaded', () => {
  const flashMessages = document.querySelectorAll('.message');
  flashMessages.forEach(msg => {
    setTimeout(() => {
      msg.style.display = 'none';
    }, 4000); // se oculta luego de 4 segundos
  });
});

// === Confirmar eliminación ===
function confirmarEliminacion(nombreItem) {
  return confirm(`¿Estás seguro de eliminar el ítem "${nombreItem}"? Esta acción no se puede deshacer.`);
}
let selectedMethod = '';

function openDonationModal() {
  document.getElementById('donationModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function closeDonationModal() {
  document.getElementById('donationModal').style.display = 'none';
  document.body.style.overflow = 'auto';
  selectedMethod = '';
  const cards = document.querySelectorAll('.donation-method');
  cards.forEach(card => card.classList.remove('selected'));
}

function selectMethod(method) {
  selectedMethod = method;

  const cards = document.querySelectorAll('.donation-method');
  cards.forEach(card => card.classList.remove('selected'));

  event.target.closest('.donation-method').classList.add('selected');
}

function getQRImageUrl(method) {
  const urls = {
    'yape': '/static/images/qr-yape.png',
    'plin': '/static/images/qr-plin.png'
  };
  return urls[method] || '';
}

function getMethodName(method) {
  const names = {
    'yape': 'Yape',
    'plin': 'Plin',
    'bcp': 'BCP',
    'interbank': 'Interbank',
    'bbva': 'BBVA',
    'efectivo': 'Efectivo'
  };
  return names[method] || method;
}

function processDonation() {
  if (!selectedMethod) {
    alert('Por favor selecciona un método de pago.');
    return;
  }

  let message = `Método seleccionado: ${getMethodName(selectedMethod)}\n\n`;

  switch (selectedMethod) {
    case 'yape':
    case 'plin':
      message += `1. Abre tu app ${getMethodName(selectedMethod)}\n`;
      message += `2. Escanea el código QR o usa el número: 958-685-460\n`;
      message += `3. Ingresa el monto y escribe "Donación Iglesia Shaddai"\n`;
      showQRModal(message, getQRImageUrl(selectedMethod));
      break;
    case 'bcp':
      message += '1. Cuenta BCP: 2157534935605 \n2. A nombre de: Iglesia Bautista Shaddai\n';
      message += '3. Ingresa el monto y en concepto: "Donación"';
      alert(message);
      break;
    case 'interbank':
      message += '1. Cuenta Interbank: 3003363171209\n2. A nombre de: Iglesia Bautista Shaddai\n';
      message += '3. Ingresa el monto y en concepto: "Donación"';
      alert(message);
      break;
    case 'bbva':
      message += '1. Cuenta BBVA: 456-78912345-6-78\n2. A nombre de: Iglesia Bautista Shaddai\n';
      message += '3. Ingresa el monto y en concepto: "Donación"';
      alert(message);
      break;
    case 'efectivo':
      message += '1. Puedes entregar tu donación durante los servicios\n';
      message += '2. O depositarla en las urnas de ofrenda';
      alert(message);
      break;
  }

  closeDonationModal();
}

// Modal QR personalizado
function showQRModal(message, qrUrl) {
  const existing = document.getElementById('qrModal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'qrModal';
  modal.className = 'modal';
  modal.style.display = 'block';

  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h2>Gracias por tu Donación 🙏</h2>
        <button class="close-btn" onclick="closeQRModal()">×</button>
      </div>
      <div class="modal-body" style="text-align: center;">
        ${qrUrl ? `<img src="${qrUrl}" style="max-width: 250px; margin-bottom: 1rem;" alt="Código QR">` : ''}
        <pre style="text-align: left; white-space: pre-wrap;">${message}</pre>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" onclick="closeQRModal()">Cerrar</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  document.body.style.overflow = 'hidden';
}

function closeQRModal() {
  const modal = document.getElementById('qrModal');
  if (modal) {
    modal.remove();
    document.body.style.overflow = 'auto';
  }
}
// === Cargar estadísticas ===
function cargarEstadisticas() {
  fetch('/api/estadisticas')
    .then(response => response.json())
    .then(data => {
      const statsDiv = document.getElementById('stats');
      if (!statsDiv) return;

      statsDiv.innerHTML = `
        <h3>Total de Ítems: ${data.gran_total_cantidad_items || 'N/A'}</h3>
        <h3>Valor Total: S/ ${data.gran_total_valor?.toFixed(2) || '0.00'}</h3>
        <p>Categorías activas: ${data.total_categorias_activas || 0}</p>
      `;
    })
    .catch(error => {
      console.error('Error al cargar estadísticas:', error);
    });
}

// Llamar automáticamente si la página tiene el div con id "stats"
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('stats')) {
    cargarEstadisticas();
  }
});

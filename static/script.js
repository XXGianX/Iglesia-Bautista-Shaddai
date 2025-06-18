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
    resetSelection();
}

function selectMethod(method) {
    selectedMethod = method;
    document.querySelectorAll('.donation-method').forEach(card => {
        card.classList.remove('selected');
    });
    const selectedCard = event.target.closest('.donation-method');
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
}

function processDonation() {
    if (!selectedMethod) {
        alert('Por favor selecciona un método de pago.');
        return;
    }

    let message = `¡Gracias por tu donación mediante ${selectedMethod.toUpperCase()}! 🙌`;
    alert(message);
    closeDonationModal();
}

function resetSelection() {
    selectedMethod = '';
    document.querySelectorAll('.donation-method').forEach(card => {
        card.classList.remove('selected');
    });
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

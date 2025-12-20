document.addEventListener('DOMContentLoaded', () => {
    const fetchBtn = document.getElementById('fetchBtn');
    const statusMsg = document.getElementById('statusMsg');
    const manualBtn = document.getElementById('manualBtn');
    const manualModal = document.getElementById('manualModal');
    const closeBtn = document.querySelector('.close');
    const manualForm = document.getElementById('manualForm');
    const manualType = document.getElementById('manualType');
    const superInputGroup = document.getElementById('superInputGroup');

    // Fetch Data
    fetchBtn.addEventListener('click', async () => {
        statusMsg.textContent = 'Explorando la red...';
        fetchBtn.classList.add('disabled');

        try {
            const response = await fetch('/api/fetch-results', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                statusMsg.textContent = `¡Listo! ${data.message} Total: ${data.count} registros.`;
                statusMsg.style.color = '#4ade80'; // Green
            } else {
                statusMsg.textContent = 'Error: ' + data.message;
                statusMsg.style.color = '#ef4444'; // Red
            }
        } catch (error) {
            statusMsg.textContent = 'Error de conexión.';
        } finally {
            fetchBtn.classList.remove('disabled');
        }
    });

    // Generate Prediction
    window.generatePrediction = async (type) => {
        statusMsg.textContent = `Analizando patrones de ${type}...`;
        const container = type === 'baloto' ? document.getElementById('balotoResult') : document.getElementById('milotoResult');

        try {
            const response = await fetch(`/api/generate-${type}`);
            const data = await response.json();

            if (data.status === 'success') {
                renderBalls(container, data.prediction, type);
                statusMsg.textContent = '¡Combinación generada!';
            } else {
                statusMsg.textContent = data.message;
                statusMsg.style.color = '#ef4444';
            }
        } catch (error) {
            statusMsg.textContent = 'Error al generar.';
        }
    };

    function renderBalls(container, prediction, type) {
        container.innerHTML = '';

        // Main numbers
        prediction.numbers.forEach(num => {
            const ball = document.createElement('span');
            ball.className = 'ball';
            ball.textContent = num;
            container.appendChild(ball);
        });

        // Super Ball (for Baloto)
        if (type === 'baloto' && prediction.super_balota) {
            const superBall = document.createElement('span');
            superBall.className = 'super-ball';
            superBall.textContent = prediction.super_balota;
            container.appendChild(superBall);
        }
    }

    // Modal Logic
    manualBtn.onclick = () => manualModal.style.display = 'block';
    closeBtn.onclick = () => manualModal.style.display = 'none';
    window.onclick = (event) => {
        if (event.target == manualModal) manualModal.style.display = 'none';
    }

    manualType.onchange = () => {
        superInputGroup.style.display = manualType.value === 'baloto' ? 'block' : 'none';
    }

    manualForm.onsubmit = async (e) => {
        e.preventDefault();
        const type = manualType.value;
        const numbersStr = document.getElementById('manualNumbers').value;
        const numbers = numbersStr.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));

        const payload = {
            type: type,
            date: document.getElementById('manualDate').value,
            numbers: numbers
        };

        if (type === 'baloto') {
            payload.super_balota = parseInt(document.getElementById('manualSuper').value);
        }

        try {
            const response = await fetch('/api/add-manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (data.status === 'success') {
                alert('Guardado exitosamente');
                manualModal.style.display = 'none';
                manualForm.reset();
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Error enviando datos');
        }
    }
});

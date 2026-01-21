document.addEventListener('DOMContentLoaded', () => {
    const fetchBtn = document.getElementById('fetchBtn');
    const statusMsg = document.getElementById('statusMsg');
    const manualBtn = document.getElementById('manualBtn');
    const manualModal = document.getElementById('manualModal');
    const closeBtn = document.querySelector('.close');
    const manualForm = document.getElementById('manualForm');
    const manualType = document.getElementById('manualType');
    const superInputGroup = document.getElementById('superInputGroup');

    // Chart instances
    let frequencyChart = null;
    let gapsChart = null;
    let sumChart = null;
    let pairsChart = null;
    let superChart = null;

    // Current selected game for predictive tab
    let currentGame = 'baloto';

    // ============================================
    // TAB NAVIGATION
    // ============================================
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            // Update active states
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `tab-${tabId}`) {
                    content.classList.add('active');
                }
            });

            // Load predictive data when switching to that tab
            if (tabId === 'predictive') {
                loadPredictiveData(currentGame);
            }
        });
    });

    // ============================================
    // GAME SELECTOR (Predictive Tab)
    // ============================================
    const gameBtns = document.querySelectorAll('.game-btn');
    
    gameBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const game = btn.dataset.game;
            currentGame = game;
            
            gameBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle baloto-only elements
            const chartsContainer = document.querySelector('.charts-container');
            if (game === 'miloto') {
                chartsContainer.classList.add('miloto-mode');
            } else {
                chartsContainer.classList.remove('miloto-mode');
            }
            
            loadPredictiveData(game);
        });
    });

    // ============================================
    // FETCH DATA
    // ============================================
    fetchBtn.addEventListener('click', async () => {
        statusMsg.textContent = 'Explorando la red...';
        statusMsg.style.color = '#8b5cf6';
        fetchBtn.classList.add('disabled');

        try {
            const response = await fetch('/api/fetch-results', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                statusMsg.textContent = `¡Listo! ${data.message} Total: ${data.count} registros.`;
                statusMsg.style.color = '#4ade80';
                
                // Refresh predictive data if on that tab
                const predictiveTab = document.getElementById('tab-predictive');
                if (predictiveTab.classList.contains('active')) {
                    loadPredictiveData(currentGame);
                }
            } else {
                statusMsg.textContent = 'Error: ' + data.message;
                statusMsg.style.color = '#ef4444';
            }
        } catch (error) {
            statusMsg.textContent = 'Error de conexión.';
            statusMsg.style.color = '#ef4444';
        } finally {
            fetchBtn.classList.remove('disabled');
        }
    });

    // ============================================
    // GENERATE PREDICTION
    // ============================================
    window.generatePrediction = async (type) => {
        statusMsg.textContent = `Analizando patrones de ${type}...`;
        statusMsg.style.color = '#8b5cf6';
        const container = type === 'baloto' ? document.getElementById('balotoResult') : document.getElementById('milotoResult');

        try {
            const response = await fetch(`/api/generate-${type}`);
            const data = await response.json();

            if (data.status === 'success') {
                renderBalls(container, data.prediction, type);
                statusMsg.textContent = '¡Combinación generada!';
                statusMsg.style.color = '#4ade80';
            } else {
                statusMsg.textContent = data.message;
                statusMsg.style.color = '#ef4444';
            }
        } catch (error) {
            statusMsg.textContent = 'Error al generar.';
            statusMsg.style.color = '#ef4444';
        }
    };

    function renderBalls(container, prediction, type) {
        container.innerHTML = '';

        prediction.numbers.forEach(num => {
            const ball = document.createElement('span');
            ball.className = 'ball';
            ball.textContent = num;
            container.appendChild(ball);
        });

        if (type === 'baloto' && prediction.super_balota) {
            const superBall = document.createElement('span');
            superBall.className = 'super-ball';
            superBall.textContent = prediction.super_balota;
            container.appendChild(superBall);
        }
    }

    // ============================================
    // MODAL LOGIC
    // ============================================
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

    // ============================================
    // PREDICTIVE ANALYTICS
    // ============================================
    async function loadPredictiveData(gameType) {
        try {
            statusMsg.textContent = `Cargando análisis predictivo para ${gameType}...`;
            statusMsg.style.color = '#8b5cf6';

            const response = await fetch(`/api/predictive/${gameType}`);
            const result = await response.json();

            if (result.status === 'success') {
                const data = result.data;
                
                renderFrequencyChart(data.frequency_chart, gameType);
                renderHotColdNumbers(data.hot_cold);
                renderGapsChart(data.gaps);
                renderTrends(data.trends);
                renderSumDistribution(data.sum_distribution);
                renderPairsChart(data.pairs);
                renderPositionAnalysis(data.position_analysis);
                
                if (gameType === 'baloto' && data.super_analysis) {
                    renderSuperChart(data.super_analysis);
                }
                
                renderPredictionSummary(data, gameType);
                
                statusMsg.textContent = `Análisis de ${gameType} cargado (${data.total_draws} sorteos)`;
                statusMsg.style.color = '#4ade80';
            } else {
                statusMsg.textContent = result.message;
                statusMsg.style.color = '#ef4444';
            }
        } catch (error) {
            console.error('Error loading predictive data:', error);
            statusMsg.textContent = 'Error cargando datos predictivos';
            statusMsg.style.color = '#ef4444';
        }
    }

    // ============================================
    // CHART RENDERING FUNCTIONS
    // ============================================

    function renderFrequencyChart(freqData, gameType) {
        const ctx = document.getElementById('frequencyChart').getContext('2d');
        const maxNum = gameType === 'baloto' ? 43 : 39;
        
        const labels = [];
        const values = [];
        const colors = [];
        
        // Calculate average for coloring
        const freqValues = Object.values(freqData.numbers);
        const avgFreq = freqValues.length > 0 ? freqValues.reduce((a, b) => a + b, 0) / freqValues.length : 0;
        
        for (let i = 1; i <= maxNum; i++) {
            labels.push(i);
            const freq = freqData.numbers[i] || 0;
            values.push(freq);
            
            // Color based on frequency
            if (freq > avgFreq * 1.3) {
                colors.push('rgba(239, 68, 68, 0.8)'); // Hot - Red
            } else if (freq < avgFreq * 0.7) {
                colors.push('rgba(59, 130, 246, 0.8)'); // Cold - Blue
            } else {
                colors.push('rgba(99, 102, 241, 0.8)'); // Normal - Purple
            }
        }

        if (frequencyChart) {
            frequencyChart.destroy();
        }

        frequencyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Frecuencia',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `Apariciones: ${context.raw}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            maxRotation: 0
                        }
                    }
                }
            }
        });
    }

    function renderHotColdNumbers(hotColdData) {
        const hotList = document.getElementById('hotNumbersList');
        const coldList = document.getElementById('coldNumbersList');
        
        hotList.innerHTML = '';
        coldList.innerHTML = '';
        
        hotColdData.hot.forEach(item => {
            const div = document.createElement('div');
            div.className = 'number-item hot';
            div.innerHTML = `
                <span class="num">${item.number}</span>
                <span class="freq">${item.frequency}x</span>
            `;
            hotList.appendChild(div);
        });
        
        hotColdData.cold.forEach(item => {
            const div = document.createElement('div');
            div.className = 'number-item cold';
            div.innerHTML = `
                <span class="num">${item.number}</span>
                <span class="freq">${item.frequency}x</span>
            `;
            coldList.appendChild(div);
        });
    }

    function renderGapsChart(gapsData) {
        const ctx = document.getElementById('gapsChart').getContext('2d');
        
        // Get top 15 overdue numbers
        const topGaps = gapsData.slice(0, 15);
        
        const labels = topGaps.map(g => g.number);
        const values = topGaps.map(g => g.gap);

        if (gapsChart) {
            gapsChart.destroy();
        }

        gapsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sorteos sin aparecer',
                    data: values,
                    backgroundColor: 'rgba(245, 158, 11, 0.7)',
                    borderColor: 'rgba(245, 158, 11, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    function renderTrends(trendsData) {
        const upList = document.getElementById('trendingUpList');
        const downList = document.getElementById('trendingDownList');
        
        upList.innerHTML = '';
        downList.innerHTML = '';
        
        trendsData.trending_up.slice(0, 5).forEach(item => {
            const div = document.createElement('div');
            div.className = 'trend-item';
            div.innerHTML = `
                <span class="num">#${item.number}</span>
                <span class="change up">+${item.change_pct}%</span>
            `;
            upList.appendChild(div);
        });
        
        trendsData.trending_down.slice(0, 5).forEach(item => {
            const div = document.createElement('div');
            div.className = 'trend-item';
            div.innerHTML = `
                <span class="num">#${item.number}</span>
                <span class="change down">${item.change_pct}%</span>
            `;
            downList.appendChild(div);
        });
    }

    function renderSumDistribution(sumData) {
        const ctx = document.getElementById('sumChart').getContext('2d');
        const statsContainer = document.getElementById('sumStats');
        
        const labels = sumData.distribution.map(d => `${d.range_start}-${d.range_end}`);
        const values = sumData.distribution.map(d => d.count);

        if (sumChart) {
            sumChart.destroy();
        }

        sumChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Frecuencia',
                    data: values,
                    fill: true,
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(99, 102, 241, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            maxRotation: 45
                        }
                    }
                }
            }
        });

        // Render stats
        statsContainer.innerHTML = `
            <div class="sum-stat">
                <span class="label">Promedio</span>
                <span class="value">${sumData.average}</span>
            </div>
            <div class="sum-stat">
                <span class="label">Mínimo</span>
                <span class="value">${sumData.min}</span>
            </div>
            <div class="sum-stat">
                <span class="label">Máximo</span>
                <span class="value">${sumData.max}</span>
            </div>
            <div class="sum-stat">
                <span class="label">Rango Recomendado</span>
                <span class="value recommended">${sumData.recommended_range.low} - ${sumData.recommended_range.high}</span>
            </div>
        `;
    }

    function renderPairsChart(pairsData) {
        const ctx = document.getElementById('pairsChart').getContext('2d');
        
        const topPairs = pairsData.slice(0, 10);
        const labels = topPairs.map(p => `${p.pair[0]}-${p.pair[1]}`);
        const values = topPairs.map(p => p.frequency);

        if (pairsChart) {
            pairsChart.destroy();
        }

        pairsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(74, 222, 128, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(20, 184, 166, 0.8)',
                        'rgba(168, 85, 247, 0.8)',
                        'rgba(251, 146, 60, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#94a3b8',
                            padding: 10,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.raw} veces`
                        }
                    }
                }
            }
        });
    }

    function renderPositionAnalysis(positionData) {
        const container = document.getElementById('positionAnalysis');
        container.innerHTML = '';
        
        positionData.forEach(pos => {
            const column = document.createElement('div');
            column.className = 'position-column';
            
            let numbersHtml = '';
            pos.top_numbers.forEach(num => {
                numbersHtml += `
                    <div class="pos-num">
                        <span class="number">${num.number}</span>
                        <span class="count">${num.frequency}x</span>
                    </div>
                `;
            });
            
            column.innerHTML = `
                <h5>Posición ${pos.position}</h5>
                <div class="position-numbers">
                    ${numbersHtml}
                </div>
            `;
            
            container.appendChild(column);
        });
    }

    function renderSuperChart(superData) {
        const ctx = document.getElementById('superChart').getContext('2d');
        
        const labels = [];
        const values = [];
        const colors = [];
        
        // Calculate average
        const freqValues = superData.frequencies.map(f => f.frequency);
        const avgFreq = freqValues.length > 0 ? freqValues.reduce((a, b) => a + b, 0) / freqValues.length : 0;
        
        for (let i = 1; i <= 16; i++) {
            labels.push(i);
            const item = superData.frequencies.find(f => f.number === i);
            const freq = item ? item.frequency : 0;
            values.push(freq);
            
            if (freq > avgFreq * 1.2) {
                colors.push('rgba(236, 72, 153, 0.8)');
            } else if (freq < avgFreq * 0.8) {
                colors.push('rgba(59, 130, 246, 0.8)');
            } else {
                colors.push('rgba(139, 92, 246, 0.8)');
            }
        }

        if (superChart) {
            superChart.destroy();
        }

        superChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Frecuencia Super Balota',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    function renderPredictionSummary(data, gameType) {
        const container = document.getElementById('predictionSummary');
        
        // Get recommended numbers based on analysis
        const hotNumbers = data.hot_cold.hot.slice(0, 3).map(h => h.number);
        const overdueNumbers = data.gaps.slice(0, 2).map(g => g.number);
        const trendingNumbers = data.trends.trending_up.slice(0, 2).map(t => t.number);
        
        // Combine and deduplicate
        const recommended = [...new Set([...hotNumbers, ...overdueNumbers, ...trendingNumbers])].slice(0, 5);
        
        // Get super balota recommendation for Baloto
        let superRecommendation = null;
        if (gameType === 'baloto' && data.super_analysis) {
            const hotSuper = data.super_analysis.hot[0];
            const overdueSuper = data.super_analysis.gaps[0];
            superRecommendation = hotSuper ? hotSuper.number : (overdueSuper ? overdueSuper.number : 1);
        }
        
        let html = `
            <div class="prediction-section">
                <h4><i class="fas fa-star"></i> Números Recomendados</h4>
                <div class="recommended-numbers">
                    ${recommended.map(n => `<span class="rec-ball">${n}</span>`).join('')}
                    ${superRecommendation ? `<span class="rec-ball super">${superRecommendation}</span>` : ''}
                </div>
            </div>
            
            <div class="prediction-section">
                <h4><i class="fas fa-lightbulb"></i> Análisis</h4>
                <div class="prediction-tip">
                    <strong>Números Calientes:</strong> ${hotNumbers.join(', ') || 'N/A'} - Han aparecido con mayor frecuencia.<br><br>
                    <strong>Números Atrasados:</strong> ${overdueNumbers.join(', ') || 'N/A'} - Llevan varios sorteos sin salir.<br><br>
                    <strong>En Tendencia:</strong> ${trendingNumbers.join(', ') || 'N/A'} - Están aumentando su frecuencia recientemente.<br><br>
                    <strong>Rango de Suma:</strong> Busca combinaciones cuya suma esté entre ${data.sum_distribution.recommended_range.low} y ${data.sum_distribution.recommended_range.high}.
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    // ============================================
    // HISTORY TAB
    // ============================================
    const loadHistoryBtn = document.getElementById('loadHistoryBtn');
    const historyGameSelect = document.getElementById('historyGameSelect');
    
    loadHistoryBtn.addEventListener('click', async () => {
        const gameType = historyGameSelect.value;
        
        try {
            statusMsg.textContent = `Cargando historial de ${gameType}...`;
            statusMsg.style.color = '#8b5cf6';
            
            const response = await fetch(`/api/history/${gameType}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                renderHistory(result.data, gameType);
                statusMsg.textContent = `Historial cargado: ${result.count} sorteos`;
                statusMsg.style.color = '#4ade80';
            } else {
                statusMsg.textContent = result.message;
                statusMsg.style.color = '#ef4444';
            }
        } catch (error) {
            statusMsg.textContent = 'Error cargando historial';
            statusMsg.style.color = '#ef4444';
        }
    });

    function renderHistory(data, gameType) {
        const container = document.getElementById('historyContainer');
        
        if (data.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay datos disponibles. Actualiza los datos primero.</p>';
            return;
        }
        
        let tableHtml = `
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Números</th>
                        ${gameType === 'baloto' ? '<th>Super</th>' : ''}
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.forEach(draw => {
            const numbersHtml = draw.numbers.map(n => `<span class="history-ball">${n}</span>`).join('');
            const superHtml = gameType === 'baloto' && draw.super ? `<span class="history-ball super">${draw.super}</span>` : '';
            
            tableHtml += `
                <tr>
                    <td>${draw.date}</td>
                    <td><div class="history-numbers">${numbersHtml}</div></td>
                    ${gameType === 'baloto' ? `<td>${superHtml}</td>` : ''}
                </tr>
            `;
        });
        
        tableHtml += '</tbody></table>';
        container.innerHTML = tableHtml;
    }
});

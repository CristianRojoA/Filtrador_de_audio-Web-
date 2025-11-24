let ultimoAnalisisFFT = null;

// Manejar selección de archivo
document.getElementById('audioFileFFT').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    document.getElementById('fileNameFFT').textContent = `📁 ${file.name}`;
    
    // Subir archivo
    const formData = new FormData();
    formData.append('audio', file);
    
    try {
        const response = await fetch('/api/fft/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('✅ Archivo cargado correctamente', 'success');
        } else {
            mostrarMensaje('❌ Error al cargar archivo: ' + data.error, 'error');
        }
    } catch (error) {
        mostrarMensaje('❌ Error: ' + error.message, 'error');
    }
});

async function analizarFFT() {
    const graficos = document.getElementById('graficosFFT');
    
    graficos.innerHTML = `
        <div class="loading-overlay">
            <div class="loader">
                <div class="truckWrapper">
                    <div class="truckBody">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 198 93" class="trucksvg">
                            <path stroke-width="3" stroke="#282828" fill="#F83D3D" d="M135 22.5H177.264C178.295 22.5 179.22 23.133 179.594 24.0939L192.33 56.8443C192.442 57.1332 192.5 57.4404 192.5 57.7504V89C192.5 90.3807 191.381 91.5 190 91.5H135C133.619 91.5 132.5 90.3807 132.5 89V25C132.5 23.6193 133.619 22.5 135 22.5Z"></path>
                            <path stroke-width="3" stroke="#282828" fill="#7D7C7C" d="M146 33.5H181.741C182.779 33.5 183.709 34.1415 184.078 35.112L190.538 52.112C191.16 53.748 189.951 55.5 188.201 55.5H146C144.619 55.5 143.5 54.3807 143.5 53V36C143.5 34.6193 144.619 33.5 146 33.5Z"></path>
                            <path stroke-width="2" stroke="#282828" fill="#282828" d="M150 65C150 65.39 149.763 65.8656 149.127 66.2893C148.499 66.7083 147.573 67 146.5 67C145.427 67 144.501 66.7083 143.873 66.2893C143.237 65.8656 143 65.39 143 65C143 64.61 143.237 64.1344 143.873 63.7107C144.501 63.2917 145.427 63 146.5 63C147.573 63 148.499 63.2917 149.127 63.7107C149.763 64.1344 150 64.61 150 65Z"></path>
                            <rect stroke-width="2" stroke="#282828" fill="#FFFCAB" rx="1" height="7" width="5" y="63" x="187"></rect>
                            <rect stroke-width="2" stroke="#282828" fill="#282828" rx="1" height="11" width="4" y="81" x="193"></rect>
                            <rect stroke-width="3" stroke="#282828" fill="#DFDFDF" rx="2.5" height="90" width="121" y="1.5" x="6.5"></rect>
                            <rect stroke-width="2" stroke="#282828" fill="#DFDFDF" rx="2" height="4" width="6" y="84" x="1"></rect>
                        </svg>
                    </div>
                    <div class="truckTires">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 30 30" class="tiresvg">
                            <circle stroke-width="3" stroke="#282828" fill="#282828" r="13.5" cy="15" cx="15"></circle>
                            <circle fill="#DFDFDF" r="7" cy="15" cx="15"></circle>
                        </svg>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 30 30" class="tiresvg">
                            <circle stroke-width="3" stroke="#282828" fill="#282828" r="13.5" cy="15" cx="15"></circle>
                            <circle fill="#DFDFDF" r="7" cy="15" cx="15"></circle>
                        </svg>
                    </div>
                    <div class="road"></div>
                    <svg class="trafficLight" width="70" height="100" viewBox="0 80 240">
                        <rect x="35" y="20" width="10" height="200" fill="#555" />
                        <rect x="25" y="35" width="30" height="59" rx="8" fill="#333" stroke="#222" stroke-width="3" />
                        <circle cx="40" cy="45" r="8" fill="#d62828" />
                        <circle cx="40" cy="65" r="8" fill="#fcbf49" />
                        <circle cx="40" cy="85" r="8" fill="#38b000" />
                    </svg>
                </div>
            </div>
            <p class="loading-text">🎵 Generando espectrograma...</p>
        </div>
    `;
    
    const tiempoInicio = Date.now();
    
    try {
        const response = await fetch('/api/fft/analizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        const tiempoTranscurrido = ((Date.now() - tiempoInicio) / 1000).toFixed(2);
        
        if (data.success) {
            ultimoAnalisisFFT = data;
            
            // Mostrar solo el espectrograma
            if (data.espectrograma_url) {
                mostrarEspectrograma(data.espectrograma_url, data.archivo, tiempoTranscurrido);
            } else {
                graficos.innerHTML = '<div class="error-message">❌ No se pudo generar el espectrograma</div>';
            }
        } else {
            graficos.innerHTML = `<div class="error-message">❌ Error: ${data.error}</div>`;
        }
    } catch (error) {
        graficos.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    }
}

function mostrarAnalisisCompleto(data) {
    const resultados = document.getElementById('resultadosFFT');
    
    const frecuenciasDominantes = data.frecuencias_dominantes
        .sort((a, b) => b.magnitud - a.magnitud)
        .slice(0, 10);
    
    let html = `
<div class="success-message">
    <h3>📊 ANÁLISIS FFT COMPLETO</h3>
    
    <div class="info-grid">
        <div class="info-item">
            <strong>📁 Archivo:</strong> ${data.archivo}
        </div>
        <div class="info-item">
            <strong>⏱️ Duración:</strong> ${data.duracion_total.toFixed(2)}s
        </div>
        <div class="info-item">
            <strong>🎵 Tasa de muestreo:</strong> ${data.sample_rate} Hz
        </div>
        <div class="info-item">
            <strong>🔊 Potencia promedio:</strong> ${data.potencia_promedio.toFixed(2)} dB
        </div>
    </div>
    
    <h4>🎯 Top 10 Frecuencias Dominantes:</h4>
    <div class="frequency-list">
        ${frecuenciasDominantes.map((f, i) => `
            <div class="frequency-item">
                <span class="rank">#${i + 1}</span>
                <span class="frequency">${f.frecuencia.toFixed(2)} Hz</span>
                <span class="magnitude">Magnitud: ${f.magnitud.toFixed(2)}</span>
            </div>
        `).join('')}
    </div>
    
    <h4>📈 Rangos de Frecuencia:</h4>
    <div class="range-analysis">
        <div class="range-item">
            <strong>🔊 Graves (20-250 Hz):</strong> 
            ${calcularEnergiaRango(data.frecuencias_dominantes, 20, 250)}%
        </div>
        <div class="range-item">
            <strong>🎤 Medios (250-2000 Hz):</strong> 
            ${calcularEnergiaRango(data.frecuencias_dominantes, 250, 2000)}%
        </div>
        <div class="range-item">
            <strong>🎵 Agudos (2000-20000 Hz):</strong> 
            ${calcularEnergiaRango(data.frecuencias_dominantes, 2000, 20000)}%
        </div>
    </div>
</div>
    `;
    
    resultados.innerHTML = html;
}

function mostrarAnalisisVentanas(data) {
    const resultados = document.getElementById('resultadosFFT');
    
    let html = `
<div class="success-message">
    <h3>📊 ANÁLISIS FFT POR VENTANAS</h3>
    
    <div class="info-grid">
        <div class="info-item">
            <strong>📁 Archivo:</strong> ${data.archivo}
        </div>
        <div class="info-item">
            <strong>⏱️ Duración total:</strong> ${data.duracion_total.toFixed(2)}s
        </div>
        <div class="info-item">
            <strong>🔍 Ventanas analizadas:</strong> ${data.ventanas.length}
        </div>
        <div class="info-item">
            <strong>🎵 Tasa de muestreo:</strong> ${data.sample_rate} Hz
        </div>
    </div>
    
    <h4>📊 Análisis por Ventana:</h4>
    <div class="windows-list">
        ${data.ventanas.map((v, i) => `
            <div class="window-item">
                <h5>Ventana ${i + 1}: ${v.tiempo_inicio.toFixed(2)}s - ${v.tiempo_fin.toFixed(2)}s</h5>
                <p><strong>🔊 Potencia:</strong> ${v.potencia.toFixed(2)} dB</p>
                <p><strong>🎯 Frecuencia dominante:</strong> ${v.frecuencia_dominante.toFixed(2)} Hz</p>
                
                <details>
                    <summary>Ver frecuencias principales</summary>
                    <div class="freq-details">
                        ${v.frecuencias_principales.slice(0, 5).map((f, j) => `
                            <div>#${j + 1}: ${f.frecuencia.toFixed(2)} Hz (${f.magnitud.toFixed(2)})</div>
                        `).join('')}
                    </div>
                </details>
            </div>
        `).join('')}
    </div>
</div>
    `;
    
    resultados.innerHTML = html;
}

function calcularEnergiaRango(frecuencias, min, max) {
    const total = frecuencias.reduce((sum, f) => sum + f.magnitud, 0);
    const rango = frecuencias
        .filter(f => f.frecuencia >= min && f.frecuencia <= max)
        .reduce((sum, f) => sum + f.magnitud, 0);
    
    return ((rango / total) * 100).toFixed(1);
}

function crearGraficoASCII(data) {
    const graficos = document.getElementById('graficosFFT');
    
    const frecuencias = data.frecuencias_dominantes
        .sort((a, b) => b.magnitud - a.magnitud)
        .slice(0, 25);
    
    const maxMag = Math.max(...frecuencias.map(f => f.magnitud));
    
    let html = '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; color: white;">';
    html += '<h3 style="margin: 0 0 20px 0; font-size: 20px;">📊 ESPECTRO DE FRECUENCIAS (Top 25)</h3>';
    
    frecuencias.forEach((f, i) => {
        const barLength = (f.magnitud / maxMag) * 100;
        const color = i < 3 ? '#FFD700' : i < 10 ? '#00ff88' : '#4FC3F7';
        const emoji = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '📊';
        
        html += `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; margin-bottom: 3px;">
                    <span style="width: 30px;">${emoji}</span>
                    <span style="font-weight: bold; min-width: 80px;">${f.frecuencia.toFixed(0)} Hz</span>
                    <span style="color: rgba(255,255,255,0.7); font-size: 13px;">${f.magnitud.toFixed(1)}</span>
                </div>
                <div style="background: rgba(255,255,255,0.2); border-radius: 10px; height: 18px; overflow: hidden; margin-left: 30px;">
                    <div style="background: ${color}; height: 100%; width: ${barLength}%; transition: width 0.5s; border-radius: 10px; box-shadow: 0 0 10px ${color};"></div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    graficos.innerHTML = html;
}

async function exportarFFT() {
    if (!ultimoAnalisisFFT) {
        mostrarMensaje('⚠️ No hay análisis para exportar', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/fft/exportar', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje(`✅ Análisis FFT exportado a: ${data.path}`, 'success');
        } else {
            mostrarMensaje(`❌ Error al exportar: ${data.error}`, 'error');
        }
    } catch (error) {
        mostrarMensaje(`❌ Error: ${error.message}`, 'error');
    }
}

function mostrarMensaje(mensaje, tipo) {
    const resultados = document.getElementById('resultadosFFT');
    resultados.innerHTML = `<div class="${tipo}-message">${mensaje}</div>`;
}

function mostrarEspectrograma(url, archivo, tiempoTranscurrido) {
    const graficos = document.getElementById('graficosFFT');
    
    graficos.innerHTML = `
        <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
                <h3 style="color: #333; margin: 0; font-size: 22px;">
                    📊 Espectrograma del audio seleccionado
                </h3>
                <button onclick="descargarEspectrograma('${url}', '${archivo}')" class="btn btn-success" style="padding: 10px 20px; font-size: 0.9em; margin: 0;">
                    💾 Descargar Imagen
                </button>
            </div>
            <div style="background: #f5f5f5; padding: 10px; border-radius: 10px; margin-bottom: 15px;">
                <p style="margin: 5px 0; color: #666;"><strong>📁 Archivo:</strong> ${archivo}</p>
                ${tiempoTranscurrido ? `<p style="margin: 5px 0; color: #666;"><strong>⏱️ Tiempo de análisis:</strong> ${tiempoTranscurrido}s</p>` : ''}
            </div>
            <div style="background: white; border: 2px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
                <img src="${url}" alt="Espectrograma" style="width: 100%; height: auto; display: block;" id="espectrogramaImg">
            </div>
            <p style="color: #888; margin: 15px 0 0 0; font-size: 13px; text-align: right; font-style: italic;">
                Espectrograma generado automáticamente
            </p>
        </div>
    `;
}

function descargarEspectrograma(url, archivo) {
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = blobUrl;
            
            // Nombre del archivo con timestamp
            const nombreArchivo = archivo.replace(/\.[^/.]+$/, '');
            const timestamp = new Date().toISOString().slice(0,19).replace(/:/g,'-');
            a.download = `espectrograma_${nombreArchivo}_${timestamp}.png`;
            
            document.body.appendChild(a);
            a.click();
            
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(blobUrl);
            }, 100);
            
            mostrarMensaje('✅ Espectrograma descargado', 'success');
        })
        .catch(error => {
            mostrarMensaje('❌ Error al descargar: ' + error.message, 'error');
        });
}

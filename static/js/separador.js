let archivoFiltrado = null;

// Manejar selección de archivo
document.getElementById('audioFileSeparador').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    document.getElementById('fileNameSeparador').textContent = `📁 ${file.name}`;
    
    // Subir archivo
    const formData = new FormData();
    formData.append('audio', file);
    
    try {
        const response = await fetch('/api/separador/upload', {
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

async function separarAudio() {
    const resultados = document.getElementById('resultadosSeparador');
    const claseAudio = document.querySelector('input[name="claseAudio"]:checked')?.value;
    const modoOperacion = 'aislar';  // Siempre aislar
    
    if (!claseAudio) {
        mostrarMensaje('❌ Por favor selecciona una clase de audio', 'error');
        return;
    }
    
    resultados.innerHTML = `
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
            <p class="loading-text">🔊 Aplicando SFFT → Aislando frecuencias → ISFFT...</p>
        </div>
    `;
    
    let payload = { 
        clase_audio: claseAudio,
        modo_operacion: modoOperacion
    };
    
    try {
        const response = await fetch('/api/separador/filtrar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.success) {
            archivoFiltrado = data.archivo_filtrado;
            
            let html = `
<div class="success-message">
    <h3>✅ Frecuencias Aisladas con ISFFT</h3>
    
    <div class="info-grid">
        <div class="info-item">
            <strong>📁 Archivo original:</strong> ${data.archivo_original}
        </div>
        <div class="info-item">
            <strong>🎯 Clase procesada:</strong> ${data.clase_procesada || 'N/A'}
        </div>
        <div class="info-item">
            <strong>🎵 Frecuencias aisladas:</strong> ${data.num_frecuencias || 0} frecuencias (ruido eliminado)
        </div>
        <div class="info-item">
            <strong>⏱️ Duración:</strong> ${data.duracion.toFixed(2)}s
        </div>
    </div>
    
    <h4>📊 Frecuencias Aisladas (Hz):</h4>
    <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <p style="margin: 0; color: #0c5460;">
            <strong>✅ Mantenidas (ruido de fondo eliminado):</strong><br>
            ${data.frecuencias_procesadas && data.frecuencias_procesadas.length > 0 
                ? data.frecuencias_procesadas.slice(0, 10).map(f => f.toFixed(1) + ' Hz').join(', ') + 
                  (data.frecuencias_procesadas.length > 10 ? '...' : '')
                : 'No hay frecuencias para mostrar'}
        </p>
    </div>
    
    <h4>📊 Análisis de Energía:</h4>
    <div class="filter-stats">
        <div class="stat-item">
            <div class="stat-label">🔊 Energía original</div>
            <div class="stat-value">${data.energia_original.toFixed(2)} dB</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">🎚️ Energía después de IFFT</div>
            <div class="stat-value">${data.energia_filtrada.toFixed(2)} dB</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">📉 Reducción</div>
            <div class="stat-value">${data.reduccion_db ? data.reduccion_db.toFixed(2) : '0.00'} dB</div>
        </div>
    </div>
    
    <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #0c5460;">
        <p style="margin: 0; color: #0c5460;">
            <strong>🔬 Método:</strong> ${data.metodo || 'SFFT → Supresión → ISFFT'}
        </p>
    </div>
    
    <p class="info-message">
        💾 Archivo guardado en: ${data.archivo_filtrado}
    </p>
</div>
            `;
            
            resultados.innerHTML = html;
            
            // Mostrar reproductor de audio
            const audioPlayer = document.getElementById('audioPlayer');
            const audioElement = document.getElementById('audioFiltrado');
            audioElement.src = `/api/separador/descargar?archivo=${encodeURIComponent(data.archivo_filtrado)}`;
            audioPlayer.style.display = 'block';
            
            // Mostrar comparación de espectros
            mostrarComparacion(data);
            
        } else {
            resultados.innerHTML = `
                <div class="error-message">
                    <h3>❌ Error en el Procesamiento</h3>
                    <p><strong>Mensaje:</strong> ${data.error}</p>
                    <p><strong>💡 Posibles soluciones:</strong></p>
                    <ul style="text-align: left; margin: 10px 0;">
                        <li>Asegúrate de haber entrenado el modelo primero</li>
                        <li>Verifica que existan los perfiles de frecuencia (frequency_profiles.json)</li>
                        <li>Recarga la página e intenta nuevamente</li>
                    </ul>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error completo:', error);
        resultados.innerHTML = `
            <div class="error-message">
                <h3>❌ Error de Conexión</h3>
                <p><strong>Mensaje:</strong> ${error.message}</p>
                <p><strong>💡 Verifica:</strong></p>
                <ul style="text-align: left; margin: 10px 0;">
                    <li>Que el servidor esté ejecutándose</li>
                    <li>Que hayas cargado un archivo de audio</li>
                    <li>La consola del navegador (F12) para más detalles</li>
                </ul>
            </div>
        `;
    }
}

function mostrarComparacion(data) {
    const comparacion = document.getElementById('comparacionEspectros');
    
    // Validar que existan las URLs de los espectrogramas
    if (!data.espectrograma_original_url || !data.espectrograma_filtrado_url) {
        comparacion.innerHTML = `
            <div class="error-message">
                ⚠️ No se pudieron generar los espectrogramas
            </div>
        `;
        return;
    }
    
    let html = `
<div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
    <h3 style="color: #333; margin: 0 0 20px 0; font-size: 22px; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
        📊 Comparación de Espectros
    </h3>
    
    <div style="margin-bottom: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="color: #555; margin: 0;">📊 Espectro Original</h4>
            <button onclick="descargarEspectrogramaSeparador('${data.espectrograma_original_url}', 'original')" class="btn btn-success" style="padding: 8px 15px; font-size: 0.85em;">
                💾 Descargar
            </button>
        </div>
        <div style="background: white; border: 2px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
            <img src="${data.espectrograma_original_url}" alt="Espectrograma Original" style="width: 100%; height: auto; display: block;">
        </div>
    </div>
    
    <div style="margin-bottom: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="color: #555; margin: 0;">🎚️ Espectro Reconstruido con ISFFT</h4>
            <button onclick="descargarEspectrogramaSeparador('${data.espectrograma_filtrado_url}', 'filtrado')" class="btn btn-success" style="padding: 8px 15px; font-size: 0.85em;">
                💾 Descargar
            </button>
        </div>
        <div style="background: white; border: 2px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
            <img src="${data.espectrograma_filtrado_url}" alt="Espectrograma Filtrado" style="width: 100%; height: auto; display: block;">
        </div>
    </div>
    
    <div style="background: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
        <h4 style="color: #667eea; margin: 0 0 10px 0;">💡 Interpretación:</h4>
        <p style="color: #555; margin: 5px 0;">El audio fue reconstruido usando <strong>ISFFT</strong> manteniendo solo las frecuencias aprendidas de "${data.clase_procesada || 'la clase seleccionada'}".</p>
        <p style="color: #555; margin: 5px 0;">Las líneas <strong style="color: cyan;">cyan</strong> en el espectrograma indican las frecuencias que fueron aisladas. Todo el ruido de fondo fue eliminado.</p>
    </div>
</div>
    `;
    
    comparacion.innerHTML = html;
}

function descargarEspectrogramaSeparador(url, tipo) {
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = blobUrl;
            
            const timestamp = new Date().toISOString().slice(0,19).replace(/:/g,'-');
            a.download = `espectrograma_${tipo}_${timestamp}.png`;
            
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

function crearEspectroASCII(espectro, icon) {
    if (!espectro || espectro.length === 0) {
        return 'No hay datos de espectro disponibles';
    }
    
    const maxMag = Math.max(...espectro.map(e => e.magnitud));
    let grafico = '';
    
    espectro.slice(0, 15).forEach(e => {
        const barLength = Math.floor((e.magnitud / maxMag) * 30);
        const bar = icon.repeat(Math.max(1, barLength));
        grafico += `${e.frecuencia.toFixed(0).padStart(6)} Hz │${bar}\n`;
    });
    
    return grafico;
}

function descargarAudio() {
    if (!archivoFiltrado) {
        mostrarMensaje('⚠️ No hay audio filtrado para descargar', 'warning');
        return;
    }
    
    const link = document.createElement('a');
    link.href = `/api/separador/descargar?archivo=${encodeURIComponent(archivoFiltrado)}`;
    link.download = archivoFiltrado.split('/').pop();
    link.click();
    
    mostrarMensaje('✅ Descargando audio filtrado...', 'success');
}

function mostrarMensaje(mensaje, tipo) {
    const resultados = document.getElementById('resultadosSeparador');
    resultados.innerHTML = `<div class="${tipo}-message">${mensaje}</div>`;
}

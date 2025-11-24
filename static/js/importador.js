let datosActuales = null;
let nombreArchivoActual = '';

// Manejar selección de archivo
document.getElementById('jsonFile').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = `📁 ${file.name}`;
    }
});

function cambiarTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Mostrar tab seleccionado
    const tabId = 'tab' + tabName.charAt(0).toUpperCase() + tabName.slice(1);
    const tabElement = document.getElementById(tabId);
    
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // Marcar botón como activo
    if (window.event && window.event.target) {
        window.event.target.classList.add('active');
    }
}

async function listarArchivos() {
    const lista = document.getElementById('listaArchivos');
    lista.innerHTML = '⏳ Buscando archivos...';
    
    try {
        const response = await fetch('/api/importar/listar');
        const data = await response.json();
        
        if (data.success && data.archivos.length > 0) {
            let html = '<div class="file-grid">';
            
            data.archivos.forEach(archivo => {
                const icono = archivo.tipo === 'detecciones' ? '🎯' : '📍';
                const clase = archivo.tipo === 'detecciones' ? 'file-detecciones' : 'file-metadatos';
                const tipoTexto = archivo.tipo === 'detecciones' ? 'Detecciones' : 'Metadatos';
                
                html += `
                    <div class="file-card ${clase}">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="file-icon">${icono}</div>
                            <div style="font-size: 0.85em; color: #999; font-weight: 600;">${tipoTexto}</div>
                        </div>
                        <div class="file-info">
                            <div class="file-name">${archivo.nombre}</div>
                            <div class="file-meta">
                                📅 ${archivo.fecha}<br>
                                📦 ${archivo.tamano}
                            </div>
                        </div>
                        <button class="btn btn-primary btn-small" onclick="cargarArchivoServidor('${archivo.nombre}')">
                            📥 Cargar Archivo
                        </button>
                    </div>
                `;
            });
            
            html += '</div>';
            lista.innerHTML = html;
        } else {
            lista.innerHTML = '<p class="info-message">📭 No hay archivos exportados disponibles</p>';
        }
    } catch (error) {
        lista.innerHTML = `<p class="error-message">❌ Error: ${error.message}</p>`;
    }
}

async function cargarJSON() {
    const fileInput = document.getElementById('jsonFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('⚠️ Por favor selecciona un archivo JSON');
        return;
    }
    
    try {
        const texto = await file.text();
        const datos = JSON.parse(texto);
        
        datosActuales = datos;
        mostrarDatos(datos, file.name);
    } catch (error) {
        alert(`❌ Error al leer el archivo: ${error.message}`);
    }
}

async function cargarArchivoServidor(nombre) {
    try {
        const response = await fetch('/api/importar/cargar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre })
        });
        
        const data = await response.json();
        
        if (data.success) {
            datosActuales = data.contenido;
            mostrarDatos(data.contenido, nombre);
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

function mostrarDatos(datos, nombreArchivo) {
    console.log('mostrarDatos llamada:', { nombreArchivo, esDetecciones: datos.detecciones !== undefined, numDetecciones: datos.detecciones?.length });
    
    datosActuales = datos;
    nombreArchivoActual = nombreArchivo;
    
    document.getElementById('panelResultados').style.display = 'block';
    document.getElementById('panelEstadisticas').style.display = 'block';
    
    // Determinar tipo de archivo
    const esDetecciones = datos.detecciones !== undefined || datos.detecciones_agrupadas !== undefined;
    const esMetadatos = datos.ubicacion !== undefined;
    
    // Normalizar: si tiene detecciones_agrupadas, usarlas como detecciones
    if (datos.detecciones_agrupadas && !datos.detecciones) {
        datos.detecciones = datos.detecciones_agrupadas;
    }
    
    // Resetear tabs - mostrar Metadatos por defecto
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('tabMetadatos').classList.add('active');
    document.getElementById('tabBtnMetadatos').classList.add('active');
    
    // Mostrar metadatos
    mostrarMetadatos(datos);
    
    // Mostrar JSON crudo
    document.getElementById('contenidoJson').textContent = JSON.stringify(datos, null, 2);
    
    // Calcular estadísticas
    if (esDetecciones) {
        calcularEstadisticas(datos.detecciones);
    }
}

function mostrarResumen(datos, nombreArchivo, esDetecciones, esMetadatos) {
    const contenido = document.getElementById('contenidoResumen');
    
    let html = `
<div class="summary-card">
    <h3>📄 ${nombreArchivo}</h3>
    
    <div class="info-grid">
        <div class="info-item">
            <strong>📁 Archivo:</strong> ${datos.archivo || 'N/A'}
        </div>
        <div class="info-item">
            <strong>⏱️ Duración:</strong> ${datos.duracion_total?.toFixed(2) || 'N/A'}s
        </div>
        <div class="info-item">
            <strong>📅 Fecha:</strong> ${datos.fecha || 'N/A'}
        </div>
        <div class="info-item">
            <strong>🎵 Sample Rate:</strong> ${datos.sample_rate || 'N/A'} Hz
        </div>
    </div>
    
    ${esDetecciones ? `
        <div class="info-message">
            🎯 <strong>Total de detecciones:</strong> ${datos.detecciones.length}
        </div>
        <div class="detections-list" style="max-height: 400px; overflow-y: auto;">
            ${datos.detecciones.slice(0, 10).map((det, i) => `
                <div class="detection-card">
                    <div class="detection-header">
                        <span class="detection-number">#${i + 1}</span>
                        <span class="detection-class">${det.clase}</span>
                        <span class="detection-confidence">${(det.confianza * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detection-body">
                        <div class="detection-time">
                            ⏱️ ${det.tiempo_inicio.toFixed(2)}s → ${det.tiempo_fin.toFixed(2)}s
                            <span class="duration">(${det.duracion.toFixed(2)}s)</span>
                        </div>
                    </div>
                </div>
            `).join('')}
            ${datos.detecciones.length > 10 ? `
                <p class="info-message">
                    ... y ${datos.detecciones.length - 10} detecciones más (ver pestaña Detecciones)
                </p>
            ` : ''}
        </div>
    ` : ''}
    
    ${esMetadatos ? `
        <div class="info-message">
            📍 <strong>Contiene metadatos geográficos</strong>
        </div>
        <div class="metadata-preview" style="margin-top: 15px;">
            ${datos.ubicacion ? `
                <div class="metadata-section">
                    <h4>📍 Ubicación</h4>
                    <p><strong>Dirección:</strong> ${datos.ubicacion.direccion || 'N/A'}</p>
                    <p><strong>Ciudad:</strong> ${datos.ubicacion.ciudad || 'N/A'}</p>
                    <p><strong>País:</strong> ${datos.ubicacion.pais || 'N/A'}</p>
                </div>
            ` : ''}
            ${datos.condiciones ? `
                <div class="metadata-section">
                    <h4>⛅ Condiciones</h4>
                    <p><strong>Clima:</strong> ${datos.condiciones.clima || 'N/A'}</p>
                    ${datos.condiciones.temperatura ? `<p><strong>Temperatura:</strong> ${datos.condiciones.temperatura}°C</p>` : ''}
                    ${datos.condiciones.trafico_estimado ? `<p><strong>Tráfico:</strong> ${datos.condiciones.trafico_estimado}</p>` : ''}
                    ${datos.condiciones.trafico ? `<p><strong>Tráfico:</strong> ${datos.condiciones.trafico}</p>` : ''}
                </div>
            ` : ''}
            ${datos.grabacion ? `
                <div class="metadata-section">
                    <h4>🎙️ Grabación</h4>
                    <p><strong>Fecha:</strong> ${datos.grabacion.fecha_grabacion || datos.grabacion.fecha || 'N/A'}</p>
                    <p><strong>Hora:</strong> ${datos.grabacion.hora_grabacion || datos.grabacion.hora || 'N/A'}</p>
                </div>
            ` : ''}
            ${datos.dispositivo ? `
                <div class="metadata-section">
                    <h4>📱 Dispositivo</h4>
                    <p><strong>Tipo:</strong> ${datos.dispositivo.tipo || 'N/A'}</p>
                </div>
            ` : ''}
        </div>
    ` : ''}
</div>
    `;
    
    contenido.innerHTML = html;
}

function mostrarDetecciones(detecciones) {
    const contenido = document.getElementById('contenidoDetecciones');
    
    console.log('mostrarDetecciones llamada con:', detecciones?.length, 'detecciones');
    
    if (!detecciones || detecciones.length === 0) {
        contenido.innerHTML = '<p class="info-message">No hay detecciones disponibles</p>';
        return;
    }
    
    let html = '<div class="detections-list">';
    
    detecciones.forEach((det, i) => {
        html += `
<div class="detection-card">
    <div class="detection-header">
        <span class="detection-number">#${i + 1}</span>
        <span class="detection-class">${det.clase}</span>
        <span class="detection-confidence">${(det.confianza * 100).toFixed(1)}%</span>
    </div>
    <div class="detection-body">
        <div class="detection-time">
            ⏱️ ${det.tiempo_inicio.toFixed(2)}s → ${det.tiempo_fin.toFixed(2)}s
            <span class="duration">(${det.duracion.toFixed(2)}s)</span>
        </div>
    </div>
</div>
        `;
    });
    
    html += '</div>';
    contenido.innerHTML = html;
}

function mostrarMetadatos(datos) {
    const contenido = document.getElementById('contenidoMetadatos');
    
    let html = '<div class="metadata-view">';
    
    // Información del archivo
    html += `
<div class="metadata-section">
    <h3>📄 Información del Archivo</h3>
    ${datos.archivo ? `<p><strong>Archivo:</strong> ${datos.archivo}</p>` : ''}
    ${datos.duracion_total ? `<p><strong>Duración:</strong> ${datos.duracion_total.toFixed(2)}s</p>` : ''}
    ${datos.fecha ? `<p><strong>Fecha de análisis:</strong> ${datos.fecha}</p>` : ''}
    ${datos.fecha_analisis ? `<p><strong>Fecha de análisis:</strong> ${datos.fecha_analisis}</p>` : ''}
    ${datos.sample_rate ? `<p><strong>Sample Rate:</strong> ${datos.sample_rate} Hz</p>` : ''}
</div>
    `;
    
    // Ubicación
    if (datos.ubicacion) {
        html += `
<div class="metadata-section">
    <h3>📍 Ubicación</h3>
    ${datos.ubicacion.direccion ? `<p><strong>Dirección:</strong> ${datos.ubicacion.direccion}</p>` : ''}
    ${datos.ubicacion.ciudad ? `<p><strong>Ciudad:</strong> ${datos.ubicacion.ciudad}</p>` : ''}
    ${datos.ubicacion.pais ? `<p><strong>País:</strong> ${datos.ubicacion.pais}</p>` : ''}
    ${datos.ubicacion.latitud ? `<p><strong>Coordenadas:</strong> ${datos.ubicacion.latitud}, ${datos.ubicacion.longitud}</p>` : ''}
    ${datos.ubicacion.notas_ubicacion ? `<p><strong>Notas:</strong> ${datos.ubicacion.notas_ubicacion}</p>` : ''}
</div>
        `;
    }
    
    // Condiciones
    if (datos.condiciones) {
        html += `
<div class="metadata-section">
    <h3>🌤️ Condiciones</h3>
    ${datos.condiciones.clima ? `<p><strong>Clima:</strong> ${datos.condiciones.clima}</p>` : ''}
    ${datos.condiciones.trafico_estimado ? `<p><strong>Tráfico:</strong> ${datos.condiciones.trafico_estimado}</p>` : ''}
    ${datos.condiciones.trafico ? `<p><strong>Tráfico:</strong> ${datos.condiciones.trafico}</p>` : ''}
    ${datos.condiciones.hora_dia ? `<p><strong>Hora del día:</strong> ${datos.condiciones.hora_dia}</p>` : ''}
    ${datos.condiciones.dia_semana ? `<p><strong>Día de la semana:</strong> ${datos.condiciones.dia_semana}</p>` : ''}
    ${datos.condiciones.temperatura ? `<p><strong>Temperatura:</strong> ${datos.condiciones.temperatura}°C</p>` : ''}
</div>
        `;
    }
    
    // Grabación
    if (datos.grabacion) {
        html += `
<div class="metadata-section">
    <h3>🎙️ Grabación</h3>
    ${datos.grabacion.fecha_grabacion ? `<p><strong>Fecha:</strong> ${datos.grabacion.fecha_grabacion}</p>` : ''}
    ${datos.grabacion.fecha ? `<p><strong>Fecha:</strong> ${datos.grabacion.fecha}</p>` : ''}
    ${datos.grabacion.hora_grabacion ? `<p><strong>Hora:</strong> ${datos.grabacion.hora_grabacion}</p>` : ''}
    ${datos.grabacion.hora ? `<p><strong>Hora:</strong> ${datos.grabacion.hora}</p>` : ''}
    ${datos.grabacion.duracion_segundos ? `<p><strong>Duración:</strong> ${datos.grabacion.duracion_segundos}s</p>` : ''}
    ${datos.grabacion.duracion ? `<p><strong>Duración:</strong> ${datos.grabacion.duracion}</p>` : ''}
    ${datos.grabacion.calidad_audio ? `<p><strong>Calidad:</strong> ${datos.grabacion.calidad_audio}</p>` : ''}
</div>
        `;
    }
    
    // Dispositivo
    if (datos.dispositivo) {
        html += `
<div class="metadata-section">
    <h3>📱 Dispositivo</h3>
    ${datos.dispositivo.tipo ? `<p><strong>Tipo:</strong> ${datos.dispositivo.tipo}</p>` : ''}
    ${datos.dispositivo.marca_modelo ? `<p><strong>Modelo:</strong> ${datos.dispositivo.marca_modelo}</p>` : ''}
    ${datos.dispositivo.modelo ? `<p><strong>Modelo:</strong> ${datos.dispositivo.modelo}</p>` : ''}
    ${datos.dispositivo.sample_rate ? `<p><strong>Sample Rate:</strong> ${datos.dispositivo.sample_rate} Hz</p>` : ''}
    ${datos.dispositivo.sistema_operativo ? `<p><strong>SO:</strong> ${datos.dispositivo.sistema_operativo}</p>` : ''}
</div>
        `;
    }
    
    // Análisis
    if (datos.analisis) {
        html += `
<div class="metadata-section">
    <h3>📊 Análisis</h3>
    ${datos.analisis.clasificacion ? `<p><strong>Clasificación:</strong> ${datos.analisis.clasificacion}</p>` : ''}
    ${datos.analisis.confianza ? `<p><strong>Confianza:</strong> ${(datos.analisis.confianza * 100).toFixed(2)}%</p>` : ''}
    ${datos.analisis.detecciones_temporales && datos.analisis.detecciones_temporales.length > 0 ? `<p><strong>Detecciones temporales:</strong> ${datos.analisis.detecciones_temporales.length}</p>` : ''}
    ${datos.analisis.recomendaciones && datos.analisis.recomendaciones.length > 0 ? `
        <div style="margin-top: 10px;">
            <strong>Recomendaciones:</strong>
            <ul style="margin: 5px 0; padding-left: 20px;">
                ${datos.analisis.recomendaciones.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    ` : ''}
</div>
        `;
    }
    
    // Detecciones (si existen)
    if (datos.detecciones || datos.detecciones_agrupadas) {
        const detecciones = datos.detecciones || datos.detecciones_agrupadas;
        html += `
<div class="metadata-section">
    <h3>🎯 Detecciones (${detecciones.length})</h3>
    <div class="detections-list" style="max-height: 400px; overflow-y: auto;">
        ${detecciones.slice(0, 20).map((det, i) => `
            <div class="detection-card" style="margin-bottom: 10px; padding: 10px; background: #f5f5f5; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold;">#${i + 1} ${det.clase}</span>
                    <span style="color: #667eea; font-weight: bold;">${(det.confianza * 100).toFixed(1)}%</span>
                </div>
                <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                    ⏱️ ${det.tiempo_inicio.toFixed(2)}s → ${det.tiempo_fin.toFixed(2)}s (${det.duracion.toFixed(2)}s)
                </div>
            </div>
        `).join('')}
        ${detecciones.length > 20 ? `
            <p style="text-align: center; color: #666; margin-top: 10px;">
                ... y ${detecciones.length - 20} detecciones más
            </p>
        ` : ''}
    </div>
</div>
        `;
    }
    
    // Notas
    if (datos.notas) {
        html += `
<div class="metadata-section">
    <h3>📝 Notas</h3>
    <p style="white-space: pre-wrap;">${datos.notas}</p>
</div>
        `;
    }
    
    // Si no hay ningún dato
    if (!datos.ubicacion && !datos.condiciones && !datos.grabacion && !datos.dispositivo && !datos.analisis && !datos.notas && !datos.detecciones && !datos.detecciones_agrupadas) {
        html = '<p class="info-message">No hay metadatos disponibles en este archivo</p>';
    }
    
    html += '</div>';
    contenido.innerHTML = html;
}

function calcularEstadisticas(detecciones) {
    const estadisticas = document.getElementById('estadisticas');
    
    // Contar por clase
    const conteo = {};
    let duracionTotal = 0;
    let confianzaTotal = 0;
    
    detecciones.forEach(det => {
        conteo[det.clase] = (conteo[det.clase] || 0) + 1;
        duracionTotal += det.duracion || 0;
        confianzaTotal += det.confianza || 0;
    });
    
    const confianzaPromedio = confianzaTotal / detecciones.length;
    
    let html = `
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">${detecciones.length}</div>
        <div class="stat-label">🎯 Total Detecciones</div>
    </div>
    
    <div class="stat-card">
        <div class="stat-value">${duracionTotal.toFixed(1)}s</div>
        <div class="stat-label">⏱️ Duración Total</div>
    </div>
    
    <div class="stat-card">
        <div class="stat-value">${(confianzaPromedio * 100).toFixed(1)}%</div>
        <div class="stat-label">📊 Confianza Promedio</div>
    </div>
    
    <div class="stat-card">
        <div class="stat-value">${Object.keys(conteo).length}</div>
        <div class="stat-label">📚 Clases Únicas</div>
    </div>
</div>

<h4>📊 Distribución por Clase:</h4>
<div class="class-distribution">
    ${Object.entries(conteo)
        .sort((a, b) => b[1] - a[1])
        .map(([clase, cantidad]) => `
            <div class="class-bar">
                <div class="class-label">${clase}</div>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${(cantidad / detecciones.length * 100)}%"></div>
                    <span class="bar-value">${cantidad}</span>
                </div>
            </div>
        `).join('')}
</div>
    `;
    
    estadisticas.innerHTML = html;
}

// Función para descargar metadatos en formato legible
function descargarMetadatos() {
    if (!datosActuales) {
        alert('⚠️ No hay datos cargados');
        return;
    }
    
    let contenido = '';
    contenido += '╔════════════════════════════════════════════════════════════════╗\n';
    contenido += '║          REPORTE DE METADATOS - ANÁLISIS DE AUDIO             ║\n';
    contenido += '╚════════════════════════════════════════════════════════════════╝\n\n';
    
    // Información del archivo
    contenido += '📄 INFORMACIÓN DEL ARCHIVO\n';
    contenido += '─'.repeat(60) + '\n';
    if (datosActuales.archivo) contenido += `Archivo: ${datosActuales.archivo}\n`;
    if (datosActuales.duracion_total) contenido += `Duración: ${datosActuales.duracion_total.toFixed(2)}s\n`;
    if (datosActuales.fecha) contenido += `Fecha de análisis: ${datosActuales.fecha}\n`;
    if (datosActuales.fecha_analisis) contenido += `Fecha de análisis: ${datosActuales.fecha_analisis}\n`;
    if (datosActuales.sample_rate) contenido += `Sample Rate: ${datosActuales.sample_rate} Hz\n`;
    contenido += '\n';
    
    // Ubicación
    if (datosActuales.ubicacion) {
        contenido += '📍 UBICACIÓN\n';
        contenido += '─'.repeat(60) + '\n';
        const ub = datosActuales.ubicacion;
        if (ub.direccion) contenido += `Dirección: ${ub.direccion}\n`;
        if (ub.ciudad) contenido += `Ciudad: ${ub.ciudad}\n`;
        if (ub.pais) contenido += `País: ${ub.pais}\n`;
        if (ub.latitud) contenido += `Coordenadas: ${ub.latitud}, ${ub.longitud}\n`;
        if (ub.notas_ubicacion) contenido += `Notas: ${ub.notas_ubicacion}\n`;
        contenido += '\n';
    }
    
    // Condiciones
    if (datosActuales.condiciones) {
        contenido += '🌤️ CONDICIONES\n';
        contenido += '─'.repeat(60) + '\n';
        const cond = datosActuales.condiciones;
        if (cond.clima) contenido += `Clima: ${cond.clima}\n`;
        if (cond.trafico_estimado) contenido += `Tráfico: ${cond.trafico_estimado}\n`;
        if (cond.trafico) contenido += `Tráfico: ${cond.trafico}\n`;
        if (cond.hora_dia) contenido += `Hora del día: ${cond.hora_dia}\n`;
        if (cond.dia_semana) contenido += `Día de la semana: ${cond.dia_semana}\n`;
        if (cond.temperatura) contenido += `Temperatura: ${cond.temperatura}°C\n`;
        contenido += '\n';
    }
    
    // Grabación
    if (datosActuales.grabacion) {
        contenido += '🎙️ GRABACIÓN\n';
        contenido += '─'.repeat(60) + '\n';
        const grab = datosActuales.grabacion;
        if (grab.fecha_grabacion) contenido += `Fecha: ${grab.fecha_grabacion}\n`;
        if (grab.fecha) contenido += `Fecha: ${grab.fecha}\n`;
        if (grab.hora_grabacion) contenido += `Hora: ${grab.hora_grabacion}\n`;
        if (grab.hora) contenido += `Hora: ${grab.hora}\n`;
        if (grab.duracion_segundos) contenido += `Duración: ${grab.duracion_segundos}s\n`;
        if (grab.duracion) contenido += `Duración: ${grab.duracion}\n`;
        if (grab.calidad_audio) contenido += `Calidad: ${grab.calidad_audio}\n`;
        contenido += '\n';
    }
    
    // Dispositivo
    if (datosActuales.dispositivo) {
        contenido += '📱 DISPOSITIVO\n';
        contenido += '─'.repeat(60) + '\n';
        const disp = datosActuales.dispositivo;
        if (disp.tipo) contenido += `Tipo: ${disp.tipo}\n`;
        if (disp.marca) contenido += `Marca: ${disp.marca}\n`;
        if (disp.modelo) contenido += `Modelo: ${disp.modelo}\n`;
        contenido += '\n';
    }
    
    // Observaciones
    if (datosActuales.observaciones) {
        contenido += '📝 OBSERVACIONES\n';
        contenido += '─'.repeat(60) + '\n';
        const obs = datosActuales.observaciones;
        if (obs.eventos_notables) contenido += `Eventos notables: ${obs.eventos_notables}\n`;
        if (obs.anomalias) contenido += `Anomalías: ${obs.anomalias}\n`;
        if (obs.notas_adicionales) contenido += `Notas adicionales: ${obs.notas_adicionales}\n`;
        if (obs.comentarios_generales) contenido += `Comentarios: ${obs.comentarios_generales}\n`;
        contenido += '\n';
    }
    
    // Detecciones (resumen)
    if (datosActuales.detecciones && datosActuales.detecciones.length > 0) {
        contenido += '🎯 RESUMEN DE DETECCIONES\n';
        contenido += '─'.repeat(60) + '\n';
        contenido += `Total de detecciones: ${datosActuales.detecciones.length}\n\n`;
        
        // Contar por clase
        const conteo = {};
        datosActuales.detecciones.forEach(det => {
            const clase = det.clase || 'Desconocido';
            conteo[clase] = (conteo[clase] || 0) + 1;
        });
        
        contenido += 'Distribución por clase:\n';
        Object.entries(conteo)
            .sort((a, b) => b[1] - a[1])
            .forEach(([clase, cantidad]) => {
                const porcentaje = ((cantidad / datosActuales.detecciones.length) * 100).toFixed(1);
                contenido += `  • ${clase}: ${cantidad} (${porcentaje}%)\n`;
            });
        contenido += '\n';
    }
    
    contenido += '═'.repeat(60) + '\n';
    contenido += `Generado: ${new Date().toLocaleString('es-ES')}\n`;
    contenido += '═'.repeat(60) + '\n';
    
    // Crear archivo y descargar
    const blob = new Blob([contenido], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    
    const nombreBase = nombreArchivoActual.replace('.json', '') || 'metadatos';
    a.download = `${nombreBase}_legible.txt`;
    
    document.body.appendChild(a);
    a.click();
    
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

// Cargar lista de archivos al iniciar
window.addEventListener('load', listarArchivos);

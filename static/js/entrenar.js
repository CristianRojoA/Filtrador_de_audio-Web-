async function listarClases() {
    const carpeta = document.getElementById('carpetaEntrenamiento').value;
    const clasesInfo = document.getElementById('clasesInfo');
    
    clasesInfo.innerHTML = '⏳ Analizando carpeta...';
    
    try {
        const response = await fetch('/api/entrenar/listar-clases', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ carpeta })
        });
        
        const data = await response.json();
        
        if (data.success) {
            let html = `
<div class="success-message">
    ✅ Carpeta analizada correctamente
    
    📚 Clases encontradas: ${data.clases.length}
    📁 Total de archivos: ${data.total_archivos}
    
    ${data.clases.map(clase => `
        <div class="clase-item">
            📂 ${clase.nombre}
            📊 ${clase.cantidad} archivos
        </div>
    `).join('')}
</div>
            `;
            clasesInfo.innerHTML = html;
        } else {
            clasesInfo.innerHTML = `<div class="error-message">❌ Error: ${data.error}</div>`;
        }
    } catch (error) {
        clasesInfo.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    }
}

async function iniciarEntrenamiento() {
    const carpeta = document.getElementById('carpetaEntrenamiento').value;
    const numEstimadores = parseInt(document.getElementById('numEstimadores').value);
    const maxProfundidad = parseInt(document.getElementById('maxProfundidad').value);
    const testSize = parseFloat(document.getElementById('testSize').value) / 100;
    
    const progreso = document.getElementById('progresoEntrenamiento');
    const progressBar = document.getElementById('progressBar');
    const progresoTexto = document.getElementById('progresoTexto');
    const resultados = document.getElementById('resultadosEntrenamiento');
    
    progreso.style.display = 'block';
    resultados.innerHTML = '';
    progressBar.style.width = '0%';
    
    // Mostrar animación de mano
    progreso.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; gap: 30px; padding: 40px;">
            <div class="🤚">
                <div class="👉"></div>
                <div class="👉"></div>
                <div class="👉"></div>
                <div class="👉"></div>
                <div class="🌴"></div>
                <div class="👍"></div>
            </div>
            <div class="progress-bar" style="width: 300px;">
                <div id="progressBar" class="progress-fill"></div>
            </div>
            <p id="progresoTexto" style="font-size: 1.1em; color: #667eea; font-weight: 600;">Iniciando entrenamiento...</p>
        </div>
    `;
    
    const newProgressBar = document.getElementById('progressBar');
    const newProgresoTexto = document.getElementById('progresoTexto');
    
    try {
        // Simular progreso visual
        let progresoPorcentaje = 0;
        const intervalo = setInterval(() => {
            progresoPorcentaje = Math.min(progresoPorcentaje + 5, 90);
            newProgressBar.style.width = progresoPorcentaje + '%';
            
            if (progresoPorcentaje < 30) {
                newProgresoTexto.textContent = '📂 Cargando archivos de audio...';
            } else if (progresoPorcentaje < 60) {
                newProgresoTexto.textContent = '🔊 Extrayendo características...';
            } else {
                newProgresoTexto.textContent = '🧠 Adquiriendo conocimiento...';
            }
        }, 500);
        
        const response = await fetch('/api/entrenar/entrenar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                carpeta,
                n_estimators: numEstimadores,
                max_depth: maxProfundidad,
                test_size: testSize
            })
        });
        
        clearInterval(intervalo);
        newProgressBar.style.width = '100%';
        newProgresoTexto.textContent = '✅ Entrenamiento completado';
        
        const data = await response.json();
        
        if (data.success) {
            let html = `
<div class="success-message">
    <h3 style="text-align: center; margin-bottom: 30px; font-size: 1.8em;">🎉 Modelo Entrenado Exitosamente</h3>
    
    <div class="metrics" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);">
            <div class="metric-value" style="font-size: 2.5em; font-weight: bold; color: white; margin-bottom: 10px;">${data.archivos_entrenados}</div>
            <div class="metric-label" style="color: rgba(255, 255, 255, 0.9); font-size: 1em;">📁 Archivos Procesados</div>
        </div>
        
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(240, 147, 251, 0.3);">
            <div class="metric-value" style="font-size: 2.5em; font-weight: bold; color: white; margin-bottom: 10px;">${data.clases.length}</div>
            <div class="metric-label" style="color: rgba(255, 255, 255, 0.9); font-size: 1em;">📚 Clases</div>
        </div>
        
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3);">
            <div class="metric-value" style="font-size: 2.5em; font-weight: bold; color: white; margin-bottom: 10px;">${data.tiempo_entrenamiento}s</div>
            <div class="metric-label" style="color: rgba(255, 255, 255, 0.9); font-size: 1em;">⏱️ Tiempo</div>
        </div>
    </div>
    
    <div style="background: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h4 style="color: #667eea; margin-bottom: 15px; font-size: 1.2em;">📂 Clases Entrenadas:</h4>
        <div class="clases-list" style="display: flex; gap: 10px; flex-wrap: wrap;">
            ${data.clases.map(clase => `<span class="clase-badge" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; font-size: 1em;">${clase}</span>`).join('')}
        </div>
    </div>
    
    <div style="background: #f0f9ff; padding: 20px; border-radius: 15px; border-left: 4px solid #667eea;">
        <p style="margin: 0; color: #1e40af; font-size: 1.1em;"><strong>💾 Modelo guardado en:</strong></p>
        <code style="background: white; padding: 10px 15px; border-radius: 8px; display: inline-block; margin-top: 10px; color: #667eea; font-size: 1em;">${data.modelo_guardado}</code>
    </div>
</div>
            `;
            resultados.innerHTML = html;
        } else {
            resultados.innerHTML = `<div class="error-message">❌ Error: ${data.error}</div>`;
        }
        
        setTimeout(() => {
            progreso.style.display = 'none';
        }, 2000);
        
    } catch (error) {
        resultados.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
        progreso.style.display = 'none';
    }
}

async function verInfoModelo() {
    const infoModelo = document.getElementById('infoModelo');
    infoModelo.innerHTML = '⏳ Cargando información...';
    
    try {
        const response = await fetch('/api/entrenar/info-modelo');
        const data = await response.json();
        
        if (data.success) {
            let html = `
<div class="info-message">
    <h4>ℹ️ Información del Modelo Actual</h4>
    
    <p><strong>📚 Clases:</strong> ${data.clases.join(', ')}</p>
    <p><strong>🌳 Estimadores:</strong> ${data.n_estimators}</p>
    <p><strong>📏 Profundidad Máxima:</strong> ${data.max_depth}</p>
    
    ${data.ultima_precision ? 
        `<p><strong>📊 Última Precisión:</strong> ${(data.ultima_precision * 100).toFixed(2)}%</p>` 
        : ''}
    
    <p><strong>💾 Modelo Guardado:</strong> modelo_personalizado/modelo_rf.pkl</p>
</div>
            `;
            infoModelo.innerHTML = html;
        } else {
            infoModelo.innerHTML = `<div class="warning-message">⚠️ No hay modelo entrenado</div>`;
        }
    } catch (error) {
        infoModelo.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    }
}

async function analizarCarpeta() {
    const carpeta = document.getElementById('carpetaEntrenamiento').value;
    const infoModelo = document.getElementById('infoModelo');
    
    infoModelo.innerHTML = '⏳ Analizando carpeta...';
    
    try {
        const response = await fetch('/api/entrenar/analizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ carpeta })
        });
        
        const data = await response.json();
        
        if (data.success) {
            let html = `
<div class="info-message">
    <h4>📊 Análisis de Carpeta</h4>
    
    <p><strong>📂 Ruta:</strong> ${data.carpeta}</p>
    <p><strong>📁 Total de archivos:</strong> ${data.total_archivos}</p>
    <p><strong>⏱️ Duración total:</strong> ${data.duracion_total.toFixed(2)}s</p>
    <p><strong>📚 Clases:</strong> ${data.clases.length}</p>
    
    <h5>Detalle por clase:</h5>
    ${data.clases.map(clase => `
        <div class="clase-detalle">
            <strong>${clase.nombre}</strong><br>
            📁 ${clase.archivos} archivos | ⏱️ ${clase.duracion.toFixed(2)}s
        </div>
    `).join('')}
</div>
            `;
            infoModelo.innerHTML = html;
        } else {
            infoModelo.innerHTML = `<div class="error-message">❌ Error: ${data.error}</div>`;
        }
    } catch (error) {
        infoModelo.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    }
}

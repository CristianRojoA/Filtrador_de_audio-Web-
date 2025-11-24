let ultimoResultado = null;
let mediaRecorder = null;
let audioChunks = [];
let tiempoInicio = null;
let intervaloTiempo = null;
let ultimaGrabacion = null;

// Cambiar entre archivo y micrófono
function cambiarFuente(fuente) {
    const tabs = document.querySelectorAll('.source-tab');
    const archivo = document.getElementById('fuenteArchivo');
    const microfono = document.getElementById('fuenteMicrofono');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    
    if (fuente === 'archivo') {
        tabs[0].classList.add('active');
        archivo.style.display = 'block';
        microfono.style.display = 'none';
    } else {
        tabs[1].classList.add('active');
        archivo.style.display = 'none';
        microfono.style.display = 'block';
    }
}

// Iniciar grabación
async function iniciarGrabacion() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            ultimaGrabacion = audioBlob; // Guardar para descargar después
            await subirAudioGrabado(audioBlob);
            
            // Detener el stream
            stream.getTracks().forEach(track => track.stop());
        });
        
        mediaRecorder.start();
        
        document.getElementById('btnGrabar').style.display = 'none';
        document.getElementById('btnDetener').style.display = 'inline-block';
        document.getElementById('estadoGrabacion').textContent = '🔴 Grabando...';
        
        // Iniciar contador
        tiempoInicio = Date.now();
        intervaloTiempo = setInterval(() => {
            const segundos = Math.floor((Date.now() - tiempoInicio) / 1000);
            document.getElementById('tiempoGrabacion').textContent = `${segundos}s`;
        }, 100);
        
    } catch (error) {
        mostrarMensaje('❌ Error al acceder al micrófono: ' + error.message, 'error');
    }
}

// Detener grabación
function detenerGrabacion() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        
        clearInterval(intervaloTiempo);
        
        document.getElementById('btnGrabar').style.display = 'inline-block';
        document.getElementById('btnDetener').style.display = 'none';
        document.getElementById('estadoGrabacion').innerHTML = '✅ Grabación completada<br><button onclick="descargarGrabacion()" class="btn btn-success" style="margin-top: 10px;">💾 Descargar Audio</button>';
        document.getElementById('tiempoGrabacion').textContent = '';
    }
}

// Subir audio grabado
async function subirAudioGrabado(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'grabacion.wav');
    
    try {
        const response = await fetch('/api/identificar/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('✅ Audio grabado y cargado correctamente', 'success');
            document.getElementById('fileName').textContent = '📁 grabacion.wav';
        } else {
            mostrarMensaje('❌ Error al cargar grabación: ' + data.error, 'error');
        }
    } catch (error) {
        mostrarMensaje('❌ Error: ' + error.message, 'error');
    }
}

// Descargar grabación
function descargarGrabacion() {
    if (!ultimaGrabacion) {
        mostrarMensaje('❌ No hay grabación disponible', 'error');
        return;
    }
    
    const url = URL.createObjectURL(ultimaGrabacion);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `grabacion_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.wav`;
    
    document.body.appendChild(a);
    a.click();
    
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
    
    mostrarMensaje('✅ Audio descargado', 'success');
}

// Manejar selección de archivo
document.getElementById('audioFile').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    document.getElementById('fileName').textContent = `📁 ${file.name}`;
    
    // Subir archivo
    const formData = new FormData();
    formData.append('audio', file);
    
    try {
        const response = await fetch('/api/identificar/upload', {
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

async function predecirSimple() {
    const resultados = document.getElementById('resultados');
    resultados.innerHTML = '⏳ Analizando...';
    
    try {
        const response = await fetch('/api/identificar/simple', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            let html = `
📊 PREDICCIÓN SIMPLE
${'='.repeat(50)}

🎯 Clase predicha: ${data.clase}
📊 Confianza: ${(data.confianza * 100).toFixed(2)}%

📈 Probabilidades por clase:
${Object.entries(data.probabilidades)
    .sort((a, b) => b[1] - a[1])
    .map(([clase, prob]) => `   • ${clase}: ${(prob * 100).toFixed(2)}%`)
    .join('\n')}
            `;
            
            resultados.textContent = html;
            
            // Mostrar modal de alerta si es Mucho_Trafico
            if (data.clase.toLowerCase().includes('mucho_trafico') || data.clase.toLowerCase().includes('mucho trafico')) {
                mostrarAlerta();
            }
        } else {
            resultados.textContent = '❌ Error: ' + data.error;
        }
    } catch (error) {
        resultados.textContent = '❌ Error: ' + error.message;
    }
}

async function predecirTemporal() {
    const resultados = document.getElementById('resultados');
    const ventana = document.getElementById('ventana').value;
    
    resultados.innerHTML = '⏳ Realizando análisis temporal...';
    
    const tiempoInicio = Date.now();
    
    try {
        const response = await fetch('/api/identificar/temporal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ventana: parseFloat(ventana) })
        });
        
        const data = await response.json();
        const tiempoTranscurrido = ((Date.now() - tiempoInicio) / 1000).toFixed(2);
        
        if (data.success) {
            // Normalizar estructura: asegurar que tenga 'detecciones_agrupadas'
            ultimoResultado = {
                archivo: data.archivo,
                duracion_total: data.duracion_total,
                detecciones_agrupadas: data.detecciones
            };
            document.getElementById('btnExportar').disabled = false;
            
            // Calcular tiempo por clase para determinar la dominante
            const tiempoPorClase = {};
            data.detecciones.forEach(det => {
                const clase = det.clase || 'Desconocido';
                const duracion = det.tiempo_fin - det.tiempo_inicio;
                tiempoPorClase[clase] = (tiempoPorClase[clase] || 0) + duracion;
            });
            
            // Encontrar clase dominante
            let claseDominante = null;
            let tiempoMax = 0;
            for (const [clase, tiempo] of Object.entries(tiempoPorClase)) {
                if (tiempo > tiempoMax) {
                    tiempoMax = tiempo;
                    claseDominante = clase;
                }
            }
            
            let html = `
📊 ANÁLISIS TEMPORAL
${'='.repeat(50)}

📁 Archivo: ${data.archivo}
⏱️ Duración total: ${data.duracion_total.toFixed(2)}s
🔍 Total de detecciones: ${data.detecciones.length}
⏱️ Tiempo de análisis: ${tiempoTranscurrido}s

${'='.repeat(50)}

DETECCIONES:

${data.detecciones.map((det, i) => `
${i + 1}. ${(det.clase || 'Desconocido').toUpperCase()}
   ⏱️  ${det.tiempo_inicio.toFixed(2)}s → ${det.tiempo_fin.toFixed(2)}s
   📊 Confianza: ${((det.confianza_promedio || det.confianza || 0) * 100).toFixed(2)}%
`).join('\n')}
            `;
            resultados.textContent = html;
            
            // Mostrar alerta si la clase dominante es Mucho_Trafico
            if (claseDominante && (claseDominante.toLowerCase().includes('mucho_trafico') || claseDominante.toLowerCase().includes('mucho trafico'))) {
                mostrarAlerta();
            }
        } else {
            resultados.textContent = '❌ Error: ' + data.error;
        }
    } catch (error) {
        resultados.textContent = '❌ Error: ' + error.message;
    }
}

async function exportarJSON() {
    if (!ultimoResultado) {
        mostrarMensaje('⚠️ No hay resultados para exportar', 'warning');
        return;
    }
    
    const agregarMetadatos = confirm('¿Deseas agregar información de ubicación y contexto?');
    
    try {
        // Exportar detecciones enviando el resultado en el cuerpo
        const response1 = await fetch('/api/exportar/detecciones', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ultimoResultado)
        });
        
        const data1 = await response1.json();
        
        if (!data1.success) {
            mostrarMensaje('❌ Error al exportar: ' + data1.error, 'error');
            return;
        }
        
        if (agregarMetadatos) {
            // Mostrar formulario de metadatos
            const metadatos = await capturarMetadatos();
            
            if (metadatos) {
                console.log('📤 Enviando metadatos al servidor:', metadatos);
                const response2 = await fetch('/api/exportar/metadatos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(metadatos)
                });
                
                const data2 = await response2.json();
                console.log('📥 Respuesta del servidor:', data2);
                
                if (data2.success) {
                    mostrarMensaje(`✅ Exportado correctamente\n📄 Detecciones: ${data1.path}\n📍 Metadatos: ${data2.path}`, 'success');
                } else {
                    mostrarMensaje(`❌ Error al guardar metadatos: ${data2.error}`, 'error');
                }
            }
        } else {
            mostrarMensaje(`✅ Detecciones exportadas a: ${data1.path}`, 'success');
        }
    } catch (error) {
        mostrarMensaje('❌ Error: ' + error.message, 'error');
    }
}

function capturarMetadatos() {
    return new Promise((resolve) => {
        // Crear modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; max-width: 500px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
                <h2 style="color: white; margin: 0 0 20px 0; font-size: 24px;">📍 Información de Ubicación y Contexto</h2>
                
                <div style="margin-bottom: 15px;">
                    <label style="color: rgba(255,255,255,0.9); display: block; margin-bottom: 5px; font-weight: 500;">🏠 Dirección:</label>
                    <input type="text" id="metaDireccion" placeholder="Ej: Av. Principal 123" style="width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 14px; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="color: rgba(255,255,255,0.9); display: block; margin-bottom: 5px; font-weight: 500;">🏙️ Ciudad:</label>
                    <input type="text" id="metaCiudad" placeholder="Ej: Santiago" style="width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 14px; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="color: rgba(255,255,255,0.9); display: block; margin-bottom: 5px; font-weight: 500;">🌍 País:</label>
                    <input type="text" id="metaPais" placeholder="Ej: Chile" style="width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 14px; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="color: rgba(255,255,255,0.9); display: block; margin-bottom: 5px; font-weight: 500;">🌤️ Clima:</label>
                    <select id="metaClima" style="width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 14px; box-sizing: border-box;">
                        <option value="soleado">☀️ Soleado</option>
                        <option value="nublado">☁️ Nublado</option>
                        <option value="lluvia">🌧️ Lluvia</option>
                        <option value="niebla">🌫️ Niebla</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="color: rgba(255,255,255,0.9); display: block; margin-bottom: 5px; font-weight: 500;">📱 Tipo de Dispositivo:</label>
                    <select id="metaTipoDispositivo" style="width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 14px; box-sizing: border-box;">
                        <option value="telefono">📱 Teléfono</option>
                        <option value="microfono">🎤 Micrófono</option>
                        <option value="otro">🔧 Otro</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="color: rgba(255,255,255,0.9); display: block; margin-bottom: 5px; font-weight: 500;">🏷️ Modelo del Dispositivo:</label>
                    <input type="text" id="metaModeloDispositivo" placeholder="Ej: iPhone 13, Samsung Galaxy S21, Blue Yeti" style="width: 100%; padding: 10px; border: none; border-radius: 8px; font-size: 14px; box-sizing: border-box;">
                </div>
                
                <div style="display: flex; gap: 10px;">
                    <button id="btnGuardarMeta" style="flex: 1; padding: 12px; background: white; color: #667eea; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">
                        ✅ Guardar
                    </button>
                    <button id="btnCancelarMeta" style="flex: 1; padding: 12px; background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">
                        ❌ Cancelar
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Enfocar primer campo
        setTimeout(() => document.getElementById('metaDireccion').focus(), 100);
        
        // Botón guardar
        document.getElementById('btnGuardarMeta').onclick = () => {
            const direccion = document.getElementById('metaDireccion').value;
            const ciudad = document.getElementById('metaCiudad').value;
            const pais = document.getElementById('metaPais').value;
            const clima = document.getElementById('metaClima').value;
            const tipoDispositivo = document.getElementById('metaTipoDispositivo').value;
            const modeloDispositivo = document.getElementById('metaModeloDispositivo').value;
            
            document.body.removeChild(modal);
            
            if (direccion || ciudad) {
                const metadatos = {
                    ubicacion: { direccion, ciudad, pais },
                    condiciones: { clima },
                    grabacion: { 
                        fecha: new Date().toISOString().split('T')[0],
                        hora: new Date().toTimeString().split(' ')[0].substring(0, 5)
                    },
                    dispositivo: { 
                        tipo: tipoDispositivo,
                        marca_modelo: modeloDispositivo || null
                    }
                };
                console.log('📍 Metadatos capturados:', metadatos);
                resolve(metadatos);
            } else {
                resolve(null);
            }
        };
        
        // Botón cancelar
        document.getElementById('btnCancelarMeta').onclick = () => {
            document.body.removeChild(modal);
            resolve(null);
        };
        
        // Cerrar con ESC
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                resolve(null);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    });
}

// Funciones para el modal de alerta de tráfico
function mostrarAlerta() {
    const modal = document.getElementById('alertModal');
    modal.classList.add('active');
}

function closeAlert() {
    const modal = document.getElementById('alertModal');
    modal.classList.remove('active');
}

// Cerrar modal al hacer clic fuera de él
document.addEventListener('DOMContentLoaded', function() {
    const alertModal = document.getElementById('alertModal');
    if (alertModal) {
        alertModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAlert();
            }
        });
    }
});

function mostrarMensaje(mensaje, tipo) {
    const resultados = document.getElementById('resultados');
    resultados.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
}

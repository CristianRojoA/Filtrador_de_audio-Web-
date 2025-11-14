"""
🔧 CONVERTIDOR DE AUDIOS A WAV
================================
Convierte todos los MP3 corruptos a formato WAV limpio
"""

import os
from pydub import AudioSegment
from pathlib import Path

def convertir_mp3_a_wav(directorio_base="datos_entrenamiento"):
    """Convierte todos los MP3 a WAV"""
    print("🔄 CONVIRTIENDO AUDIOS A WAV...")
    print("="*50)
    
    total_convertidos = 0
    total_errores = 0
    
    for carpeta in os.listdir(directorio_base):
        carpeta_path = os.path.join(directorio_base, carpeta)
        if not os.path.isdir(carpeta_path):
            continue
        
        print(f"\n📂 Procesando: {carpeta}")
        
        archivos_mp3 = [f for f in os.listdir(carpeta_path) if f.lower().endswith('.mp3')]
        
        for archivo in archivos_mp3:
            archivo_path = os.path.join(carpeta_path, archivo)
            nuevo_nombre = archivo.replace('.mp3', '.wav')
            nuevo_path = os.path.join(carpeta_path, nuevo_nombre)
            
            # Si ya existe el WAV, saltar
            if os.path.exists(nuevo_path):
                print(f"   ⏭️ Ya existe: {nuevo_nombre}")
                continue
            
            try:
                # Intentar cargar y convertir
                audio = AudioSegment.from_mp3(archivo_path)
                
                # Convertir a mono si es estéreo
                if audio.channels > 1:
                    audio = audio.set_channels(1)
                
                # Establecer sample rate a 16000 Hz
                audio = audio.set_frame_rate(16000)
                
                # Exportar como WAV
                audio.export(nuevo_path, format="wav")
                
                print(f"   ✅ Convertido: {archivo} → {nuevo_nombre}")
                total_convertidos += 1
                
                # Opcional: eliminar MP3 original
                # os.remove(archivo_path)
                
            except Exception as e:
                print(f"   ❌ Error con {archivo}: {e}")
                total_errores += 1
    
    print(f"\n🎯 RESUMEN:")
    print(f"   ✅ Convertidos: {total_convertidos}")
    print(f"   ❌ Errores: {total_errores}")
    print(f"\n💡 Ahora ejecuta el entrenador de nuevo")

if __name__ == "__main__":
    # Instalar pydub si no está instalado
    try:
        from pydub import AudioSegment
    except ImportError:
        print("📦 Instalando pydub...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pydub'])
        from pydub import AudioSegment
    
    convertir_mp3_a_wav()

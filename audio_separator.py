"""
🎵 SEPARADOR DE AUDIO
=====================
Separa y filtra componentes específicos del audio
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from pathlib import Path
import json
from datetime import datetime

class AudioSeparator:
    def isolate_by_class(self, segment_audio, clase, filter_mode='keep_motors'):
        """Aísla o filtra el audio según la clase y el modo de filtrado.
        
        Args:
            segment_audio: Audio del segmento
            clase: Clase detectada
            filter_mode: 'keep_motors' = mantener solo motores, eliminar voces/claxon
                        'keep_all_vehicle' = mantener todo el vehículo
                        'custom' = usar rango específico de la clase
        """
        # Definir rangos de frecuencia según el modo
        if filter_mode == 'keep_motors':
            # Mantener solo frecuencias de motores, eliminar voces (300-3400 Hz) y claxon (400-800 Hz)
            freq_ranges = {
                'auto': [(60, 250), (1200, 2500)],      # Motor bajo y alto, evita voces medias
                'trafico': [(60, 300), (1000, 2500)],   # Motores múltiples
                'trafico pesado': [(40, 200)]           # Solo graves profundos de motores pesados
            }
        elif filter_mode == 'keep_all_vehicle':
            # Mantener todo el espectro del vehículo
            freq_ranges = {
                'auto': [(60, 3000)],
                'trafico': [(60, 4000)],
                'trafico pesado': [(40, 1500)]
            }
        else:  # custom
            freq_ranges = {
                'auto': [(80, 1200)],
                'trafico': [(80, 3000)],
                'trafico pesado': [(40, 800)]
            }
        
        # Normalizar nombre de clase
        clase_key = clase.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        ranges = freq_ranges.get(clase_key, [(20, self.sample_rate//2)])
        
        n = len(segment_audio)
        # FFT
        spectrum = np.fft.rfft(segment_audio)
        freqs = np.fft.rfftfreq(n, d=1/self.sample_rate)
        
        # Crear máscara combinada para múltiples rangos
        mask = np.zeros(len(freqs), dtype=bool)
        for low, high in ranges:
            mask |= (freqs >= low) & (freqs <= high)
        
        filtered_spectrum = spectrum * mask
        # IFFT
        filtered_audio = np.fft.irfft(filtered_spectrum, n=n)
        return filtered_audio

    def __init__(self, entrenador=None):
        self.entrenador = entrenador
        self.audio_data = None
        self.sample_rate = None
        self.file_path = None
        
    def load_audio(self, file_path):
        """Cargar archivo de audio"""
        try:
            self.file_path = file_path
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None, mono=True)
            return True, f"Audio cargado: {len(self.audio_data)/self.sample_rate:.2f}s"
        except Exception as e:
            return False, f"Error al cargar audio: {str(e)}"
    
    def analyze_segments(self, window_size=2.0):
        """Analizar audio en segmentos con clasificación"""
        if self.audio_data is None:
            return None, "No hay audio cargado"
        
        if self.entrenador is None or self.entrenador.modelo is None:
            return None, "No hay modelo cargado"
        
        samples_per_window = int(window_size * self.sample_rate)
        num_windows = int(len(self.audio_data) / samples_per_window)
        
        segments = []
        
        # Guardar temporalmente el audio como archivo para procesarlo
        import tempfile
        import os
        
        for i in range(num_windows):
            start_idx = i * samples_per_window
            end_idx = start_idx + samples_per_window
            
            segment_audio = self.audio_data[start_idx:end_idx]
            start_time = start_idx / self.sample_rate
            end_time = end_idx / self.sample_rate
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                sf.write(tmp_path, segment_audio, self.sample_rate)
            
            try:
                # Extraer características usando el método del entrenador
                features = self.entrenador.extraer_caracteristicas_yamnet(tmp_path)
                
                if features is not None:
                    # Asegurar que features tenga la forma correcta (1, n_features)
                    if len(features.shape) == 1:
                        features = features.reshape(1, -1)
                    
                    # Predecir usando el modelo (RandomForest)
                    # predict_proba devuelve probabilidades para cada clase
                    probabilidades = self.entrenador.modelo.predict_proba(features)[0]
                    clase_idx = np.argmax(probabilidades)
                    confianza = float(probabilidades[clase_idx])
                    clase = self.entrenador.class_names[clase_idx]
                    
                    segments.append({
                        'start': start_time,
                        'end': end_time,
                        'start_idx': start_idx,
                        'end_idx': end_idx,
                        'clase': clase,
                        'confianza': confianza,
                        'probabilidades': probabilidades.tolist()
                    })
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        return segments, None
    
    def filter_by_class(self, segments, selected_classes):
        """Filtrar segmentos por clases seleccionadas"""
        return [seg for seg in segments if seg['clase'] in selected_classes]
    
    def filter_by_confidence(self, segments, min_confidence=0.5):
        """Filtrar segmentos por confianza mínima"""
        return [seg for seg in segments if seg['confianza'] >= min_confidence]
    
    def filter_unknown(self, segments, threshold=0.5):
        """Filtrar segmentos desconocidos (baja confianza)"""
        return [seg for seg in segments if seg['confianza'] < threshold]
    
    def export_segments(self, segments, output_dir, prefix="segment", apply_isolation=False, filter_mode='keep_motors'):
        """Exportar segmentos seleccionados como archivos individuales.
        
        Args:
            segments: Lista de segmentos a exportar
            output_dir: Directorio de salida
            prefix: Prefijo para los nombres de archivo
            apply_isolation: Si True, aísla el audio según la clase detectada usando FFT/IFFT
            filter_mode: Modo de filtrado ('keep_motors', 'keep_all_vehicle', 'custom')
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = []

        for i, seg in enumerate(segments, 1):
            # Extraer audio del segmento
            segment_audio = self.audio_data[seg['start_idx']:seg['end_idx']]

            # Aislar el audio según la clase detectada si está activado
            if apply_isolation:
                segment_audio = self.isolate_by_class(segment_audio, seg['clase'], filter_mode)

            # Nombre del archivo
            clase = seg['clase'].replace(' ', '_')
            confianza = int(seg['confianza'] * 100)
            suffix = f"_{filter_mode}" if apply_isolation else ""
            filename = f"{prefix}_{i:03d}_{clase}_{confianza}pct{suffix}.wav"
            filepath = output_path / filename

            # Guardar archivo
            sf.write(str(filepath), segment_audio, self.sample_rate)
            exported_files.append(str(filepath))

        return exported_files
    
    def merge_segments(self, segments):
        """Unir segmentos consecutivos de la misma clase"""
        if not segments:
            return []
        
        merged = []
        current = segments[0].copy()
        
        for seg in segments[1:]:
            # Si es la misma clase y es consecutivo
            if (seg['clase'] == current['clase'] and 
                abs(seg['start'] - current['end']) < 0.1):
                # Extender el segmento actual
                current['end'] = seg['end']
                current['end_idx'] = seg['end_idx']
                # Promediar confianza
                current['confianza'] = (current['confianza'] + seg['confianza']) / 2
            else:
                # Guardar el actual y empezar uno nuevo
                merged.append(current)
                current = seg.copy()
        
        merged.append(current)
        return merged
    
    def export_merged_audio(self, segments, output_file):
        """Exportar audio concatenado de segmentos seleccionados"""
        if not segments:
            return False, "No hay segmentos para exportar"
        
        # Concatenar audio de todos los segmentos
        merged_audio = []
        for seg in segments:
            segment_audio = self.audio_data[seg['start_idx']:seg['end_idx']]
            merged_audio.append(segment_audio)
        
        # Unir todo
        final_audio = np.concatenate(merged_audio)
        
        # Guardar
        try:
            sf.write(output_file, final_audio, self.sample_rate)
            return True, f"Audio exportado: {len(final_audio)/self.sample_rate:.2f}s"
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"
    
    def export_full_audio_filtered(self, output_file, filter_mode='keep_motors', target_class='auto'):
        """Exportar el audio completo filtrado para mantener solo sonidos de motores/vehículos.
        
        Args:
            output_file: Ruta del archivo de salida
            filter_mode: Modo de filtrado ('keep_motors', 'keep_all_vehicle', 'custom')
            target_class: Clase objetivo para el filtrado ('auto', 'trafico', 'trafico pesado')
        """
        if self.audio_data is None:
            return False, "No hay audio cargado"
        
        try:
            # Aplicar el filtro a todo el audio
            filtered_audio = self.isolate_by_class(self.audio_data, target_class, filter_mode)
            
            # Guardar
            sf.write(output_file, filtered_audio, self.sample_rate)
            
            mode_names = {
                'keep_motors': 'solo motores',
                'keep_all_vehicle': 'todo el vehículo',
                'custom': 'personalizado'
            }
            mode_name = mode_names.get(filter_mode, 'filtrado')
            
            return True, f"Audio completo exportado ({mode_name}): {len(filtered_audio)/self.sample_rate:.2f}s"
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"
    
    def apply_frequency_filter(self, low_freq=None, high_freq=None):
        """Aplicar filtro de frecuencias al audio completo"""
        if self.audio_data is None:
            return False, "No hay audio cargado"
        
        filtered = self.audio_data.copy()
        
        # Filtro pasa-altos
        if low_freq:
            sos = signal.butter(10, low_freq, 'hp', fs=self.sample_rate, output='sos')
            filtered = signal.sosfilt(sos, filtered)
        
        # Filtro pasa-bajos
        if high_freq:
            sos = signal.butter(10, high_freq, 'lp', fs=self.sample_rate, output='sos')
            filtered = signal.sosfilt(sos, filtered)
        
        self.audio_data = filtered
        return True, f"Filtro aplicado: {low_freq or 0}-{high_freq or 'max'} Hz"
    
    def export_metadata(self, segments, output_file):
        """Exportar metadatos de los segmentos"""
        metadata = {
            'file': str(self.file_path),
            'sample_rate': self.sample_rate,
            'duration': len(self.audio_data) / self.sample_rate,
            'export_date': datetime.now().isoformat(),
            'segments': [
                {
                    'id': i,
                    'start': f"{int(seg['start']//60):02d}:{seg['start']%60:05.2f}",
                    'end': f"{int(seg['end']//60):02d}:{seg['end']%60:05.2f}",
                    'duration': seg['end'] - seg['start'],
                    'class': seg['clase'],
                    'confidence': round(seg['confianza'], 4)
                }
                for i, seg in enumerate(segments, 1)
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return True, f"Metadatos exportados: {len(segments)} segmentos"

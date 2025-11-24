"""
📊 ANALIZADOR FFT PARA AUDIO
=============================
Análisis espectral y visualización de frecuencias
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal
import os

class FFTAnalyzer:
    """Analizador de espectro de frecuencias usando FFT"""
    
    def __init__(self):
        self.sr = 16000  # Sample rate
        
    def load_audio(self, audio_path):
        """Cargar archivo de audio"""
        audio, sr = librosa.load(audio_path, sr=self.sr)
        return audio, sr
    
    def compute_fft(self, audio):
        """Calcular FFT del audio"""
        # Aplicar ventana de Hamming para reducir fugas espectrales
        windowed = audio * np.hamming(len(audio))
        
        # Calcular FFT
        fft_values = np.fft.rfft(windowed)
        fft_magnitude = np.abs(fft_values)
        
        # Calcular frecuencias correspondientes
        freqs = np.fft.rfftfreq(len(audio), 1/self.sr)
        
        return freqs, fft_magnitude
    
    def compute_spectrogram(self, audio):
        """Calcular espectrograma (FFT en ventanas de tiempo)"""
        # Parámetros del espectrograma
        nperseg = 2048  # Tamaño de ventana
        noverlap = nperseg // 2  # 50% solapamiento
        
        # Calcular espectrograma usando STFT (Short-Time Fourier Transform)
        freqs, times, Sxx = signal.spectrogram(
            audio, 
            fs=self.sr,
            nperseg=nperseg,
            noverlap=noverlap
        )
        
        # Convertir a escala logarítmica (dB)
        Sxx_db = 10 * np.log10(Sxx + 1e-10)
        
        return freqs, times, Sxx_db
    
    def get_dominant_frequencies(self, audio, n_top=5):
        """Obtener las frecuencias dominantes"""
        freqs, magnitude = self.compute_fft(audio)
        
        # Encontrar picos
        peaks, properties = signal.find_peaks(magnitude, height=np.max(magnitude)*0.1)
        
        # Ordenar por magnitud
        peak_magnitudes = magnitude[peaks]
        sorted_indices = np.argsort(peak_magnitudes)[::-1][:n_top]
        
        dominant_freqs = freqs[peaks[sorted_indices]]
        dominant_mags = peak_magnitudes[sorted_indices]
        
        return list(zip(dominant_freqs, dominant_mags))
    
    def analyze_frequency_bands(self, audio):
        """Analizar energía en bandas de frecuencia"""
        freqs, magnitude = self.compute_fft(audio)
        
        # Definir bandas de frecuencia
        bands = {
            'Sub-graves (20-60 Hz)': (20, 60),
            'Graves (60-250 Hz)': (60, 250),
            'Medios bajos (250-500 Hz)': (250, 500),
            'Medios (500-2000 Hz)': (500, 2000),
            'Medios altos (2-4 kHz)': (2000, 4000),
            'Agudos (4-8 kHz)': (4000, 8000)
        }
        
        band_energy = {}
        for band_name, (low, high) in bands.items():
            # Encontrar índices de frecuencias en este rango
            mask = (freqs >= low) & (freqs <= high)
            # Calcular energía total en la banda
            energy = np.sum(magnitude[mask])
            band_energy[band_name] = energy
        
        return band_energy
    
    def create_spectrum_plot(self, audio, title="Espectro de Frecuencias"):
        """Crear gráfico del espectro de frecuencias"""
        freqs, magnitude = self.compute_fft(audio)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Convertir a dB
        magnitude_db = 20 * np.log10(magnitude + 1e-10)
        
        ax.plot(freqs, magnitude_db, linewidth=0.8, color='#2196F3')
        ax.fill_between(freqs, magnitude_db, alpha=0.3, color='#2196F3')
        ax.set_xlabel('Frecuencia (Hz)', fontsize=10)
        ax.set_ylabel('Magnitud (dB)', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 8000)  # Limitar a frecuencias audibles relevantes
        
        # <-- AQUÍ AGREGA LA ECUACIÓN:
        plt.text(0.05, 0.95,
            r"$X_k = \sum_{n=0}^{N-1} x_n \cdot e^{-2\pi i \frac{kn}{N}}$",
            fontsize=14, transform=plt.gca().transAxes, verticalalignment='top')
        
        plt.tight_layout()
        return fig
    
    def create_spectrogram_plot(self, audio, title="Espectrograma"):
        """Crear espectrograma visual"""
        freqs, times, Sxx_db = self.compute_spectrogram(audio)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Crear espectrograma
        im = ax.pcolormesh(times, freqs, Sxx_db, shading='gouraud', cmap='viridis')
        ax.set_ylabel('Frecuencia (Hz)', fontsize=10)
        ax.set_xlabel('Tiempo (s)', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylim(0, 8000)  # Limitar a frecuencias relevantes
        
        # Agregar barra de color
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Intensidad (dB)', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def create_band_energy_plot(self, audio, title="Energía por Banda de Frecuencia"):
        """Crear gráfico de energía por banda"""
        band_energy = self.analyze_frequency_bands(audio)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        bands = list(band_energy.keys())
        energies = list(band_energy.values())
        
        # Normalizar energías
        total_energy = sum(energies)
        energies_pct = [e/total_energy*100 for e in energies]
        
        colors = ['#f44336', '#ff9800', '#ffeb3b', '#4caf50', '#2196f3', '#9c27b0']
        bars = ax.barh(bands, energies_pct, color=colors, alpha=0.8)
        
        ax.set_xlabel('Energía (%)', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Agregar valores en las barras
        for i, (bar, val) in enumerate(zip(bars, energies_pct)):
            ax.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def compare_spectrograms(self, audio_paths, labels):
        """Comparar espectrogramas de múltiples audios"""
        n_audios = len(audio_paths)
        fig, axes = plt.subplots(n_audios, 1, figsize=(10, 3*n_audios))
        
        if n_audios == 1:
            axes = [axes]
        
        for i, (audio_path, label) in enumerate(zip(audio_paths, labels)):
            audio, _ = self.load_audio(audio_path)
            freqs, times, Sxx_db = self.compute_spectrogram(audio)
            
            im = axes[i].pcolormesh(times, freqs, Sxx_db, shading='gouraud', cmap='viridis')
            axes[i].set_ylabel('Frecuencia (Hz)', fontsize=9)
            axes[i].set_title(label, fontsize=10, fontweight='bold')
            axes[i].set_ylim(0, 8000)
            
            if i == n_audios - 1:
                axes[i].set_xlabel('Tiempo (s)', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def get_analysis_summary(self, audio_path):
        """Obtener resumen completo del análisis"""
        audio, sr = self.load_audio(audio_path)
        
        # Frecuencias dominantes
        dominant = self.get_dominant_frequencies(audio, n_top=5)
        
        # Energía por banda
        band_energy = self.analyze_frequency_bands(audio)
        
        # Estadísticas
        duration = len(audio) / sr
        
        summary = {
            'duracion': duration,
            'sample_rate': sr,
            'frecuencias_dominantes': dominant,
            'energia_bandas': band_energy
        }
        
        return summary

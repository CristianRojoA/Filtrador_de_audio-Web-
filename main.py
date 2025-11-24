import os
from datetime import datetime
from entrenador_personalizado import EntrenadorPersonalizado

def main():
    """Función principal interactiva"""
    print("🎯 ENTRENADOR DE CLASIFICADOR PERSONALIZADO")
    print("="*60)
    print("🚀 ¡Entrena tu propio clasificador de sonidos urbanos!")
    print()
    
    entrenador = EntrenadorPersonalizado()
    
    while True:
        print("\n🔧 ¿QUÉ QUIERES HACER?")
        print("="*40)
        print("1️⃣ 📁 Crear estructura de carpetas")
        print("2️⃣ 🔍 Verificar datos disponibles")
        print("3️⃣ 🧠 Entrenar nuevo modelo")
        print("4️⃣ 📂 Cargar modelo existente")
        print("5️⃣ 🎵 Predecir archivo de audio (simple)")
        print("6️⃣ ⏰ Análisis temporal (cuándo pasa cada evento)")
        print("7️⃣ 📊 Ver modelos guardados")
        print("8️⃣ 🚪 Salir")
        
        try:
            opcion = input("\n👉 Elige una opción (1-8): ").strip()
            
            if opcion == "1":
                categorias = entrenador.crear_estructura_datos()
                print(f"\n✅ ¡Estructura creada! Ahora agrega archivos a las {len(categorias)} carpetas")
                
            elif opcion == "2":
                entrenador.verificar_datos()
                
            elif opcion == "3":
                print("\n🧠 Iniciando entrenamiento...")
                if entrenador.entrenar_modelo():
                    print("\n🎉 ¡Modelo entrenado exitosamente!")
                else:
                    print("\n😞 El entrenamiento falló")
                    
            elif opcion == "4":
                if entrenador.cargar_modelo_entrenado():
                    print("\n✅ ¡Modelo cargado y listo para usar!")
                else:
                    print("\n😞 No se pudo cargar el modelo")
                    
            elif opcion == "5":
                if not hasattr(entrenador, 'modelo'):
                    print("⚠️ Primero debes cargar un modelo (opción 4)")
                    continue
                    
                archivo = input("📁 Ruta del archivo de audio: ").strip().strip('"')
                if archivo and os.path.exists(archivo):
                    resultado = entrenador.predecir_audio(archivo)
                    if resultado:
                        print(f"\n🎯 ¡Predicción completada!")
                else:
                    print("❌ Archivo no encontrado")
            
            elif opcion == "6":
                if not hasattr(entrenador, 'modelo'):
                    print("⚠️ Primero debes cargar un modelo (opción 4)")
                    continue
                
                archivo = input("📁 Ruta del archivo de audio: ").strip().strip('"')
                if archivo and os.path.exists(archivo):
                    print("\n⚙️ Configuración del análisis:")
                    ventana_input = input("   Ventana de análisis en segundos [2.0]: ").strip()
                    
                    # Validar entrada numérica
                    try:
                        ventana = float(ventana_input) if ventana_input else 2.0
                        if ventana <= 0:
                            print("⚠️ Usando valor por defecto de 2.0 segundos")
                            ventana = 2.0
                    except ValueError:
                        print("⚠️ Valor inválido. Usando valor por defecto de 2.0 segundos")
                        ventana = 2.0
                    
                    resultado = entrenador.predecir_audio_temporal(
                        archivo, 
                        ventana_segundos=ventana
                    )
                    
                    if resultado:
                        # Preguntar si quiere exportar
                        exportar = input("\n💾 ¿Exportar resultados a JSON? (s/n): ").strip().lower()
                        if exportar == 's':
                            entrenador.exportar_detecciones_json(resultado)
                else:
                    print("❌ Archivo no encontrado")
                    
            elif opcion == "7":
                modelo_dir = "modelo_personalizado"
                if os.path.exists(modelo_dir):
                    modelos = [f for f in os.listdir(modelo_dir) if f.startswith('clasificador_')]
                    if modelos:
                        print(f"\n📊 Modelos guardados ({len(modelos)}):")
                        for i, modelo in enumerate(sorted(modelos), 1):
                            timestamp = modelo.replace('clasificador_', '').replace('.pkl', '')
                            fecha = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                            print(f"   [{i}] {modelo} (creado: {fecha.strftime('%Y-%m-%d %H:%M')})")
                    else:
                        print("📭 No hay modelos guardados")
                else:
                    print("📭 No existe directorio de modelos")
                    
            elif opcion == "8":
                print("\n👋 ¡Hasta luego! Happy coding! 🚀")
                break
                
            else:
                print("❌ Opción inválida. Usa números 1-8")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
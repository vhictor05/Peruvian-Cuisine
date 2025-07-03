import subprocess
import sys
import atexit
import os
import time
import webbrowser

# Lista para mantener los procesos hijos
child_processes = []

def start_process(command):
    """Inicia un proceso y lo añade a la lista de procesos hijos."""
    # Determinar las creationflags para Windows para evitar que Ctrl+C en la consola del launcher mate a los hijos.
    # En Linux, el comportamiento por defecto es generalmente adecuado.
    kwargs = {}
    if sys.platform == "win32":
        kwargs['creationflags'] = subprocess.CREATE_NEW_CONSOLE

    process = subprocess.Popen([sys.executable, command], **kwargs)
    child_processes.append(process)
    print(f"Proceso iniciado: {command} (PID: {process.pid})")
    return process

def cleanup_processes():
    """Termina todos los procesos hijos al salir."""
    print("Cerrando procesos hijos...")
    for process in child_processes:
        if process.poll() is None:  # Verificar si el proceso aún está en ejecución
            print(f"Terminando proceso {process.pid}...")
            process.terminate()  # Envía SIGTERM
            try:
                process.wait(timeout=5)  # Espera un poco a que termine
                print(f"Proceso {process.pid} terminado.")
            except subprocess.TimeoutExpired:
                print(f"Proceso {process.pid} no terminó a tiempo, forzando cierre...")
                process.kill()  # Envía SIGKILL si no termina con SIGTERM
                print(f"Proceso {process.pid} forzado a cerrar.")
        else:
            print(f"Proceso {process.pid} ya había terminado.")
    print("Limpieza de procesos hijos completada.")

# Registrar la función de limpieza para que se ejecute al salir
atexit.register(cleanup_processes)

if __name__ == "__main__":
    # Obtener la ruta del directorio actual del script launcher.py
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construir las rutas absolutas para app.py y api/app.py
    app_gui_path = os.path.join(current_dir, "app.py")
    app_api_path = os.path.join(current_dir, "api", "app.py")

    print(f"Iniciando GUI desde: {app_gui_path}")
    print(f"Iniciando API desde: {app_api_path}")

    # Comandos para iniciar los scripts
    command_gui = app_gui_path
    command_api = app_api_path

    # Iniciar los procesos
    process_gui = start_process(command_gui)
    process_api = start_process(command_api)

    # Esperar 2 segundos y abrir el navegador
    if process_api:
        print("Esperando 2 segundos antes de abrir el navegador para la documentación de la API...")
        time.sleep(2)
        try:
            webbrowser.open("http://127.0.0.1:8000/docs")
            print("Navegador abierto en http://127.0.0.1:8000/docs")
        except Exception as e:
            print(f"No se pudo abrir el navegador: {e}")

    print("Ambos procesos han sido iniciados.")
    print("El lanzador permanecerá activo. Cierra esta ventana o presiona Ctrl+C para terminar todos los procesos.")

    # Mantener el script principal en ejecución
    # Esperar a que los procesos terminen solo si queremos que el launcher dependa de ellos.
    # En este caso, queremos que el launcher controle a los hijos, así que simplemente esperamos una interrupción.
    try:
        # Esperamos a que ambos procesos terminen.
        # Si uno de los procesos es cerrado manualmente por el usuario, process.wait() retornará.
        # Si el launcher es interrumpido (Ctrl+C), la función de atexit se encargará de los hijos.
        if process_gui:
            process_gui.wait()
        if process_api:
            process_api.wait()
    except KeyboardInterrupt:
        print("Lanzador interrumpido por el usuario (Ctrl+C).")
    except Exception as e:
        print(f"Ocurrió un error en el lanzador: {e}")
    finally:
        # La limpieza se realiza mediante atexit, así que no es estrictamente necesario aquí,
        # pero puede ser útil si atexit no se dispara en todos los escenarios (ej. kill -9 en Linux).
        # Sin embargo, atexit es bastante robusto para señales normales de terminación.
        print("Saliendo del lanzador.")

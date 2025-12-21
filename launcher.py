"""
SW BALOTO Launcher
Starts the Flask server and automatically opens the browser
"""
import webbrowser
import threading
import time
from app import app

def open_browser():
    """Wait for server to start, then open browser"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.2:5000')

if __name__ == '__main__':
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask server
    print("=" * 50)
    print("SW BALOTO - Analizador de Resultados de Lotería")
    print("=" * 50)
    print("\nIniciando servidor...")
    print("La aplicación se abrirá automáticamente en tu navegador.")
    print("\nPara cerrar la aplicación, cierra esta ventana.")
    print("=" * 50)
    
    app.run(debug=False, port=5000, host='127.0.0.2', use_reloader=False)

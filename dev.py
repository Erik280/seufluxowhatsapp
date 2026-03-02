import subprocess
import time
import sys
import os

def run_dev():
    print("🚀 Iniciando WhatsApp Atendimento SaaS...")
    
    # Inicia o Backend
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print("⏳ Aguardando backend iniciar...")
    time.sleep(3)
    
    # Inicia o Frontend
    frontend = subprocess.Popen(
        [sys.executable, "frontend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print("✅ Sistema rodando!")
    print("📡 API: http://localhost:8000")
    print("🌐 Frontend: http://localhost:8080")
    
    try:
        while True:
            # Mantém processo rodando e printa logs se necessário
            line = backend.stdout.readline()
            if line:
                print(f"[Backend] {line.strip()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Encerrando processos...")
        backend.terminate()
        frontend.terminate()
        print("Bye!")

if __name__ == "__main__":
    run_dev()

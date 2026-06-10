import time
from playwright.sync_api import sync_playwright

def guardar_sesion():
    
    with sync_playwright() as p:
        
        # Iniciamos el navegador visible (headless=False)
        # 'user_data_dir' creará una carpeta donde se guardará tu sesión (como el perfil de Chrome)
        
        context = p.chromium.launch_persistent_context('sesion_usuario', headless=False, accept_downloads=True)
        page = context.new_page()
        
        # URL de login de tu página de envíos
        print("🌐 Abriendo la página... Por favor, inicia sesión manualmente.")
        page.goto("https://certi.fivesoftcolombia.com/loginfp")
        
        print("\n⏳ El navegador está listo. Tienes hasta 5 minutos para loguearte.")
        print("👉 IMPORTANTE: Cuando termines de loguearte, NO cierres el navegador con la 'X'.")
        print("👉 Presiona ENTER aquí en la terminal/consola para cerrar todo correctamente.\n")
        
        # En lugar de esperar a que cierres la ventana, el script espera a que presiones ENTER en la consola
        input("¿Ya iniciaste sesión? Presiona ENTER aquí para guardar y cerrar: ")
        
        # Cierre ordenado para evitar el error de Windows (ValueError: I/O operation on closed pipe)
        print("💾 Guardando sesión y cerrando de forma segura...")
        context.close()     # Te da hasta 5 minutos para loguearte  
        
if __name__ == "__main__":
    guardar_sesion()  
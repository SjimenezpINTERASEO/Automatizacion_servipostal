import os 
import time
import pandas as pd


ruta_excel=r"C:\Users\santiago.jimenez\Downloads\22-05-2026 CERTIFICADOS DE RECLAMO.xlsx"
tabla_excel= "CERTIFICADOS_OCOBOS"
columna_excel= "tagid"


FECHA_INICIO= "2026-05-22"
FECHA_FIN= "2026-05-22"

CARPETA_DESCARGA= os.path.join(os.getcwd(), FECHA_INICIO)

if not os.path.exists(CARPETA_DESCARGA):
    os.makedirs(CARPETA_DESCARGA)
    print(f"📁 Carpeta '{CARPETA_DESCARGA}' creada para almacenar los certificados descargados.")
    
def descargar_certificados():
    try:
        df=pd.read_excel(ruta_excel, sheet_name=tabla_excel)
        lista_guias = df[COLUMNA_GUIAS].dropna().astype(str).str.strip().tolist()
        print(f"📊 Total de guías ('tagid') cargadas desde {TABLA_EXCEL}: {len(lista_guias)}")
    except Exception as e:
        print(f"❌ Error al leer el Excel (Revisa el nombre del archivo o de la pestaña): {e}")
        return
    
    with sync_playwright() as p:
        
        context= p.chromium.launch_persistent_context('sesion_usuario', headless=False, accept_downloads=True)
        page= context.new_page()
        
        print("🌐 Abriendo el portal de reportes...")
        # ──> REEMPLAZA CON TU URL REAL
        page.goto("https://certi.fivesoftcolombia.com/dashboard")
        page.wait_for_load_state("networkidle")
        
        # PASOS INICIALES DE LA AUTOMATIZACION
        
        
########
        print("⏳ Aplicando filtros iniciales...")
        
        try:
            # 1. MODIFICACIÓN: Llenar fechas usando clases fijas e índices (evita IDs dinámicos)
            page.locator(".q-field__native.q-placeholder").nth(0).fill(FECHA_INICIO) # Inicio
            page.locator(".q-field__native.q-placeholder").nth(1).fill(FECHA_FIN)    # Fin
            print("  ├─ Fechas ingresadas correctamente.")
            
            page.click("#cuadro-texto-reportes") 
            page.click("//text()='ALL' or .//*[contains(text(), 'ALL')]") 
            print("🔄 Cargando toda la tabla gigante (ALL)...")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000) 
            
        except Exception as e:
            print(f"❌ Error en los pasos iniciales: {e}")
            context.close()
            return

        # ==========================================================
        # BUCLE PRINCIPAL (ITERACIÓN POR GUÍA / TAGID)
        # ==========================================================
        print("🤖 Iniciando procesamiento...")
        
        for i, guia in enumerate(lista_guias, start=1):
            print(f" [{i}/{len(lista_guias)}] Procesando tagid: {guia}")
            
            try:
                # PASO 4: Localizar fila usando el 'tagid' de la tabla web
                celda_guia = page.locator(f"//td[text()='{guia}']")
                if not celda_guia.is_visible():
                    print(f"  ⚠️ El tagid {guia} no está visible en la tabla web. Saltando...")
                    continue
                
                # PASO 5: Clic en desplegar menú de la fila (Cambiar '.clase-icono-desplegar')
                page.locator(f"//td[text()='{guia}']/..//*.clase-icono-desplegar").click()
                page.wait_for_timeout(1000) 

                # PASO 6: Abrir ventana emergente principal (Cambiar '.clase-icono-popup')
                with context.expect_page() as new_page_info:
                    page.locator(f"//td[text()='{guia}']/..//*.clase-icono-popup").click()
                ventana_emergente = new_page_info.value
                ventana_emergente.wait_for_load_state()

                # ==========================================================
                # PASO 7A: DESCARGAR CERTIFICACIÓN
                # ==========================================================
                print("  ├─ Generando PDF Certificación...")
                ventana_emergente.click("#generar-pdf-certificacion-de-guia")
                ventana_emergente.wait_for_timeout(1500)
                
                # Clic en el enlace "ya puede generar el pdf..." (Cambiar si el texto varía)
                with context.expect_page() as pdf_page_info:
                    ventana_emergente.click("text='ya puede generar el pdf de la certificación'")
                
                pag_pdf_cert = pdf_page_info.value
                
                with pag_pdf_cert.expect_download() as download_info1:
                    pass # Captura automática al abrir la pestaña
                
                download1 = download_info1.value
                ruta_cert = os.path.join(CARPETA_DESCARGAS, f"{guia}_certificacion.pdf")
                download1.save_as(ruta_cert)
                print(f"  ├─ ✅ Certificación guardada.")
                pag_pdf_cert.close()

                # ==========================================================
                # PASO 7B: DESCARGAR DOCUMENTOS CARGADOS
                # ==========================================================
                print("  ├─ Generando Documentos Cargados...")
                # ──> REEMPLAZA '#btn-documentos-cargados' con el ID real
                ventana_emergente.click("#btn-documentos-cargados")
                ventana_emergente.wait_for_timeout(1500)
                
                # Clic en "Ver" (Cambiar si el texto varía)
                with context.expect_page() as doc_page_info:
                    ventana_emergente.click("text='Ver'")
                
                pag_pdf_doc = doc_page_info.value
                
                with pag_pdf_doc.expect_download() as download_info2:
                    pass # Captura automática al abrir la pestaña
                
                download2 = download_info2.value
                ruta_doc = os.path.join(CARPETA_DESCARGAS, f"{guia}_documentos.pdf")
                download2.save_as(ruta_doc)
                print(f"  ├─ ✅ Documentos cargados guardados.")
                pag_pdf_doc.close()

                # Cerrar ventana intermedia
                ventana_emergente.close()
                print(f"  └─ Procesado con éxito.")

            except Exception as e:
                print(f"  ❌ Error procesando el tagid {guia}: {e}")
                try: ventana_emergente.close()
                except: pass
            
            time.sleep(1.5) 

        context.close()
        print(f"\n🎉 ¡Proceso completado! Los archivos están en la carpeta: '{FECHA_INICIO}'")

if __name__ == "__main__":
    iniciar_automatizacion()
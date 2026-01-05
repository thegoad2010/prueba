# PDF Vocalizer - Convertidor de PDF a Audio

Aplicación web moderna y completa para convertir documentos PDF a archivos de audio MP3, desarrollada con Python (Flask) y un diseño Premium.

## Características

- **Autenticación de Usuarios**: Registro y login seguro con historial personal.
- **Procesamiento Inteligente**: Extracción de texto, detección automática de idioma y metadatos.
- **Síntesis de Voz**: Generación de audio de alta calidad usando Google TTS.
- **Diseño Premium**: Interfaz moderna con estilo "Glassmorphism", modo oscuro y responsive.
- **Historial Completo**: Guarda tus conversiones, reproduce y descarga cuando quieras.

## Estructura del Proyecto

```
proyecto/
├── app.py              # Aplicación principal Flask
├── requirements.txt    # Dependencias
├── config.py           # Configuraciones
├── models.py           # Modelos de base de datos (Usuario, Conversión)
├── utils/              # Módulos de utilidad
│   ├── pdf_processor.py
│   ├── audio_generator.py
│   └── validators.py
├── templates/          # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── history.html
└── static/             # Archivos estáticos
    ├── css/
    ├── js/
    ├── uploads/        # Almacenamiento temporal de PDF
    └── audio/          # Almacenamiento permanente de MP3
```

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación Paso a Paso

1.  **Clonar o descargar el proyecto** en tu carpeta de trabajo.

2.  **Crear un entorno virtual** (recomendado):
    ```bash
    python -m venv venv
    
    # En Windows:
    venv\Scripts\activate
    
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración de Base de Datos**:
    La aplicación usa SQLite por defecto. La base de datos se creará automáticamente (`app.db`) al iniciar la aplicación por primera vez.

## Ejecución

1.  **Iniciar el servidor**:
    ```bash
    python app.py
    ```

2.  **Acceder a la aplicación**:
    Abre tu navegador y ve a: `http://127.0.0.1:5000`

## Uso

1.  **Regístrate** crea una cuenta nueva.
2.  **Sube un PDF**: Arrastra tu archivo al área designada (máximo 71 páginas).
3.  **Configura**: El sistema detectará el idioma. Selecciona la voz y confirma.
4.  **Escucha**: Espera a que la barra de progreso termine y reproduce tu audio o descárgalo.

## Notas Técnicas

- La velocidad de generación depende de la conexión a internet (para Google TTS).
- Los archivos PDF se eliminan tras el procesamiento (según lógica de limpieza implementable), los audios se mantienen.

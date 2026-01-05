# Guía de Publicación (Deployment) en Render.com

Esta guía te ayudará a publicar tu aplicación gratuitamente en internet usando **Render**.

## Paso 1: Subir código a GitHub

Si aún no lo has hecho, sube tu código a un repositorio de GitHub:

1.  Crea un nuevo repositorio en [github.com](https://github.com).
2.  En la carpeta de tu proyecto, inicia git y sube el código:
    ```bash
    git init
    git add .
    git commit -m "Primera versión lista para deploy"
    git branch -M main
    git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
    git push -u origin main
    ```

## Paso 2: Crear Web Service en Render

1.  Ve a [render.com](https://render.com) y crea una cuenta.
2.  En el Dashboard, haz clic en **"New +"** y selecciona **"Web Service"**.
3.  Conecta tu cuenta de GitHub y selecciona el repositorio que acabas de crear.
4.  Llena el formulario con estos datos:
    *   **Name**: Nombre de tu app (ej. `pdf-vocalizer-app`)
    *   **Region**: La más cercana (ej. Ohio, Frankfurt)
    *   **Branch**: `main`
    *   **Root Directory**: (Déjalo vacío)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app` (Debería detectarse automáticamente desde el `Procfile`)
    *   **Instance Type**: Free

5.  Haz clic en **"Create Web Service"**.

## Paso 3: Configurar Base de Datos (PostgreSQL)

Como Render reinicia los discos en el plan gratuito, necesitamos una base de datos externa para no perder los usuarios:

1.  En el Dashboard de Render, haz clic en **"New +"** y selecciona **"PostgreSQL"**.
2.  Ponle nombre (ej. `pdf-db`) y dale a **Create Database**.
3.  Cuando termine, copia la **"Internal Database URL"**.
4.  Vuelve a tu **Web Service** (el que creaste en el paso 2).
5.  Ve a la pestaña **"Environment"**.
6.  Añade las siguientes variables:
    *   Key: `DATABASE_URL` | Value: (Pega la URL de la base de datos que copiaste)
    *   Key: `SECRET_KEY` | Value: (Inventa una contraseña larga y segura)
    *   Key: `PYTHON_VERSION` | Value: `3.10.0`

## Paso 4: ¡Listo!

Render detectará los cambios y volverá a desplegar la aplicación. Cuando termine (verás "Live"), podrás acceder a tu app desde la URL que te asignen (ej. `https://pdf-vocalizer-app.onrender.com`).

**Nota Importante sobre Archivos**: 
En el plan gratuito de Render, los archivos subidos (PDFs y MP3s) se borrarán si el servidor se reinicia o 'duerme'. Para una solución permanente real, se debería integrar **AWS S3** o **Google Cloud Storage** para guardar los archivos. Por ahora, funcionará, pero ten en cuenta que los audios no son eternos en esta configuración gratuita.

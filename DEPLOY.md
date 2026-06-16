# Despliegue (acceso desde fuera)

El proyecto tiene 3 piezas: **frontend** (React), **backend** (FastAPI) y **MongoDB**.
La configuración ya no está hardcodeada: las URLs se inyectan por variables de entorno,
así que se puede desplegar en cualquier PaaS.

Variables clave:

| Servicio | Variable | Para qué sirve |
|----------|----------|----------------|
| backend  | `MONGO_URI` | URI de conexión a MongoDB |
| backend  | `CORS_ORIGINS` | Origen(es) permitidos. La URL pública del frontend, o `*` para abrir a todos |
| frontend | `REACT_APP_API_BASE_URL` | URL pública del backend (se hornea en el build) |

> ⚠️ `REACT_APP_API_BASE_URL` se usa **en tiempo de build**. Si la cambias, hay que
> reconstruir el frontend.

---

## Opción A — Railway (recomendada, MongoDB persistente incluido)

1. Entra en https://railway.app y crea un proyecto desde el repo de GitHub.
2. **Añade MongoDB**: botón *New → Database → Add MongoDB*. Railway crea la base de
   datos con un **volumen persistente** y expone la variable `MONGO_URL`.
3. **Servicio backend**:
   - *New → GitHub Repo*, raíz `/backend` (Root Directory = `backend`).
   - Variables:
     - `MONGO_URI` = referencia a `${{MongoDB.MONGO_URL}}`
     - `CORS_ORIGINS` = `*` (o luego la URL exacta del frontend)
   - Railway detecta el `Dockerfile` y asigna `PORT` automáticamente.
   - Activa *Generate Domain* para obtener la URL pública (ej. `https://backend-xxx.up.railway.app`).
4. **Servicio frontend**:
   - *New → GitHub Repo*, Root Directory = `frontend`.
   - Variable: `REACT_APP_API_BASE_URL` = la URL pública del backend del paso anterior.
   - *Generate Domain* para obtener la URL pública del frontend.
5. (Opcional pero recomendado) Vuelve al backend y pon `CORS_ORIGINS` = la URL pública
   del frontend para no dejar el CORS abierto.

Listo: abre la URL del frontend desde cualquier sitio.

---

## Opción B — Render

Render no gestiona MongoDB, así que usa **MongoDB Atlas** (free tier) para los datos:

1. Crea un cluster gratis en https://www.mongodb.com/atlas y copia su connection string.
2. En https://render.com crea dos *Web Services* desde el repo (runtime = Docker):
   - **backend**: Root Directory `backend`. Env:
     - `MONGO_URI` = connection string de Atlas
     - `CORS_ORIGINS` = URL pública del frontend (o `*`)
   - **frontend**: Root Directory `frontend`. Env (marcar como *available at build time*):
     - `REACT_APP_API_BASE_URL` = URL pública del backend
3. Render asigna `PORT` automáticamente; los Dockerfiles ya lo respetan.

---

## Local (Docker Compose)

Para probar en tu máquina, sigue funcionando igual y ahora Mongo **persiste** los datos:

```bash
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000/docs

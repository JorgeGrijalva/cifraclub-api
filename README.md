# Cifra Club API

REST API para obtener cifras (acordes) de canciones desde [Cifra Club](https://www.cifraclub.com.br), disponibles en formato JSON.

El endpoint `/artists/:artist/songs/:song` utiliza Selenium para navegar la página web y extraer la cifra y los metadatos de la canción.

---

## 🚀 Cómo ejecutar el proyecto

Asegúrate de tener **Docker** y **Docker Compose** instalados. Luego ejecuta:

```bash
docker-compose build
docker-compose up
```

Por defecto, la API queda disponible en [http://localhost:3000](http://localhost:3000).

### Cambiar el puerto

Puedes cambiar el puerto usando la variable de entorno `PORT`:

```bash
PORT=3001 docker-compose up
```

O con Makefile:

```bash
make up
```

---

## 📖 Documentación interactiva (Swagger UI)

Una vez que el proyecto esté corriendo, puedes acceder a la documentación interactiva en:

```
http://localhost:3000/apidocs
```

Desde allí puedes explorar los endpoints y probarlos directamente en el navegador.

---

## 🎸 Cómo obtener una cifra

Con el proyecto corriendo, abre el navegador en:

```
http://localhost:3000/artists/coldplay/songs/the-scientist
```

O desde la terminal:

```bash
curl http://localhost:3000/artists/coldplay/songs/the-scientist
```

### Respuesta exitosa (`200 OK`)

```json
{
  "artist": "Coldplay",
  "name": "The Scientist",
  "youtube_url": "https://www.youtube.com/watch?v=RB-RcX5DS5A",
  "cifraclub_url": "https://www.cifraclub.com.br/coldplay/the-scientist",
  "cifra": [
    "[Intro]  C#m7  A9  E  E9",
    "",
    "C#m7             A9",
    "     Come up to meet you",
    "...",
    "[Refrão]",
    "...",
    "Nobody said it was easy"
  ]
}
```

### Canción no encontrada (`404 Not Found`)

```json
{
  "error": "Song or artist not found or could not be parsed.",
  "details": "Failed to extract cifra from https://www.cifraclub.com.br/..."
}
```

### Error interno (`500 Internal Server Error`)

```json
{
  "error": "Internal server error while processing the request.",
  "details": "..."
}
```

---

## ⚙️ Variables de entorno

| Variable       | Descripción                                               | Default                          |
|----------------|-----------------------------------------------------------|----------------------------------|
| `PORT`         | Puerto expuesto por la API Flask                          | `3000`                           |
| `SELENIUM_URL` | URL del servidor Selenium remoto                          | `http://selenium:4444/wd/hub`    |

---

## 📦 Stack

- **Python 3.8** + **Flask 2.2.2**
- **Selenium 4.6.0** con Firefox (Selenium Grid)
- **BeautifulSoup4** para parsear el HTML
- **Flasgger** para la documentación Swagger/OpenAPI

---

## 🛠️ Desarrollo

### Lint

```bash
make lint
```

### Tests

```bash
make test
```

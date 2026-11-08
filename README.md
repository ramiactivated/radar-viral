# Radar Viral 📈

Web que muestra cada día, con datos reales de YouTube:

- Los vídeos en tendencia de España y EE. UU., ordenados por visitas por hora.
- Creadores parecidos a tu canal.
- Los vídeos más vistos del último mes en tu temática.

Se actualiza sola todos los días a las 06:00 UTC con GitHub Actions y se publica con GitHub Pages.

## Cambiar el canal o la temática

Edita `config.json`:
- `handle`: tu @ de YouTube.
- `channel_queries`: búsquedas para encontrar canales parecidos.
- `video_queries`: búsquedas para encontrar virales de tu tipo.
- `keywords`: palabras que tiene que tener un vídeo en el título para contar como "de tu tipo".

## Actualizar a mano

Pestaña **Actions** → **Actualizar Radar Viral** → **Run workflow**.

La clave de la API de YouTube está guardada como secreto `YT_API_KEY` (Settings → Secrets and variables → Actions).

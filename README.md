# NES Arcade — catálogo de cartuchos

Origen de descargas para el portal cautivo **NES Arcade** (Wemos D1 mini + ESP8266).
El dispositivo levanta su propia red WiFi, sirve un emulador NES a quien se conecte,
y opcionalmente se conecta a una red con internet para traer cartuchos nuevos de aquí.

Publicado en <https://zerogapcode.github.io/nes-arcade/>.

## Estructura

```
index.html       catálogo navegable (personas)
catalogo.json    índice (dispositivo)
covers/*.jpg     carátulas 224x320
roms/*.nes       cartuchos
```

## catalogo.json

```json
{
  "version": 1,
  "actualizado": "2026-08-29",
  "base": "https://zerogapcode.github.io/nes-arcade/",
  "juegos": [
    {
      "id": "contra",
      "nombre": "Contra",
      "rom": "roms/Contra.nes",
      "bytes": 131088,
      "md5": "7bdad8b4a7a56a634c9649d20bd3011b",
      "caratula": "covers/contra.jpg",
      "caratula_bytes": 29626
    }
  ]
}
```

Las rutas son relativas a `base`. `bytes` permite al dispositivo comprobar que le queda
sitio en LittleFS antes de empezar, y `md5` que el archivo llegó completo — el ESP8266
calcula MD5 con `MD5Builder`, que ya viene en el core de Arduino.

## Notas para el firmware

- **TLS obligatorio.** GitHub Pages fuerza HTTPS y no negocia MFLN, así que BearSSL
  necesita el buffer completo de 16 KB (~22-25 KB de heap con el handshake). El equipo
  arranca con ~45 KB libres, así que conviene parar el servidor async durante la descarga.
- **TLS 1.2 con ECDHE-RSA-CHACHA20-POLY1305**, que es lo más barato para un chip sin
  acelerador AES. BearSSL no habla TLS 1.3.
- **Escribir en streaming**, en trozos de 512-1024 bytes. Una ROM de 384 KB no cabe en RAM.
- **Las carátulas ya vienen a 224x320**: el dispositivo las guarda tal cual, no las procesa.

## Añadir un cartucho

1. Copiar el `.nes` a `roms/` y la carátula (224x320, JPEG baseline) a `covers/`.
2. Regenerar `catalogo.json` con tamaños y MD5 actualizados.
3. Push a `main` — GitHub Pages publica la rama automáticamente.

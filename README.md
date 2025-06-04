# Learn English with Translations (LEwT)

Aplicación web para mejorar el nivel de inglés mediante la practica de traducciones de oraciones, verbos irregulares y verbos compuestos, con seguimiento de resultados y estadísticas.

---

## 📂 Estructura del proyecto

```text
learn-english-with-translations/       # Raíz del proyecto
├── app/                               # Paquete principal de la aplicación
│   ├── __init__.py                    # create_app(), registro de blueprints y extensiones
│   ├── database/                      # Scripts y lógica de acceso a datos
│   │   ├── __init__.py
│   │   ├── create_database.py         # Script de inicialización e inserción de datos
│   │   └── db.py                      # Función de conexión a SQLite
│   │
│   ├── routes/                        # Blueprints de Flask (módulos de rutas)
│   │   ├── __init__.py                # Registro de todos los blueprints
│   │   ├── main_routes.py             # Página principal
│   │   ├── sentences_routes.py        # Listado u ejercicios de frases
│   │   ├── irregular_verbs_routes.py  # Listado u ejercicios de verbos irregulares
│   │   └── phrasal_verbs_routes.py    # Listado u ejercicios de phrasal verbs
│   │
│   ├── static/                        # Archivos estáticos (CSS, imágenes)
│   │   ├── styles.css
│   │   └── logo.png
│   │
│   └── templates/                          # Plantillas para cada pantalla de la app
│       ├── main.html                       # Plantilla base
│       ├── home.html                       # Página de inicio con opciones de ejercicios
│       ├── header.html                     # Cabecera
│       ├── navbar.html                     # Barra de navegación
│       ├── footer.html                     # Pie de página
│       ├── sentences.html                  # Listado de oraciones
│       ├── irregular_verbs.html            # Listado de verbos irregulares
│       ├── phrasal_verbs.html              # Listado de verbos compuestos
│       ├── exercise.html                   # Ejercicio de oraciones
│       ├── exercise_irregular_verbs.html   # Ejercicio de verbos irregulares
│       ├── exercise_phrasal_verbs.html     # Ejercicio de verbos compuestos
│       ├── exercise_results.html           # Resultados de un ejercicio recién hecho de oraciones
│       └── past_exercise_results.html      # Resultados pasados de un ejercicio de oraciones
│
├── .gitignore
├── Makefile                           # Tareas: install, python-lib, create-db, run
├── requirements.txt                   # Dependencias de Python
├── run.py                             # Entrypoint: importa create_app y arranca la app
└── README.md                          # Documentación del proyecto
```

---

## 🚀 Instalación y configuración

A continuación, los pasos para configurar y ejecutar la aplicación en **Linux** y **Windows**.

### 1. Clonar el repositorio

```bash
git clone https://github.com/jesus-guijarro/learn-english-with-translations.git

cd learn-english-with-translations
```

### 2. Crear y activar el entorno virtual

**Linux (con Makefile)**
```bash
make env    # crea y activa el virtualenv lewtvenv
```

**Windows (PowerShell)**
```powershell
python -m venv lewtvenv

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process  # si es necesario

.\lewtvenv\Scripts\activate
```

### 3. Instalar dependencias

**Linux**
```bash
make python-lib   # actualiza pip e instala requirements.txt
```

**Windows**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```


### 4. Crear base de datos

**Linux**
```bash
make create-db   # ejecuta database/create_database.py
```

**Windows**
```powershell
cd database
python create_database.py
cd ..
```

---

## 💻 Ejecución de la aplicación

### En Linux:

```bash
make run    # inicia la app en http://localhost:5000
```

O bien:

```bash
source lewtvenv/bin/activate

python run.py
```

### En Windows:
Ejecuta el archivo lewt.bat haciendo doble clic:

```bash
lewt.bat
```

Por comodidad se puede crear un acceso directo (botón derecho-> Crear acceso directo) y usarlo desde el escritorio.

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
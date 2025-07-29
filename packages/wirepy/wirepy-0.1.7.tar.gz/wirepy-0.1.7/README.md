<!-- Logo -->
<p align="center">
  <svg width="444.6000000000001" height="120.16216216216218" viewBox="0 0 370 100" class="looka-1j8o68f"><defs id="SvgjsDefs1243"><linearGradient id="SvgjsLinearGradient1248"><stop id="SvgjsStop1249" stop-color="#00ff8f" offset="0"></stop><stop id="SvgjsStop1250" stop-color="#00a1ff" offset="1"></stop></linearGradient></defs><g id="SvgjsG1244" featurekey="odWo6G-0" transform="matrix(1.1111111111111112,0,0,1.1111111111111112,-5.555555555555555,-5.555555555555555)" fill="url(#SvgjsLinearGradient1248)"><path xmlns="http://www.w3.org/2000/svg" fill="url(#SvgjsLinearGradient1248)" d="M95,52c0-12.871-5.692-24.431-14.682-32.318C72.431,10.692,60.871,5,48,5C24.29,5,5,24.29,5,48  c0,12.868,5.69,24.426,14.677,32.313C27.564,89.306,39.126,95,52,95c0.084,0,0.166-0.006,0.25-0.006S52.416,95,52.5,95  C75.972,95,95,75.972,95,52.5c0-0.084-0.006-0.166-0.006-0.25S95,52.084,95,52z M21.828,73.371  c-4.245-5.978-6.77-13.259-6.822-21.121c0.135-20.511,16.732-37.109,37.244-37.244c7.862,0.052,15.144,2.577,21.121,6.822  C80.224,28.473,84.5,37.758,84.5,48c0,20.126-16.374,36.5-36.5,36.5C37.758,84.5,28.473,80.224,21.828,73.371z M6,48  C6,24.841,24.841,6,48,6c9.858,0,18.926,3.422,26.1,9.13C67.637,11.242,60.076,9,52,9C28.29,9,9,28.29,9,52  c0,8.074,2.241,15.633,6.127,22.095C9.421,66.923,6,57.856,6,48z M52,89c-10.08,0-19.227-4.055-25.905-10.615  C32.269,82.854,39.838,85.5,48,85.5c20.678,0,37.5-16.822,37.5-37.5c0-8.162-2.646-15.731-7.115-21.905  C84.945,32.773,89,41.92,89,52C89,72.402,72.402,89,52,89z"></path></g></svg>
</p>

# Wirepy

Wirepy is a Python project scaffolding tool designed to accelerate the development of FastAPI-based applications. It provides a command-line interface (CLI) to generate boilerplate code, manage migrations, and organize your project structure following best practices.

## Features
- **CLI Tooling**: Easily scaffold new FastAPI projects and components.
- **Project Templates**: Predefined templates for controllers, models, routes, schemas, services, and core utilities.
- **Database Integration**: Built-in support for database configuration and migrations using Alembic.
- **Environment Management**: Template for `.env` and requirements management.

## Folder Structure

```
── wirepy/
     ├── app/
     │   ├── controllers/
     │   ├── models/
     │   ├── routes/
     │   ├── schemas/
     │   ├── services/
     │   └── core/
     │       ├── config.py
     │       └── database.py
     ├── __init__.py
     ├── alembic/
     ├── alembic.ini
     ├── main.py
     ├── .env
     ├── requirements.txt
     └── README.md
```

## Installation

1. **Create a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Wirepy:**
   ```sh
   pip install wirepy
   ```
3. **Create a new project:**
   ```sh
   wirepy new <project-name>
   ```

<!-- ## Getting Started

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd wirepy
   ```
2. **Create a virtual environment:**
   ```sh
   python3 -m venv vvenv
   source vvenv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r wirepy/templates/requirements.txt
   ```
4. **Use the CLI to scaffold a new project or component:**
   ```sh
   python -m wirepy.cli <command> -->
   ```

## License

This project is licensed under the terms of the MIT License. See the `LICENSE` file for details.

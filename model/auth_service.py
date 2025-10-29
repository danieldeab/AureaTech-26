# auth_service.py
import json
import os
import hashlib

USUARIOS_FILE = "usuarios.json"

class AuthService:
    def __init__(self):
        self.usuarios = self._cargar_usuarios()
        self.intentos = {"count": 0, "max": 2}

    def _cargar_usuarios(self):
        if os.path.exists(USUARIOS_FILE):
            with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _guardar_usuarios(self):
        with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.usuarios, f, indent=4, ensure_ascii=False)

    def _hash_pass(self, pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()

    def autenticar(self, correo, password):
        if correo in self.usuarios and self.usuarios[correo]["password"] == self._hash_pass(password):
            self.intentos["count"] = 0
            return True, f"✅ Bienvenido, {self.usuarios[correo]['usuario']}"
        else:
            self.intentos["count"] += 1
            restantes = self.intentos["max"] - self.intentos["count"]
            if restantes <= 0:
                return False, "Intentos agotados. Ir a recuperación."
            return False, f"❌ Credenciales incorrectas ({restantes} intentos restantes)"

    def registrar(self, usuario, correo, password):
        if not usuario or not correo or not password:
            return False, "⚠️ Todos los campos son obligatorios"
        if correo in self.usuarios:
            return False, "⚠️ Ya existe una cuenta con ese correo"
        self.usuarios[correo] = {"usuario": usuario, "password": self._hash_pass(password)}
        self._guardar_usuarios()
        return True, f"✅ Usuario {usuario} registrado con éxito"

    def recuperar(self, correo):
        if not correo:
            return False, "⚠️ Introduce tu correo"
        if correo not in self.usuarios:
            return True, "📩 Si el correo existe, recibirás un enlace (simulado)"
        return True, f"📩 Correo de recuperación enviado a {correo} (simulado)"

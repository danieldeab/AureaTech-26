# app/models/user.py
# this one should change maybe
class User:
    """Entidad de usuario básica para Sprint 1."""
    def __init__(self, email, password, rol="vecino", nombre=None):
        self.email = email
        self.password = password
        self.rol = rol
        self.nombre = nombre or email.split("@")[0]

    def confirmar(self, email, password):
        """Confirma credenciales."""
        return self.email == email and self.password == password

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "rol": self.rol,
            "nombre": self.nombre,
        }
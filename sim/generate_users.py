import random
from uuid import uuid4
from app.model.user import User
from app.model.enums import RoleEnum
from app.repository.user_repository import UserRepository


class UserGenerator:
    """
    Generador de usuarios de simulación.

    """

    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository or UserRepository()

    # --- Utilidades de generación de datos sintéticos (no existen en otro lugar) ---
    @staticmethod
    def random_name() -> str:
        nombres = [
            "Carlos", "Ana", "Lucía", "Marcos", "Sara",
            "David", "Paula", "Jorge", "María", "Pedro",
        ]
        apellidos = [
            "García", "López", "Martínez", "Sánchez", "Pérez",
            "Gómez", "Díaz", "Torres", "Ruiz", "Fernández",
        ]
        return f"{random.choice(nombres)} {random.choice(apellidos)}"

    @staticmethod
    def random_email(name: str) -> str:
        base = name.lower().replace(" ", ".")
        domains = ["gmail.com", "outlook.com", "hotmail.com", "aureatech.com"]
        return f"{base}{random.randint(1, 999)}@{random.choice(domains)}"

    @staticmethod
    def random_password_hash() -> str:
        """Genera un hash simulado para datos de prueba (no usar en producción)."""
        import string
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(60))

    # --- Generación de entidad reutilizando el dominio cuando aplica ---
    def generate_random_user(self) -> User:
        name = self.random_name()
        email = self.random_email(name)
        password_hash = self.random_password_hash()
        role = random.choice(list(RoleEnum))

        # Reutiliza la factoría del modelo si está disponible
        if hasattr(User, "new") and callable(getattr(User, "new")):
            return User.new(name=name, email=email, password_hash=password_hash, role=role)
        # Fallback (no debería ocurrir normalmente)
        return User(id=uuid4(), name=name, email=email, password_hash=password_hash, role=role)

    def generate_and_save(self, count: int = 9):
        for _ in range(count):
            user = self.generate_random_user()
            # Reutiliza métodos del repositorio existentes
            self.repository.add_user(user)
        self.repository.save()
        print(f"✔ {count} usuarios generados y guardados en data/usuarios.json")


if __name__ == "__main__":
    UserGenerator().generate_and_save(9)

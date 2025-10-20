from argon2 import PasswordHasher

class User:
    def __init__(self, name, first_name, email, telephone, password, id=0):
        self.id = id
        self.name = name
        self.first_name = first_name
        self.email = email
        self.telephone = telephone
        self.password = PasswordHasher().hash(password)

    def information(self):
        print(f"""
            Nom : {self.name}
            Prenom : {self.first_name}
            Email : {self.email}
            Telephone : {self.telephone}
        """)


def UserAdmin(User):
    def __init__(self, id, nom, prenom, email, telephone, mdp, perms):
        super().__init__(id, nom, prenom, email, telephone, mdp)
        self.perms = perms
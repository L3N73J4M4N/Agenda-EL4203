class Contact:
    def __init__(self,
                 name: str,
                 last_name: str,
                 mail: str,
                 number: str):
        self.atributes = {'Nombres': name,
                          'Apellidos': last_name,
                          'Email': mail,
                          'Teléfono': number}
        self.identity = name + ' ' + last_name

    def show(self):
        for key in self.atributes:
            print(key + ':', self.atributes[key])

    def add(self, key: str, value):
        self.atributes[key] = value


class Agenda:
    def __init__(self):
        self.contacts = {}
        self.num_contacts = 0

    def add(self, contact: Contact):
        if self.contacts.get(contact.identity) is None:
            self.contacts[contact.identity] = contact
        else:
            print('El contacto ' + contact.identity + ' ya está en la agenda')
            return False
        print('Agregado ' + contact.identity)
        self.num_contacts += 1
        return True

    def remove(self, key: str):
        try:
            contact = self.contacts.pop(key)
        except KeyError:
            print('El contacto no está en la agenda')
            return False
        print('Eliminado ' + contact.identity)
        self.num_contacts -= 1
        return True

    def show(self, key: str):
        contact = self.contacts.get(key)
        if contact is None:
            print('El contacto no está en la agenda')
        else:
            contact.show()
        return contact

    def search(self, key_search: str, atribute=None):
        n = len(key_search)
        if atribute is not None:
            keys_finds = [key for key, contact in self.contacts.items() if len(contact.atributes.get(atribute)) >= n
                          and contact.atributes.get(atribute)[: n].lower() == key_search.lower()]
            return keys_finds if len(keys_finds) != 1 else keys_finds[0]
        keys_finds = []
        for key in self.contacts:
            if len(key) >= n and key[: n].lower() == key_search.lower():
                keys_finds.append(key)
                print(key)
        return keys_finds if len(keys_finds) != 1 else keys_finds[0]

    def sort(self, atribute=None):
        if atribute is None:
            self.contacts = dict(sorted(self.contacts.items()))
            return
        self.contacts = dict(sorted(self.contacts.items(), key=lambda item: item[1].atributes.get(atribute, chr(0x10FFFF))))

    def show_all(self):
        for key in self.contacts:
            print(key)

    def copy(self):
        copy = Agenda()
        copy.contacts = self.contacts.copy()
        copy.num_contacts = self.num_contacts
        return copy

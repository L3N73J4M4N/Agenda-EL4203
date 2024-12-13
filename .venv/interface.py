import pickle
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk
from textwrap import fill
from classes import Contact, Agenda

class Interface:
    def __init__(self):
        '''
        agenda y otras variables
        '''
        self.agenda = Agenda()  # Agenda
        self.atr_busqueda = None  # Atributo de busqueda, por defecto 'None' busca identidad
        self.contacts_cb = []  # CheckButtons que se muestran como contactos
        self.contacts_bv = []  # BooleanVars de los CheckButtons que se muestran
        self.contacts_id = []  # Identidad de cada contacto mostrado
        self.busqueda_value = False  # ¿Se hizo busqueda?
        self.busqueda = []  # Valores buscados
        self.orden_value = False  # ¿Se ordenó?
        self.ordenados = []  # Valores ordenados
        self.actually_key = []  # Key del contacto actual que se muestra
        self.images = {}  # Imágenes para cada key que se haya ingresado

        '''
        gestión de memoria
        '''
        try:
            with open('data.pkl', 'rb') as file:
                self.agenda = pickle.load(file)
        except FileNotFoundError:
            with open('data.pkl', 'wb') as file:
                pickle.dump(self.agenda, file)

        if self.agenda is None:
            self.agenda = Agenda()

        try:
            with open('images.pkl', 'rb') as file:
                self.images = pickle.load(file)
        except FileNotFoundError:
            with open('images.pkl', 'wb') as file:
                pickle.dump({}, file)

        if self.images is None:
            self.images = {}

        '''
        gestión de páginas
        '''
        self.pages = (self.agenda.num_contacts + 11) // 12 \
            if self.agenda.num_contacts != 0 else 1  # Número de páginas
        self.actually_page = 1  # Página actual


    def run(self, version='2024.12.09'):
        def save():
            with open('data.pkl', 'wb') as file:
                pickle.dump(self.agenda, file)
            with open('images.pkl', 'wb') as file:
                pickle.dump(self.images, file)

        '''
        inicio de ventana
        '''
        win = Tk()
        win.title('MyContactHub (v' + version + f') - Número de Contactos = {self.agenda.num_contacts}')
        win.geometry('645x490')
        win.resizable(False, False)

        '''
        cierre de ventana
        '''
        def exit():
            save()
            win.destroy()
        win.protocol('WM_DELETE_WINDOW', exit)  # root is your root window

        '''
        estilos
        '''
        style = Style()
        style.configure("Custom.TLabel", background='white')
        style.configure("Custom.TFrame", background="white")
        style.configure("Custom.TCheckbutton", background="white", focuscolor='white')
        style.configure("Custom1.TFrame", background=style.lookup("TButton", "background"))

        '''
        lado izquierdo y derecho
        '''
        left = Frame(win)
        left.grid(row=0, column=0, padx=5, pady=5)

        right = Frame(win, style="Custom.TFrame", width=300, height=465)
        right.grid(row=0, column=1, padx=5)
        right.grid_propagate(False)

        '''
        logo y nombre
        '''
        logo = Image.open('logo.png')
        logo_tk = ImageTk.PhotoImage(logo.resize((50, 50)))
        icon32_tk = ImageTk.PhotoImage(logo.resize((32, 32)))
        icon64_tk = ImageTk.PhotoImage(logo.resize((64, 64)))

        win.iconphoto(False, icon32_tk, icon64_tk)
        logo_label = Label(left, image=logo_tk)
        logo_label.image = logo_tk
        logo_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        title = Label(left, text="MyContactHub", font=("Arial", 16))
        title.grid(row=0, column=1, pady=5, sticky='w')

        '''
        busqueda
        '''
        def buscar_por_comm(key):
            if key == 'Nombre Completo':
                self.atr_busqueda = None
            elif key != 'Otro':
                self.atr_busqueda = key
            else:
                new_win = Toplevel()
                new_win.title("Busqueda")
                new_win.geometry("265x70")
                new_win.resizable(False, False)
                new_win.iconphoto(False, icon32_tk, icon64_tk)

                Label(new_win, text="Buscar por el atributo:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
                busqueda_atr_entry = Entry(new_win, width=20)
                busqueda_atr_entry.grid(row=0, column=1, pady=5, padx=5)

                def busc_atr():
                    self.atr_busqueda = busqueda_atr_entry.get()
                    new_win.destroy()

                busq_btn = Button(new_win, text="Seleccionar", command=busc_atr)
                busq_btn.grid(row=4, columnspan=2, pady=10)

        buscar_por = Menu(left, tearoff=0)
        for key in ['Nombres', 'Apellidos', 'Email', 'Teléfono', 'Nombre Completo', 'Otro']:
            buscar_por.add_command(label=key, command=lambda k=key: buscar_por_comm(k))

        def show_menu():
            buscar_por.post(buscar_boton.winfo_rootx(), buscar_boton.winfo_rooty() + buscar_boton.winfo_height())

        buscar_boton = Button(left, text="▼ Buscar por", command=show_menu)
        buscar_boton.grid(row=0, column=2, padx=5, pady=5)

        entrada = Entry(left, width=35)
        entrada.grid(row=1, columnspan=2, padx=5, pady=5)

        def search():
            contact = entrada.get()
            if contact != '':
                if self.orden_value:
                    busqueda = self.ordenados.search(contact, atribute=self.atr_busqueda)
                else:
                    busqueda = self.agenda.search(contact, atribute=self.atr_busqueda)
                if type(busqueda) == list:
                    self.busqueda = busqueda
                else:
                    self.busqueda = [busqueda]
                self.busqueda_value = True
            else:
                self.busqueda_value = False
            refresh()

        buscar = Button(left, text="Buscar", command=search)
        buscar.grid(row=1, column=2, padx=5, pady=5)

        '''
        agregar, mostrar y borrar
        '''
        def add():
            new_win = Toplevel()
            new_win.title("Agregar Contacto")
            new_win.geometry("265x165")
            new_win.resizable(False, False)
            new_win.iconphoto(False, icon32_tk, icon64_tk)

            Label(new_win, text="Nombres:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
            nombres_entry = Entry(new_win, width=30)
            nombres_entry.grid(row=0, column=1, pady=5, padx=5)

            Label(new_win, text="Apellidos:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
            apellidos_entry = Entry(new_win, width=30)
            apellidos_entry.grid(row=1, column=1, pady=5, padx=5)

            Label(new_win, text="Correo:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
            correo_entry = Entry(new_win, width=30)
            correo_entry.grid(row=2, column=1, pady=5, padx=5)

            Label(new_win, text="Teléfono:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
            telefono_entry = Entry(new_win, width=30)
            telefono_entry.grid(row=3, column=1, pady=5, padx=5)

            def agregar_contacto_nw():
                contact = Contact(name=nombres_entry.get(),
                                  last_name=apellidos_entry.get(),
                                  mail=correo_entry.get(),
                                  number=telefono_entry.get())
                self.agenda.add(contact)
                insert(contact)
                self.busqueda_value = False
                refresh()
                save()
                new_win.destroy()

            agregar_btn = Button(new_win, text="Agregar", command=agregar_contacto_nw)
            agregar_btn.grid(row=4, columnspan=2, pady=10)

        agregar = Button(left, text="Agregar", command=add)
        agregar.grid(row=2, column=0, padx=5, pady=5)

        def show():
            for i in range(12):
                if self.contacts_bv[i] != -1 and self.contacts_bv[i].get():
                    contact = self.agenda.contacts[self.contacts_id[i]]
                    insert(contact)
                    return

        mostrar = Button(left, text="Mostrar", command=show)
        mostrar.grid(row=2, column=1, padx=5, pady=5)

        def remove():
            for i in range(12):
                if self.contacts_bv[i] != -1 and self.contacts_bv[i].get():
                    self.agenda.remove(self.contacts_id[i])
                    if self.contacts_id[i] in self.busqueda:
                        self.busqueda.remove(self.contacts_id[i])
            refresh()
            save()

        borrar = Button(left, text="Borrar", command=remove)
        borrar.grid(row=2, column=2, padx=5, pady=5)

        '''
        boton de orden y frame
        '''
        contactos_frame = Frame(left, style="Custom.TFrame", width=300, height=350)
        contactos_frame.grid(row=3, columnspan=3, padx=5, pady=5)
        contactos_frame.pack_propagate(False)

        def sort(key):
            self.ordenados = self.agenda.copy()
            self.orden_value = True
            if key == 'Orden Original':
                self.orden_value = False
                refresh()
                return
            if key == 'Nombre Completo':
                self.ordenados.sort()
            elif key != 'Otro':
                self.ordenados.sort(key)
            else:
                new_win = Toplevel()
                new_win.title("Ordenación")
                new_win.geometry("265x70")
                new_win.resizable(False, False)
                new_win.iconphoto(False, icon32_tk, icon64_tk)

                Label(new_win, text="Ordenar por el atributo:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
                orden_atr_entry = Entry(new_win, width=20)
                orden_atr_entry.grid(row=0, column=1, pady=5, padx=5)

                def ord_atr():
                    self.ordenados.sort(orden_atr_entry.get())
                    refresh()
                    new_win.destroy()

                ord_btn = Button(new_win, text="Ordenar", command=ord_atr)
                ord_btn.grid(row=4, columnspan=2, pady=10)
            if self.busqueda_value:
                search()
            else:
                refresh()

        ordenar_por = Menu(contactos_frame, tearoff=0)
        for key in ['Nombres', 'Apellidos', 'Email', 'Teléfono', 'Nombre Completo', 'Orden Original', 'Otro']:
            ordenar_por.add_command(label=key, command=lambda k=key: sort(k))

        def show_menu_sort():
            ordenar_por.post(ordenar.winfo_rootx(), ordenar.winfo_rooty() + ordenar.winfo_height())

        ordenar = Button(contactos_frame, text="▼ Ordenar por", command=show_menu_sort)
        ordenar.pack(anchor='e', padx=5, pady=5)

        '''
        contactos
        '''
        paginas_frame = Frame(contactos_frame, style="Custom1.TFrame", width=300, height=100)

        def refresh():
            self.pages = (self.agenda.num_contacts + 11) // 12 if self.agenda.num_contacts != 0 else 1
            win.title('MyContactHub (v' + version + f') - Número de Contactos = {self.agenda.num_contacts}')
            contacts_bv, contacts_cb, contacts_id = [], [], []
            if self.busqueda_value:
                contacts = self.busqueda
            elif self.orden_value:
                contacts = list(self.ordenados.contacts.keys())
            else:
                contacts = list(self.agenda.contacts.keys())

            i = 12 * (self.actually_page - 1)
            for key in contacts[i: min(i + 12, len(contacts))]:
                check_var = BooleanVar()
                contact = Checkbutton(contactos_frame,
                                      text=key,
                                      style="Custom.TCheckbutton",
                                      variable=check_var)
                contacts_id.append(key)
                contacts_bv.append(check_var)
                contacts_cb.append(contact)
            if len(contacts_id) < 12:
                for _ in range(12 - len(contacts_id)):
                    label = Label(contactos_frame, text='', style='Custom.TLabel', font=('TkDefaultFont', 11))
                    contacts_id.append(-1)
                    contacts_bv.append(-1)
                    contacts_cb.append(label)

            if contacts_id == self.contacts_id:
                return False
            else:
                for widget in self.contacts_cb:
                    widget.destroy()
                paginas_frame.pack_forget()
                for widget in contacts_cb:
                    widget.pack(padx=5, anchor='nw', pady=1)
                paginas_frame.pack()
                self.contacts_cb = contacts_cb
                self.contacts_id = contacts_id
                self.contacts_bv = contacts_bv
                return True

        refresh()

        '''
        páginas
        '''
        paginas_frame.pack()
        paginas_frame.grid_propagate(False)

        def command_to_izq():
            self.actually_page -= 1
            if self.actually_page < 1:
                self.actually_page = self.pages
            pag.delete(0, 'end')
            pag.insert(0, self.actually_page)
            refresh()

        to_izq = Button(paginas_frame, text="◀", command=command_to_izq, width=5)
        to_izq.grid(row=0, column=0, padx=5, pady=5)

        def command_to_pag():
            try:
                self.actually_page = int(pag.get())
                refresh()
            except ValueError:
                return

        to_pag = Button(paginas_frame, text='Ir a página:', command=command_to_pag)
        to_pag.grid(row=0, column=1, padx=5, pady=5)
        pag = Entry(paginas_frame, width=16)
        pag.grid(row=0, column=2, padx=5, pady=5)
        pag.insert(0, '1')

        def command_to_der():
            self.actually_page += 1
            if self.actually_page > self.pages:
                self.actually_page = 1
            pag.delete(0, 'end')
            pag.insert(0, self.actually_page)
            refresh()

        to_der = Button(paginas_frame, text="▶", command=command_to_der, width=5)
        to_der.grid(row=0, column=3, padx=5, pady=5)

        '''
        botones para contacto especifico
        '''
        def add_atribute():
            new_win = Toplevel()
            new_win.title("Agregar Atributo")
            new_win.geometry("280x100")
            new_win.resizable(False, False)
            new_win.iconphoto(False, icon32_tk, icon64_tk)

            Label(new_win, text="Atributo:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
            atr_add_entry = Entry(new_win, width=30)
            atr_add_entry.grid(row=0, column=1, pady=5, padx=5)

            Label(new_win, text="Información:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
            inf_add_entry = Entry(new_win, width=30)
            inf_add_entry.grid(row=1, column=1, pady=5, padx=5)

            def agregar_atr_nw():
                self.agenda.contacts[self.actually_key].atributes[atr_add_entry.get()] = inf_add_entry.get()
                insert(self.agenda.contacts[self.actually_key])
                new_win.destroy()

            agregar_atr_btn = Button(new_win, text="Agregar", command=agregar_atr_nw)
            agregar_atr_btn.grid(row=4, columnspan=2, pady=10)

        agregar_atributo = Button(right, text='Agregar atributo', command=add_atribute)
        agregar_atributo.grid(row=0, column=0, padx=5, sticky='sw')

        def modificar():
            new_win = Toplevel()
            new_win.title("Modificar Atributo")
            new_win.geometry("280x100")
            new_win.resizable(False, False)
            new_win.iconphoto(False, icon32_tk, icon64_tk)

            Label(new_win, text="Atributo:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
            atr_mod_entry = Entry(new_win, width=30)
            atr_mod_entry.grid(row=0, column=1, pady=5, padx=5)

            Label(new_win, text="Información:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
            inf_mod_entry = Entry(new_win, width=30)
            inf_mod_entry.grid(row=1, column=1, pady=5, padx=5)

            def modificar_atr_nw():
                self.agenda.contacts[self.actually_key].atributes[atr_mod_entry.get()] = inf_mod_entry.get()
                insert(self.agenda.contacts[self.actually_key])
                new_win.destroy()


            modificar_atr_btn = Button(new_win, text="Modificar", command=modificar_atr_nw)
            modificar_atr_btn.grid(row=4, columnspan=2, pady=10)

        mod_button = Button(right, text='Modificar atributo', command=modificar)
        mod_button.grid(row=1, column=0, padx=5, sticky='w')

        def eliminar_atributo():
            new_win = Toplevel()
            new_win.title("Eliminar Atributo")
            new_win.geometry("260x70")
            new_win.resizable(False, False)
            new_win.iconphoto(False, icon32_tk, icon64_tk)

            Label(new_win, text="Atributo:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
            atr_del_entry = Entry(new_win, width=30)
            atr_del_entry.grid(row=0, column=1, pady=5, padx=5)

            def eliminar_atr_nw():
                self.agenda.contacts[self.actually_key].atributes.pop(atr_del_entry.get())
                insert(self.agenda.contacts[self.actually_key])
                new_win.destroy()

            eliminar_atr_btn = Button(new_win, text="Eliminar", command=eliminar_atr_nw)
            eliminar_atr_btn.grid(row=4, columnspan=2, pady=10)


        del_atr_button = Button(right, text='Eliminar atributo', command=eliminar_atributo)
        del_atr_button.grid(row=2, column=0, padx=5, sticky='nw')

        '''
        imagen y texto de contacto especifico
        '''
        def upload():
            img_path = filedialog.askopenfilename(title='Seleccione una imagen',
                                                  filetypes=(('Todos los archivos', '*.*'),
                                                             ('PNG','*.png'),
                                                             ('JPG','*.jpg'),
                                                             ('JPEG','*.jpeg'),
                                                             ('BMP','*.bmp'),))
            if len(img_path) > 0:
                img = Image.open(img_path).resize((120, 120))
                self.images[self.actually_key] = img
                insert(self.agenda.contacts[self.actually_key])

        img = Image.open('default.jpg')
        img_tk = ImageTk.PhotoImage(img.resize((120, 120)))
        img_label = Label(right, image=img_tk)
        img_label.image = img_tk
        img_label.grid(row=0, column=1, pady=5, rowspan=3, sticky='w')
        img_upload = Button(right, text='Subir imagen', command=upload)
        img_upload.grid(row=3, column=1, padx=24, sticky='w')

        def insert(contact):
            self.actually_key = contact.identity
            img = self.images.get(self.actually_key)
            if img is None:
                img = Image.open('default.jpg')
                img_tk = ImageTk.PhotoImage(img.resize((120, 120)))
                img_label.config(image=img_tk)
                img_label.image = img_tk
            else:
                img_tk = ImageTk.PhotoImage(img)
                img_label.config(image=img_tk)
                img_label.image = img_tk
            text = ''
            for key in contact.atributes:
                text += fill(key + ': ' + contact.atributes[key], width=40) + '\n'
                contact_text.config(state="normal")
                contact_text.delete("1.0", "end")
                contact_text.insert("1.0", text)
                contact_text.config(state="disabled")

        contact_text = Text(right, font=("TkDefaultFont", 11), wrap="word", width=40, relief='flat')
        contact_text.grid(row=5, padx=5, pady=10, columnspan=2)
        contact_text.config(state="disabled")
        if self.agenda.num_contacts != 0:
            insert(self.agenda.contacts[next(iter(self.agenda.contacts))])

        '''
        ejecutar ventana
        '''
        win.mainloop()


Interface().run('2024.12.11')
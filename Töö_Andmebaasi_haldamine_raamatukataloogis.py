import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# Andmebaasiühenduse loomine
conn = sqlite3.connect("raamatukogu.db")
c = conn.cursor()

# Tabelite loomine
c.execute("""CREATE TABLE IF NOT EXISTS Autorid (
            autor_id INTEGER PRIMARY KEY,
            autor_nimi TEXT,
            sünnikuupäev TEXT
            )""")

c.execute("""CREATE TABLE IF NOT EXISTS Žanrid (
            žanr_id INTEGER PRIMARY KEY,
            žanri_nimi TEXT
            )""")

c.execute("""CREATE TABLE IF NOT EXISTS Raamatud (
            raamat_id INTEGER PRIMARY KEY,
            pealkiri TEXT,
            väljaandmise_kuupäev TEXT,
            autor_id INTEGER,
            žanr_id INTEGER,
            FOREIGN KEY (autor_id) REFERENCES Autorid(autor_id),
            FOREIGN KEY (žanr_id) REFERENCES Žanrid(žanr_id)
            )""")

# Näidisandmete lisamine
näidisandmed = [
    ("Harry Potter ja tarkade kivi", "1997-06-26", 2, 1),
    ("Carrie", "1974-04-05", 1, 2),
    ("The Shining", "1977-01-28", 1, 2),
    ("Dracula", "1897-05-26", 3, 2),
    ("The Hobbit", "1937-09-21", 4, 1),
    ("1984", "1949-06-08", 5, 3)
]

c.executemany("INSERT INTO Raamatud (pealkiri, väljaandmise_kuupäev, autor_id, žanr_id) VALUES (?, ?, ?, ?)", näidisandmed)

conn.commit()

# Graafiline kasutajaliides Tkinteris
class RaamatukoguRakendus:
    def __init__(self, root):
        self.root = root
        self.root.title("Raamatukogu")

        self.raamatud_nupp = tk.Button(root, text="Näita raamatuid", command=self.näita_raamatud)
        self.raamatud_nupp.grid(row=0, column=0, padx=10, pady=5)

        self.lisa_raamat_nupp = tk.Button(root, text="Lisa raamat", command=self.lisa_raamat)
        self.lisa_raamat_nupp.grid(row=0, column=1, padx=10, pady=5)

        self.kustuta_raamat_nupp = tk.Button(root, text="Kustuta raamat", command=self.kustuta_raamat)
        self.kustuta_raamat_nupp.grid(row=0, column=2, padx=10, pady=5)

        self.filtri_nupp = tk.Button(root, text="Filtreeri", command=self.filtreeri)
        self.filtri_nupp.grid(row=0, column=3, padx=10, pady=5)

        # Raamatute kuvamise kast
        self.raamatute_kast = tk.Text(root, height=15, width=50)
        self.raamatute_kast.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

    def näita_raamatud(self):
        # Tühjendame eelneva sisu
        self.raamatute_kast.delete('1.0', tk.END)

        # Päring raamatute kohta andmebaasist
        c.execute("""SELECT Raamatud.pealkiri, Autorid.autor_nimi, Žanrid.žanri_nimi 
                     FROM Raamatud 
                     JOIN Autorid ON Raamatud.autor_id = Autorid.autor_id 
                     JOIN Žanrid ON Raamatud.žanr_id = Žanrid.žanr_id""")
        raamatud = c.fetchall()

        # Lisame raamatud kasti
        for raamat in raamatud:
            self.raamatute_kast.insert(tk.END, f"Pealkiri: {raamat[0]}, Autor: {raamat[1]}, Žanr: {raamat[2]}\n")

    def lisa_raamat(self):
        pealkiri = simpledialog.askstring("Lisa raamat", "Sisesta raamatu pealkiri:")
        if pealkiri:
            autor_nimi = simpledialog.askstring("Lisa raamat", "Sisesta autori nimi:")
            if autor_nimi:
                žanri_nimi = simpledialog.askstring("Lisa raamat", "Sisesta žanri nimi:")
                if žanri_nimi:
                    c.execute("INSERT INTO Raamatud (pealkiri, autor_id, žanr_id) VALUES (?, (SELECT autor_id FROM Autorid WHERE autor_nimi = ?), (SELECT žanr_id FROM Žanrid WHERE žanri_nimi = ?))", (pealkiri, autor_nimi, žanri_nimi))
                    conn.commit()
                    messagebox.showinfo("Raamat lisatud", f"Raamat '{pealkiri}' on lisatud andmebaasi.")
                    self.näita_raamatud()

    def kustuta_raamat(self):
        pealkiri = simpledialog.askstring("Kustuta raamat", "Sisesta raamatu pealkiri, mida soovid kustutada:")
        if pealkiri:
            c.execute("DELETE FROM Raamatud WHERE pealkiri=?", (pealkiri,))
            conn.commit()
            messagebox.showinfo("Raamat kustutatud", f"Raamat '{pealkiri}' on kustutatud andmebaasist.")
            self.näita_raamatud()

    def filtreeri(self):
        filter_by = simpledialog.askstring("Filtreeri", "Sisesta autorinimi või žanri nimi:")
        if filter_by:
            c.execute("""SELECT Raamatud.pealkiri, Autorid.autor_nimi, Žanrid.žanri_nimi 
                         FROM Raamatud 
                         JOIN Autorid ON Raamatud.autor_id = Autorid.autor_id 
                         JOIN Žanrid ON Raamatud.žanr_id = Žanrid.žanr_id 
                         WHERE Autorid.autor_nimi = ? OR Žanrid.žanri_nimi = ?""", (filter_by, filter_by))
            raamatud = c.fetchall()

            if raamatud:
                self.raamatute_kast.delete('1.0', tk.END)
                for raamat in raamatud:
                    self.raamatute_kast.insert(tk.END, f"Pealkiri: {raamat[0]}, Autor: {raamat[1]}, Žanr: {raamat[2]}\n")
            else:
                messagebox.showinfo("Tulemused puuduvad", "Ühtegi raamatut selle filtri kohta ei leitud.")

# Rakenduse käivitamine
root = tk.Tk()
app = RaamatukoguRakendus(root)
root.mainloop()

# Andmebaasiühenduse sulgemine
conn.close()

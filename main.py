
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class BookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Библиотека книг")
        self.books = []
        self.file_path = "books.json"

        # --- Блок ввода данных ---
        frame_input = tk.LabelFrame(root, text=" Добавить новую книгу ", padx=10, pady=10)
        frame_input.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        tk.Label(frame_input, text="Название:").grid(row=0, column=0, sticky="e")
        self.ent_title = tk.Entry(frame_input, width=30)
        self.ent_title.grid(row=0, column=1, pady=2)

        tk.Label(frame_input, text="Автор:").grid(row=1, column=0, sticky="e")
        self.ent_author = tk.Entry(frame_input, width=30)
        self.ent_author.grid(row=1, column=1, pady=2)

        tk.Label(frame_input, text="Жанр:").grid(row=2, column=0, sticky="e")
        self.ent_genre = tk.Entry(frame_input, width=30)
        self.ent_genre.grid(row=2, column=1, pady=2)

        tk.Label(frame_input, text="Страниц:").grid(row=3, column=0, sticky="e")
        self.ent_pages = tk.Entry(frame_input, width=30)
        self.ent_pages.grid(row=3, column=1, pady=2)

        tk.Button(frame_input, text="Добавить в список", command=self.add_book, bg="#d4edda").grid(row=4, column=0, columnspan=2, pady=10, sticky="we")

        # --- Блок фильтров ---
        frame_filter = tk.LabelFrame(root, text=" Фильтры и поиск ", padx=10, pady=10)
        frame_filter.grid(row=0, column=1, padx=10, pady=5, sticky="ns")

        tk.Label(frame_filter, text="Жанр:").grid(row=0, column=0, sticky="e")
        self.filter_genre = tk.Entry(frame_filter)
        self.filter_genre.grid(row=0, column=1, pady=2)

        tk.Label(frame_filter, text="Мин. страниц:").grid(row=1, column=0, sticky="e")
        self.filter_pages = tk.Entry(frame_filter)
        self.filter_pages.insert(0, "0")
        self.filter_pages.grid(row=1, column=1, pady=2)

        tk.Button(frame_filter, text="Применить", command=self.apply_filter).grid(row=2, column=0, columnspan=2, pady=5, sticky="we")
        tk.Button(frame_filter, text="Сбросить", command=self.reset_filters).grid(row=3, column=0, columnspan=2, sticky="we")

        # --- Таблица ---
        self.tree = ttk.Treeview(root, columns=("Title", "Author", "Genre", "Pages"), show='headings', height=10)
        self.tree.heading("Title", text="Название")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("Pages", text="Страниц")
        
        self.tree.column("Title", width=200)
        self.tree.column("Author", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Pages", width=80)
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # --- Кнопки управления (Удаление и Сохранение) ---
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="we")

        tk.Button(btn_frame, text="Удалить выбранную", command=self.delete_book, fg="white", bg="#dc3545").pack(side="left", padx=10, expand=True, fill="x")
        tk.Button(btn_frame, text="Очистить всё", command=self.clear_all, bg="#ffc107").pack(side="left", padx=10, expand=True, fill="x")
        tk.Button(btn_frame, text="Сохранить всё в JSON", command=self.save_data, bg="#007bff", fg="white").pack(side="left", padx=10, expand=True, fill="x")

        # Загрузка данных при запуске
        self.load_data(silent=True)

    def add_book(self):
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        genre = self.ent_genre.get().strip()
        pages = self.ent_pages.get().strip()

        if not (title and author and genre and pages):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if not pages.isdigit():
            messagebox.showerror("Ошибка", "Страницы должны быть числом!")
            return

        book = {"title": title, "author": author, "genre": genre, "pages": int(pages)}
        self.books.append(book)
        self.update_table()
        
        # Очистка полей
        for entry in [self.ent_title, self.ent_author, self.ent_genre, self.ent_pages]:
            entry.delete(0, tk.END)

    def update_table(self, data_list=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        display_list = data_list if data_list is not None else self.books
        for b in display_list:
            self.tree.insert("", tk.END, values=(b["title"], b["author"], b["genre"], b["pages"]))

    def delete_book(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления в таблице!")
            return
        
        if messagebox.askyesno("Удаление", "Удалить выбранную книгу?"):
            for item in selected_item:
                values = self.tree.item(item)['values']
                # Фильтруем список: оставляем те книги, у которых название И автор не совпадают с выбранными
                self.books = [b for b in self.books if not (str(b['title']) == str(values) and str(b['author']) == str(values[1]))]
                self.tree.delete(item)
            self.save_data(silent=True) # Автосохранение после удаления

    def clear_all(self):
        if messagebox.askyesno("Очистка", "Вы уверены, что хотите удалить ВСЕ книги?"):
            self.books = []
            self.update_table()
            self.save_data(silent=True)

    def apply_filter(self):
        genre_query = self.filter_genre.get().lower().strip()
        try:
            min_pages = int(self.filter_pages.get()) if self.filter_pages.get() else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Минимум страниц — это число!")
            return

        filtered = [
            b for b in self.books 
            if (not genre_query or genre_query in b["genre"].lower()) 
            and (b["pages"] >= min_pages)
        ]
        self.update_table(filtered)

    def reset_filters(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_pages.delete(0, tk.END)
        self.filter_pages.insert(0, "0")
        self.update_table()

    def save_data(self, silent=False):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            if not silent:
                messagebox.showinfo("Успех", "Данные сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self, silent=False):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                self.update_table()
            except Exception as e:
                if not silent:
                    messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookApp(root)
    root.mainloop()

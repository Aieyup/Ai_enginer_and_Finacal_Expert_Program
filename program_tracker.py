import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import os
from PIL import Image, ImageTk
import re

class EgitimTakipUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Eğitim Programı Takip Uygulaması")
        
        # Ekran boyutunu optimize et
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = min(1200, int(screen_width * 0.8))
        window_height = min(800, int(screen_height * 0.8))
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ana stil ayarları
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Section.TLabel", font=("Arial", 10, "bold"))
        style.configure("Task.TCheckbutton", font=("Arial", 9))
        
        # Ana container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sol ve sağ frame'leri oluştur
        self.left_frame = ttk.Frame(self.main_container)
        self.right_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Üst frame (başlık ve ilerleme çubuğu için)
        self.top_frame = ttk.Frame(self.left_frame)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Başlık
        self.title_label = ttk.Label(
            self.top_frame,
            text="Eğitim Programı Takibi",
            style="Title.TLabel"
        )
        self.title_label.pack(side=tk.TOP, pady=(0, 10))
        
        # İlerleme çubuğu frame
        self.progress_frame = ttk.Frame(self.top_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Genel İlerleme:")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=300,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.progress_text = ttk.Label(self.progress_frame, text="0%")
        self.progress_text.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik için frame ve scrollbar
        self.content_frame = ttk.Frame(self.left_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.content_frame)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid yapılandırması
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sağ taraf için değişkenleri başlat
        self.date_filter_var = tk.StringVar(value="Tüm Tarihler")
        self.search_var = tk.StringVar()
        
        # Not geçmişi alanını oluştur
        self.notes_history = scrolledtext.ScrolledText(
            self.right_frame,
            wrap=tk.WORD,
            width=30,
            height=10,
            font=("Arial", 9)
        )
        
        self.search_var.trace('w', lambda name, index, mode: self.filter_notes())
        
        # Resmi yükle ve göster
        try:
            # Resmi yükle
            image = Image.open("board-jolly-clown (1).jpg")
            # Resmi yeniden boyutlandır
            target_width = int(window_width * 0.4)
            ratio = target_width / image.width
            target_height = int(image.height * ratio)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            # PhotoImage oluştur
            self.photo = ImageTk.PhotoImage(image)
            # Label oluştur ve resmi göster
            self.image_label = ttk.Label(self.right_frame, image=self.photo)
            self.image_label.pack(pady=(20, 10), padx=20)
            
            # Not alma alanı frame'i
            self.notes_frame = ttk.LabelFrame(self.right_frame, text="Notlar", padding=(5, 5))
            self.notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            
            # Not girişi frame
            self.note_input_frame = ttk.Frame(self.notes_frame)
            self.note_input_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
            
            # Not girişi alanı
            self.note_input = scrolledtext.ScrolledText(
                self.note_input_frame,
                wrap=tk.WORD,
                width=30,
                height=5,
                font=("Arial", 9)
            )
            self.note_input.pack(fill=tk.X, expand=True, pady=(0, 5))
            
            # Butonlar için frame
            self.buttons_frame = ttk.Frame(self.note_input_frame)
            self.buttons_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Not ekle butonu
            self.add_button = ttk.Button(
                self.buttons_frame,
                text="Not Ekle",
                command=self.add_note
            )
            self.add_button.pack(side=tk.LEFT, padx=5)
            
            # Notları temizle butonu
            self.clear_button = ttk.Button(
                self.buttons_frame,
                text="Temizle",
                command=lambda: self.note_input.delete(1.0, tk.END)
            )
            self.clear_button.pack(side=tk.LEFT, padx=5)
            
            # Not geçmişi araçları frame'i
            self.history_tools_frame = ttk.Frame(self.notes_frame)
            self.history_tools_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            
            # Not arama alanı
            self.search_entry = ttk.Entry(
                self.history_tools_frame,
                textvariable=self.search_var,
                font=("Arial", 9)
            )
            self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            ttk.Label(self.search_entry, text="🔍", font=("Arial", 9)).place(x=2, y=2)
            self.search_entry.insert(0, " Notlarda ara...")
            self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
            self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
            
            # Tarih filtresi
            self.date_filter = ttk.Combobox(
                self.history_tools_frame,
                textvariable=self.date_filter_var,
                values=["Tüm Tarihler", "Bugün", "Son 7 Gün", "Son 30 Gün"],
                state="readonly",
                width=15
            )
            self.date_filter.pack(side=tk.RIGHT, padx=5)
            self.date_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_notes())
            
            # Geçmiş notlar alanı
            self.notes_history_label = ttk.Label(
                self.notes_frame,
                text="Not Geçmişi:",
                font=("Arial", 9, "bold")
            )
            self.notes_history_label.pack(fill=tk.X, padx=5, pady=(5, 0))
            
            self.notes_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.notes_history.config(state='disabled')
            
            # Notları yükle
            self.load_notes()
            
        except Exception as e:
            print(f"Resim yüklenirken hata oluştu: {e}")
        
        # Veriyi yükle ve arayüzü oluştur
        self.load_data()
        self.create_interface()
        
        # Mouse wheel binding
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Canvas'ın genişliğini ayarla
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig('window', width=event.width)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_data(self):
        try:
            with open("program.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Hata", "program.json dosyası bulunamadı!")
            self.root.quit()
    
    def save_data(self):
        with open("program.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
    
    def create_interface(self):
        for i, section in enumerate(self.data["program"]):
            # Bölüm frame
            section_frame = ttk.Frame(self.scrollable_frame)
            section_frame.pack(fill=tk.X, pady=(10, 5), padx=5)
            
            # Bölüm başlığı
            section_label = ttk.Label(
                section_frame,
                text=section["title"],
                style="Section.TLabel"
            )
            section_label.pack(fill=tk.X, pady=(5, 2))
            
            # Görevler için frame
            tasks_frame = ttk.Frame(section_frame)
            tasks_frame.pack(fill=tk.X, padx=20)
            
            # Görevler
            for j, task in enumerate(section["tasks"]):
                # Ana görev frame
                task_frame = ttk.Frame(tasks_frame)
                task_frame.pack(fill=tk.X, pady=1)
                
                # Ana görev checkbox'ı
                var = tk.BooleanVar(value=task.get("completed", False))
                checkbox = ttk.Checkbutton(
                    task_frame,
                    text=task["name"],
                    variable=var,
                    style="Task.TCheckbutton",
                    command=lambda s=i, t=j, v=var: self.update_task(s, t, v)
                )
                checkbox.pack(fill=tk.X, pady=1)
                
                # Alt görevler varsa
                if "subtasks" in task:
                    subtasks_frame = ttk.Frame(task_frame)
                    subtasks_frame.pack(fill=tk.X, padx=20)
                    
                    # Alt görevleri ekle
                    for k, subtask in enumerate(task["subtasks"]):
                        subtask_var = tk.BooleanVar(value=subtask.get("completed", False))
                        subtask_checkbox = ttk.Checkbutton(
                            subtasks_frame,
                            text=subtask["name"],
                            variable=subtask_var,
                            style="Task.TCheckbutton",
                            command=lambda s=i, t=j, st=k, v=subtask_var: self.update_subtask(s, t, st, v)
                        )
                        subtask_checkbox.pack(fill=tk.X, pady=1)
            
            # Ayırıcı çizgi
            if i < len(self.data["program"]) - 1:
                ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
    
    def update_task(self, section_index, task_index, var):
        """Ana görevi güncelle"""
        task = self.data["program"][section_index]["tasks"][task_index]
        task["completed"] = var.get()
        
        # Alt görevler varsa, ana görev işaretlendiğinde hepsini işaretle
        if "subtasks" in task:
            for subtask in task["subtasks"]:
                subtask["completed"] = var.get()
        
        self.save_data()
        self.update_progress()
    
    def update_subtask(self, section_index, task_index, subtask_index, var):
        """Alt görevi güncelle"""
        subtask = self.data["program"][section_index]["tasks"][task_index]["subtasks"][subtask_index]
        subtask["completed"] = var.get()
        
        # Alt görevlerin durumuna göre ana görevin durumunu güncelle
        task = self.data["program"][section_index]["tasks"][task_index]
        all_completed = all(st.get("completed", False) for st in task["subtasks"])
        task["completed"] = all_completed
        
        self.save_data()
        self.update_progress()
    
    def update_progress(self):
        """İlerleme durumunu güncelle"""
        total_tasks = 0
        completed_tasks = 0
        
        for section in self.data["program"]:
            for task in section["tasks"]:
                if "subtasks" in task:
                    # Alt görevler varsa onları say
                    total_tasks += len(task["subtasks"])
                    completed_tasks += sum(1 for st in task["subtasks"] if st.get("completed", False))
                else:
                    # Alt görev yoksa ana görevi say
                    total_tasks += 1
                    completed_tasks += 1 if task.get("completed", False) else 0
        
        progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        self.progress_var.set(progress)
        self.progress_text.config(text=f"{progress}%")
    
    def load_notes(self):
        """İlk yüklemede tüm notları göster"""
        self.filter_notes()
    
    def _on_search_focus_in(self, event):
        if self.search_entry.get().strip() == "Notlarda ara...":
            self.search_entry.delete(0, tk.END)
            
    def _on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, " Notlarda ara...")
    
    def filter_notes(self):
        """Notları arama metni ve tarih filtresine göre filtrele"""
        search_text = self.search_var.get().strip()
        if search_text == "Notlarda ara...":
            search_text = ""
            
        date_filter = self.date_filter_var.get()
        
        try:
            with open("notes_history.txt", "r", encoding="utf-8") as f:
                all_notes = f.read()
            
            # Notları parçala
            notes = re.split(r'\n={30,}\n', all_notes)
            filtered_notes = []
            
            for note in notes:
                if not note.strip():
                    continue
                    
                # Tarih kontrolü
                match = re.match(r'\[(\d{2}\.\d{2}\.\d{4})', note)
                if match:
                    note_date = datetime.strptime(match.group(1), "%d.%m.%Y")
                    today = datetime.now()
                    
                    # Tarih filtresini uygula
                    if date_filter == "Bugün" and note_date.date() != today.date():
                        continue
                    elif date_filter == "Son 7 Gün" and (today - note_date).days > 7:
                        continue
                    elif date_filter == "Son 30 Gün" and (today - note_date).days > 30:
                        continue
                
                # Arama metnini kontrol et
                if search_text and search_text.lower() not in note.lower():
                    continue
                    
                filtered_notes.append(note)
            
            # Filtrelenmiş notları göster
            self.notes_history.config(state='normal')
            self.notes_history.delete(1.0, tk.END)
            
            if filtered_notes:
                for i, note in enumerate(filtered_notes):
                    if i > 0:
                        self.notes_history.insert(tk.END, "\n" + "="*30 + "\n")
                    self.notes_history.insert(tk.END, note.strip())
            else:
                self.notes_history.insert(tk.END, "Filtrelenen kriterlere uygun not bulunamadı.")
            
            self.notes_history.config(state='disabled')
            self.notes_history.see(tk.END)
            
        except FileNotFoundError:
            self.notes_history.config(state='normal')
            self.notes_history.delete(1.0, tk.END)
            self.notes_history.insert(tk.END, "Henüz not eklenmemiş.")
            self.notes_history.config(state='disabled')
    
    def add_note(self):
        """Yeni not ekle"""
        note_text = self.note_input.get(1.0, tk.END).strip()
        if note_text:
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
            formatted_note = f"\n[{current_time}]\n{note_text}\n{'='*30}\n"
            
            try:
                with open("notes_history.txt", "a", encoding="utf-8") as f:
                    f.write(formatted_note)
                
                self.note_input.delete(1.0, tk.END)
                self.filter_notes()  # Filtrelenmiş notları güncelle
                messagebox.showinfo("Başarılı", "Not eklendi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Not eklenirken bir hata oluştu: {e}")
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir not girin!")

def main():
    root = tk.Tk()
    app = EgitimTakipUygulamasi(root)
    root.mainloop()

if __name__ == "__main__":
    main()
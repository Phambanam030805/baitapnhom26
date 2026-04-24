import tkinter as tk
from tkinter import messagebox
from database import Database
from gui_auth import LoginWindow
from gui_admin import AdminDashboard
from gui_teacher import TeacherDashboard
from gui_student import StudentDashboard

class AppController:
    def __init__(self):
        self.root = tk.Tk()
        self.db = Database()
        self.show_login()

    def show_login(self):
        for w in self.root.winfo_children(): w.destroy()
        self.login_app = LoginWindow(self.root, self.on_login_success, self.db)

    def on_login_success(self, user_data):
        try:
            for w in self.root.winfo_children(): w.destroy()
            role = user_data[2]
            if role == "admin": AdminDashboard(self.root, user_data, self.db, self.show_login)
            elif role == "teacher": TeacherDashboard(self.root, user_data, self.db, self.show_login)
            elif role == "student": StudentDashboard(self.root, user_data, self.db, self.show_login)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Lỗi khởi động", f"Đã xảy ra lỗi khi tạo giao diện:\n{str(e)}\n\nChi tiết:\n{error_details}")
            self.show_login()

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    AppController().run()

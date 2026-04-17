import tkinter as tk
from gui import LoginWindow, AdminDashboard, TeacherDashboard, StudentDashboard

class AppController:
    def __init__(self):
        self.root = tk.Tk()
        self.show_login()

    def show_login(self):
        for w in self.root.winfo_children(): w.destroy()
        self.login_app = LoginWindow(self.root, self.on_login_success)

    def on_login_success(self, user_data):
        for w in self.root.winfo_children(): w.destroy()
        role = user_data[2]
        if role == "admin": AdminDashboard(self.root, user_data)
        elif role == "teacher": TeacherDashboard(self.root, user_data)
        elif role == "student": StudentDashboard(self.root, user_data)
        tk.Button(self.root, text="Đăng xuất", command=self.show_login, fg="red").pack(side="bottom")

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    AppController().run()

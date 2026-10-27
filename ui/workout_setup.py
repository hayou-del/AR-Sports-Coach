"""Optional pre-workout setup dialog (Tkinter bundled with standard Windows Python)."""
from ui.workout import WorkoutGoals

def choose_goals():
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.title('AR SPORTS COACH  |  CUSTOM WORKOUT')
    root.configure(bg='#111827')
    root.geometry('470x410')
    root.resizable(False, False)
    selected = [None]
    tk.Label(root, text='BUILD YOUR WORKOUT', fg='#f4d35e', bg='#111827', font=('Segoe UI', 19, 'bold')).pack(pady=(26, 10))
    tk.Label(root, text='Squat tracking  •  Choose your session goals', fg='#cbd5e1', bg='#111827', font=('Segoe UI', 10)).pack(pady=(0, 18))
    values = []
    for label, default in [('Repetition goal', '12'), ('Time limit (minutes)', '5'), ('Estimated calorie goal (optional)', '0')]:
        tk.Label(root, text=label, fg='#e2e8f0', bg='#111827', font=('Segoe UI', 10)).pack()
        entry = tk.Entry(root, justify='center', font=('Segoe UI', 12), width=18)
        entry.insert(0, default)
        entry.pack(pady=(3, 12))
        values.append(entry)
    def start():
        try:
            selected[0] = WorkoutGoals(int(values[0].get()), int(values[1].get()), float(values[2].get()))
        except ValueError as exc:
            messagebox.showerror('Invalid workout goals', str(exc) or 'Please enter valid numbers')
            return
        root.destroy()
    tk.Button(root, text='START TRAINING', command=start, bg='#f4d35e', fg='#111827', font=('Segoe UI', 12, 'bold'), padx=24, pady=8).pack(pady=4)
    tk.Label(root, text='Calorie figures are illustrative estimates, not measurements.', fg='#94a3b8', bg='#111827', font=('Segoe UI', 9)).pack(pady=9)
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    root.mainloop()
    return selected[0]

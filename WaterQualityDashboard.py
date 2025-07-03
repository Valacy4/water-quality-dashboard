import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
import sqlite3
from reportlab.pdfgen import canvas
from datetime import datetime

# WHO/EPA Thresholds
SAFE_LIMITS = {
    "pH": (6.5, 8.5),
    "TDS": (0, 500),
    "Turbidity": (0, 5),
    "Hardness": (0, 150),
    "Chlorine": (0, 4),         # mg/L
    "Conductivity": (0, 500),   # µS/cm
    "Nitrates": (0, 10),        # mg/L
    "Fluoride": (0, 1.5),       # mg/L
    "Iron": (0, 0.3) 
}

# DB Setup
conn = sqlite3.connect('waterQualityTest.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS water_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        pH REAL,
        tds REAL,
        turbidity REAL,
        hardness REAL,
        chlorine REAL,
        conductivity REAL,
        nitrates REAL,
        fluoride REAL,
        iron REAL,
        extra REAL,
        status TEXT
    )
''')
conn.commit()

# Classification Logic
def classify_water(ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron):
    if not (SAFE_LIMITS["pH"][0] <= ph <= SAFE_LIMITS["pH"][1]):
        return "Needs Filtration"
    if tds > SAFE_LIMITS["TDS"][1] or turbidity > SAFE_LIMITS["Turbidity"][1] or hardness > SAFE_LIMITS["Hardness"][1] or chlorine > SAFE_LIMITS["Chlorine"][1]or conductivity > SAFE_LIMITS["Conductivity"][1]or nitrates > SAFE_LIMITS["Nitrates"][1]or fluoride > SAFE_LIMITS["Fluoride"][1]or iron > SAFE_LIMITS["Iron"][1] :
        return "Unsafe – Contaminated"
    return "Safe for Drinking"

# PDF Report Generator
def generate_pdf_report(ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron, status):
    filename = f"Water_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=filename)
    if file_path:
        pdf = canvas.Canvas(file_path)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 800, "💧 Water Quality Report")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 770, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.drawString(100, 740, f"pH: {ph}")
        pdf.drawString(100, 720, f"TDS: {tds} ppm")
        pdf.drawString(100, 700, f"Turbidity: {turbidity} NTU")
        pdf.drawString(100, 680, f"Hardness: {hardness} mg/L")
        pdf.drawString(100, 660, f"Chlorine: {chlorine} mg/L")
        pdf.drawString(100, 640, f"Conductivity: {conductivity} µS/cm")
        pdf.drawString(100, 620, f"Nitrates: {nitrates} mg/L")
        pdf.drawString(100, 600, f"Fluoride: {fluoride} mg/L")
        pdf.drawString(100, 580, f"Iron: {iron} mg/L")
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(100, 540, f"Water Status: {status}")
        pdf.save()
        messagebox.showinfo("Success", "PDF report saved successfully!")

# Chart
def plot_graph(ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron):
    plt.figure(figsize=(6, 4))
    labels = ['pH', 'TDS', 'Turbidity', 'Hardness','Chlorine','Conductivity','Nitrates','Fluoride','Iron']
    values = [ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron]
    plt.bar(labels, values, color=['lightblue', 'orange', 'lightgreen', 'tomato','green','blue','red','purple','pink'])
    plt.title("Water Test Parameters")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.show()

# Submit Logic
def submit():
    try:
        ph = float(ph_entry.get())
        tds = float(tds_entry.get())
        turbidity = float(turb_entry.get())
        hardness = float(hard_entry.get())
        chlorine=float(chlorine_entry.get())
        conductivity=float(conductivity_entry.get())
        nitrates=float(nitrates_entry.get())
        fluoride=float(fluoride_entry.get())
        iron=float(iron_entry.get())
        
        status = classify_water(ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron)

        # Display Result
        result_label.config(text=f"Water Status: {status}")
        if status == "Safe for Drinking":
            result_label.config(fg="green")
        elif status == "Needs Filtration":
            result_label.config(fg="orange")
        else:
            result_label.config(fg="red")

        # Save in DB
        cursor.execute('''
            INSERT INTO water_reports (date, pH, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron, status)
            VALUES (?, ?, ?, ?, ?, ?,?,?,?,?,?)''',
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron, status))
        conn.commit()

        plot_graph(ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron)
        generate_pdf_report(ph, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron, status)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers only.")

# View Past Reports
def view_reports():
    report_win = tk.Toplevel(root)
    report_win.title("Previous Water Reports")
    report_win.geometry("600x300")

    tree = ttk.Treeview(report_win, columns=('Date', 'pH', 'TDS', 'Turbidity', 'Hardness','Chlorine','Conductivity','Nitrates','Fluoride','Iron', 'Status'), show='headings')
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=90)

    cursor.execute("SELECT date, pH, tds, turbidity, hardness,chlorine,conductivity,nitrates,fluoride,iron, status FROM water_reports ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)

    tree.pack(fill='both', expand=True)

# GUI Setup
root = tk.Tk()
root.title("💧 Water Quality Monitoring Dashboard")
root.geometry("420x500")
root.configure(bg="#f0f8ff")

title = tk.Label(root, text="Water Quality Analyzer", font=("Helvetica", 18, "bold"), bg="#f0f8ff", fg="#0077b6")
title.pack(pady=15)

fields = [("pH:", "ph_entry"), ("TDS (ppm):", "tds_entry"),
          ("Turbidity (NTU):", "turb_entry"), ("Hardness (mg/L):", "hard_entry"),
         ("Chlorine(mg/L):","chlorine_entry"),("Conductivity(µS/cm):","conductivity_entry"),
         ("Nitrates(mg/L):","nitrates_entry"),("Fluoride(mg/L):","fluoride_entry"),
         ("Iron(mg/L):","iron_entry")]

entries = {}

for label, key in fields:
    tk.Label(root, text=label, font=("Arial", 12), bg="#f0f8ff").pack(pady=5)
    entry = tk.Entry(root, font=("Arial", 12), width=30)
    entry.pack()
    entries[key] = entry

ph_entry = entries["ph_entry"]
tds_entry = entries["tds_entry"]
turb_entry = entries["turb_entry"]
hard_entry = entries["hard_entry"]
chlorine_entry=entries["chlorine_entry"]
conductivity_entry=entries["conductivity_entry"]
nitrates_entry=entries["nitrates_entry"]
fluoride_entry=entries["fluoride_entry"]
iron_entry=entries["iron_entry"]


tk.Button(root, text="Analyze Water", command=submit, bg="#0077b6", fg="white", font=("Arial", 12, "bold"),
          padx=10, pady=5).pack(pady=15)

result_label = tk.Label(root, text="Water Status: ", font=("Arial", 13), bg="#f0f8ff")
result_label.pack(pady=10)

tk.Button(root, text="View Previous Reports", command=view_reports, bg="#90e0ef", font=("Arial", 11)).pack(pady=5)

root.mainloop()

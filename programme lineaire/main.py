import tkinter as tk
from tkinter import ttk
from pulp import *
import numpy as np
import matplotlib.pyplot as plt


# ==============================
# APP PRINCIPALE
# ==============================
root = tk.Tk()
root.title("Solver Programmation Linéaire")
root.geometry("900x650")
root.configure(bg="#1e1e2f")


# ==============================
# TITRE
# ==============================
title = tk.Label(
    root,
    text="OPTIMISATION - PROGRAMMATION LINEAIRE",
    font=("Arial", 16, "bold"),
    bg="#1e1e2f",
    fg="white"
)
title.pack(pady=10)


# ==============================
# VARIABLES
# ==============================
frame_top = tk.Frame(root, bg="#1e1e2f")
frame_top.pack()

tk.Label(frame_top, text="Variables:", bg="#1e1e2f", fg="white").grid(row=0, column=0)
entry_vars = tk.Entry(frame_top, width=5)
entry_vars.grid(row=0, column=1)

tk.Label(frame_top, text="Contraintes:", bg="#1e1e2f", fg="white").grid(row=0, column=2)
entry_constraints = tk.Entry(frame_top, width=5)
entry_constraints.grid(row=0, column=3)


# ==============================
# TABLE DE COEFFICIENTS
# ==============================
table_frame = tk.Frame(root, bg="#1e1e2f")
table_frame.pack(pady=10)

entries = []


# ==============================
# GENERER TABLE
# ==============================
def generer():
    global entries

    for w in table_frame.winfo_children():
        w.destroy()

    n = int(entry_vars.get())
    m = int(entry_constraints.get())

    # headers
    for j in range(n):
        tk.Label(table_frame, text=f"x{j+1}", bg="#1e1e2f", fg="yellow").grid(row=0, column=j)

    tk.Label(table_frame, text="Signe", bg="#1e1e2f", fg="yellow").grid(row=0, column=n)
    tk.Label(table_frame, text="B", bg="#1e1e2f", fg="yellow").grid(row=0, column=n+1)

    entries = []

    for i in range(m):
        row = []

        for j in range(n):
            e = tk.Entry(table_frame, width=7)
            e.grid(row=i+1, column=j)
            row.append(e)

        signe = ttk.Combobox(table_frame, values=["<=", ">=", "="], width=5)
        signe.grid(row=i+1, column=n)
        row.append(signe)

        b = tk.Entry(table_frame, width=7)
        b.grid(row=i+1, column=n+1)
        row.append(b)

        entries.append(row)


# ==============================
# RESOLUTION
# ==============================
def resoudre():
    n = int(entry_vars.get())
    m = int(entry_constraints.get())

    C = list(map(float, entry_obj.get().split()))
    variables = [LpVariable(f"x{i+1}", lowBound=0) for i in range(n)]

    model = LpProblem("PL", LpMaximize)
    model += lpSum(C[i]*variables[i] for i in range(n))

    A = []
    B = []
    signes = []

    for i in range(m):
        coeffs = []
        for j in range(n):
            coeffs.append(float(entries[i][j].get()))

        signes.append(entries[i][n].get())
        B.append(float(entries[i][n+1].get()))
        A.append(coeffs)

        expr = lpSum(coeffs[j]*variables[j] for j in range(n))

        if signes[i] == "<=":
            model += expr <= B[i]
        elif signes[i] == ">=":
            model += expr >= B[i]
        else:
            model += expr == B[i]

    model.solve()

    # ================= RESULT TABLE =================
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, f"STATUS: {LpStatus[model.status]}\n\n")

    for v in variables:
        result_box.insert(tk.END, f"{v.name} = {value(v)}\n")

    result_box.insert(tk.END, f"\nZ = {value(model.objective)}\n")

    # ================= GRAPH (2 VARIABLES ONLY) =================
    if n == 2:
        x = np.linspace(0, 5000, 400)

        plt.figure()

        feasible_x = []
        feasible_y = []

        for i in range(len(x)):
            for j in range(len(x)):
                x1 = x[i]
                x2 = x[j]

                ok = True
                for k in range(m):
                    a1, a2 = A[k]
                    if signes[k] == "<=" and a1*x1 + a2*x2 > B[k]:
                        ok = False
                    if signes[k] == ">=" and a1*x1 + a2*x2 < B[k]:
                        ok = False

                if ok:
                    feasible_x.append(x1)
                    feasible_y.append(x2)

        plt.scatter(feasible_x, feasible_y, s=1, color="lightgreen")

        # contraintes
        for k in range(m):
            if A[k][1] != 0:
                y = (B[k] - A[k][0]*x) / A[k][1]
                plt.plot(x, y)

        # optimal
        opt_x = value(variables[0])
        opt_y = value(variables[1])
        plt.scatter(opt_x, opt_y, color="red", s=100)

        plt.title("Région réalisable + solution optimale")
        plt.show()

    # ================= SIMPLEX / DUALITY =================
    result_box.insert(tk.END, "\n--- SIMPLEX ---\n")
    result_box.insert(tk.END, "Solution obtenue automatiquement par algorithme du simplexe.\n")

    result_box.insert(tk.END, "\n--- DUALITE ---\n")
    result_box.insert(tk.END, "Max problème primal ↔ Min problème dual\n")


# ==============================
# FONCTION OBJECTIF
# ==============================
tk.Label(root, text="Fonction objectif (ex: 50 30)", bg="#1e1e2f", fg="white").pack()
entry_obj = tk.Entry(root, width=30)
entry_obj.pack()


# ==============================
# BUTTONS
# ==============================
tk.Button(root, text="Générer tableau", command=generer, bg="blue", fg="white").pack(pady=5)
tk.Button(root, text="Résoudre", command=resoudre, bg="green", fg="white").pack(pady=5)


# ==============================
# RESULT AREA
# ==============================
result_box = tk.Text(root, height=12, bg="black", fg="lime")
result_box.pack(fill="both", expand=True)


root.mainloop()
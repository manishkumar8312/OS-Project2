import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
from PIL import Image, ImageTk
import os 
import winsound

class DeadlockManager:
    def __init__(self, num_processes, num_resources, instance_mode="Multi-Instance"):
        self.p = num_processes
        self.r = num_resources
        self.total_alloc = None
        self.instance_mode = instance_mode  # "Single-Instance" or "Multi-Instance"

    def detect_deadlock(self, alloc, req, avail):
        if self.instance_mode == "Multi-Instance":
           ######## Multi-Instance: Banker's Algorithm-like safe sequence check     ##########
            if self.total_alloc is None:
                self.total_alloc = [sum(alloc[i][j] for i in range(self.p)) for j in range(self.r)]
            
            work = avail[:]
            finish = [False] * self.p
            safe_seq = []

            if any(avail[j] + self.total_alloc[j] < max(req[i][j] for i in range(self.p)) for j in range(self.r)):
                return False, [], [f'P{i}' for i in range(self.p)]

            while True:
                allocated = False
                for i in range(self.p):
                    if not finish[i] and all(req[i][j] <= work[j] for j in range(self.r)):
                        for j in range(self.r):
                            work[j] += alloc[i][j]
                        finish[i] = True
                        safe_seq.append(f'P{i}')
                        allocated = True
                if not allocated:
                    break

            deadlocked = [f'P{i}' for i, done in enumerate(finish) if not done]
            return all(finish), safe_seq, deadlocked
        else:  # Single-Instance
            # Single-Instance: Simplified wait-for graph cycle detection
            # Build adjacency list for wait-for graph
            wait_for = [[] for _ in range(self.p)]
            for i in range(self.p):
                for j in range(self.r):
                    if req[i][j] > 0 and alloc[i][j] == 0 and avail[j] == 0:
                        # Find which process holds the resource
                        for k in range(self.p):
                            if alloc[k][j] > 0:
                                wait_for[i].append(k)
                                break

            ########### Detect cycle using DFS ##########
            visited = [False] * self.p
            rec_stack = [False] * self.p

            def dfs(node):
                visited[node] = True
                rec_stack[node] = True
                for neighbor in wait_for[node]:
                    if not visited[neighbor] and dfs(neighbor):
                        return True
                    elif rec_stack[neighbor]:
                        return True
                rec_stack[node] = False
                return False

            deadlocked = []
            for i in range(self.p):
                if not visited[i]:
                    if dfs(i):
                        deadlocked.append(f'P{i}')
            return len(deadlocked) == 0, [], deadlocked

    def prevent_deadlock(self, alloc, req, avail):
        # For simplicity, use multi-instance prevention logic
        work = avail[:]
        finish = [False] * self.p
        safe_seq = []
        ordered_processes = sorted(range(self.p), key=lambda i: sum(req[i]))

        for i in ordered_processes:
            if all(req[i][j] <= work[j] for j in range(self.r)):
                for j in range(self.r):
                    work[j] += alloc[i][j]
                finish[i] = True
                safe_seq.append(f'P{i}')

        deadlocked = [f'P{i}' for i, done in enumerate(finish) if not done]
        return all(finish), safe_seq, deadlocked

    def recover_deadlock(self, alloc, req, avail):
        deadlocked = self.detect_deadlock(alloc, req, avail)[2]
        return deadlocked[0] if deadlocked else None

class GraphVisualizer:
    @staticmethod
    def show_rag_graph(master, alloc, req, deadlocked, num_processes, num_resources):
        window = tb.Toplevel(master)
        window.title("Resource Allocation Graph")
        fig, ax = plt.subplots(figsize=(6, 4))
        G = nx.DiGraph()

        for i in range(num_processes):
            G.add_node(f'P{i}', color='red' if f'P{i}' in deadlocked else 'skyblue')
        for j in range(num_resources):
            G.add_node(f'R{j}', color='orange')

        edge_labels = {}
        for i in range(num_processes):
            for j in range(num_resources):
                if alloc[i][j] > 0:
                    G.add_edge(f'R{j}', f'P{i}')
                    edge_labels[(f'R{j}', f'P{i}')] = alloc[i][j]
                if req[i][j] > 0:
                    G.add_edge(f'P{i}', f'R{j}')
                    edge_labels[(f'P{i}', f'R{j}')] = req[i][j]

        pos = nx.spring_layout(G, k=0.5, iterations=50)
        colors = [data['color'] for _, data in G.nodes(data=True)]
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1000, font_size=10, ax=ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        ax.set_title("RAG (Red: Deadlocked Processes)")
        
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        tb.Button(window, text="Save Graph", command=lambda: fig.savefig("rag_graph.png"), bootstyle="success").pack(pady=5)
        canvas.draw()

    @staticmethod
    def show_charts(master, alloc, num_resources):
        alloc_sum = np.sum(alloc, axis=0)
        if np.sum(alloc_sum) == 0:
            messagebox.showinfo("Info", "No resources allocated to display charts.")
            return

        fig, axs = plt.subplots(1, 2, figsize=(9, 4))
        labels = [f'R{i}' for i in range(num_resources)]
        non_zero = [alloc_sum[i] for i in range(num_resources) if alloc_sum[i] > 0]
        non_zero_labels = [labels[i] for i in range(num_resources) if alloc_sum[i] > 0]

        if non_zero:
            axs[0].pie(non_zero, labels=non_zero_labels, autopct='%1.1f%%', startangle=90)
        else:
            axs[0].text(0.5, 0.5, "No Resources Allocated", ha='center', va='center', fontsize=12, color='red')
        axs[0].set_title("Resource Allocation")

        axs[1].bar(labels, alloc_sum, color='skyblue')
        axs[1].set_title("Allocated Units per Resource")
        axs[1].set_ylabel("Units")
        if not non_zero:
            axs[1].text(0.5, 0.5, "No Resources Allocated", ha='center', va='center', fontsize=12, color='red', transform=axs[1].transAxes)
        plt.tight_layout()

        chart_window = tb.Toplevel(master)
        chart_window.title("Resource Utilization Charts")
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()

class DeadlockGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Smart Deadlock Detection & Prevention System")
        self.master.geometry("800x600")
        self.master.resizable(True, True)
        self.num_processes = tk.IntVar()
        self.num_resources = tk.IntVar()
        self.theme_var = tk.StringVar(value="superhero")
        self.mode = tk.StringVar(value="Detection")
        self.instance_mode = tk.StringVar(value="Multi-Instance")  # New: Single or Multi-Instance
        self.style = tb.Style(theme=self.theme_var.get())
        self.manager = None
        self.alloc_entries = []
        self.req_entries = []
        self.available_entries = []
        print("Initializing GUI...")
        self.create_main_widgets()

    def create_main_widgets(self):
        print("Creating main widgets...")
        for widget in self.master.winfo_children():
            widget.destroy()

        # Main container frame
        main_frame = tb.Frame(self.master)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Image frame
        image_frame = tb.Frame(main_frame)
        image_frame.pack(pady=5)
        image_path = os.path.join("images", "ChatGPT Image Apr 10, 2025, 11_42_08 PM.png")
        print(f"Image path: {image_path}")
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found at {image_path}")
            img = Image.open(image_path)
            img = img.resize((150, 50), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            tb.Label(image_frame, image=self.logo).pack()
            print("Image loaded successfully.")
        except Exception as e:
            tb.Label(image_frame, text="Deadlock System", font=("Helvetica", 16)).pack()
            print(f"Error loading image: {e}")

        # Theme frame
        theme_frame = tb.Frame(main_frame)
        theme_frame.pack(pady=5)
        tb.Label(theme_frame, text="Theme:", font=("Helvetica", 11)).pack(side="left", padx=5)
        theme_menu = tb.OptionMenu(theme_frame, self.theme_var, self.theme_var.get(), *self.style.theme_names(), command=self.change_theme)
        theme_menu.pack(side="left")

        # Mode frame
        mode_frame = tb.Frame(main_frame)
        mode_frame.pack(pady=5)
        tb.Label(mode_frame, text="Mode:", font=("Helvetica", 11)).pack(side="left", padx=5)
        tb.OptionMenu(mode_frame, self.mode, self.mode.get(), "Detection", "Prevention").pack(side="left")

        # Instance Mode frame (new)
        instance_frame = tb.Frame(main_frame)
        instance_frame.pack(pady=5)
        tb.Label(instance_frame, text="Instance Mode:", font=("Helvetica", 11)).pack(side="left", padx=5)
        tb.OptionMenu(instance_frame, self.instance_mode, self.instance_mode.get(), "Single-Instance", "Multi-Instance").pack(side="left")

        # Input frame
        input_frame = tb.Frame(main_frame)
        input_frame.pack(pady=20)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)

        # Process input
        tb.Label(input_frame, text="Processes (1-10):", font=("Helvetica", 13)).grid(row=0, column=0, sticky="e", padx=5)
        tb.Entry(input_frame, textvariable=self.num_processes, width=10).grid(row=0, column=1, sticky="w", padx=5)

        # Resource input
        tb.Label(input_frame, text="Resources (1-10):", font=("Helvetica", 13)).grid(row=1, column=0, sticky="e", padx=5)
        tb.Entry(input_frame, textvariable=self.num_resources, width=10).grid(row=1, column=1, sticky="w", padx=5)

        # Next button
        tb.Button(input_frame, text="Next", command=self.create_matrix_inputs, bootstyle="primary").grid(row=2, column=0, columnspan=2, pady=10)

    def change_theme(self, theme):
        self.style.theme_use(theme)
        self.create_main_widgets()

    def create_matrix_inputs(self):
        print("Creating matrix inputs...")
        try:
            p = self.num_processes.get()
            r = self.num_resources.get()
            if p <= 0 or r <= 0 or p > 10 or r > 10:
                raise ValueError("Processes and resources must be between 1 and 10.")
        except:
            messagebox.showerror("Invalid Input", "Enter valid integers between 1 and 10.")
            return

        self.manager = DeadlockManager(p, r, instance_mode=self.instance_mode.get())
        self.p = p
        self.r = r
        self.alloc_entries = []
        self.req_entries = []
        self.available_entries = []

        # Destroy existing widgets except the top frames (image, theme, mode)
        for widget in self.master.winfo_children()[3:]:
            widget.destroy()

        # Main frame to hold input and matrix
        main_frame = self.master.winfo_children()[0]  # Get the main_frame
        input_frame = main_frame.winfo_children()[-1]  # Get the input_frame

        # Matrix frame below input frame
        matrix_frame = tb.Frame(main_frame)
        matrix_frame.pack(pady=10, after=input_frame)  # Pack matrix_frame after input_frame

        canvas = tk.Canvas(matrix_frame)
        scrollbar = tb.Scrollbar(matrix_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="center")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame.grid_rowconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tb.Label(scrollable_frame, text="Allocation Matrix", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=self.r, pady=5)
        tb.Label(scrollable_frame, text="(Resources currently held by each process)", font=("Helvetica", 10)).grid(row=1, column=0, columnspan=self.r)
        for i in range(self.p):
            row = []
            for j in range(self.r):
                entry = tb.Entry(scrollable_frame, width=5)
                entry.grid(row=i + 2, column=j, padx=2, pady=2)
                row.append(entry)
            self.alloc_entries.append(row)

        offset = self.p + 3
        tb.Label(scrollable_frame, text="Request Matrix", font=("Helvetica", 14)).grid(row=offset, column=0, columnspan=self.r, pady=5)
        tb.Label(scrollable_frame, text="(Additional resources needed by each process)", font=("Helvetica", 10)).grid(row=offset + 1, column=0, columnspan=self.r)
        for i in range(self.p):
            row = []
            for j in range(self.r):
                entry = tb.Entry(scrollable_frame, width=5)
                entry.grid(row=offset + i + 2, column=j, padx=2, pady=2)
                row.append(entry)
            self.req_entries.append(row)

        tb.Label(scrollable_frame, text="Available Resources:", font=("Helvetica", 13)).grid(row=offset + self.p + 3, column=0, columnspan=2, pady=5)
        tb.Label(scrollable_frame, text="(Free resources in the system)", font=("Helvetica", 10)).grid(row=offset + self.p + 4, column=0, columnspan=2)
        self.available_entries = [tb.Entry(scrollable_frame, width=5) for _ in range(self.r)]
        for j, entry in enumerate(self.available_entries):
            entry.grid(row=offset + self.p + 5, column=j, padx=2, pady=2)

        button_frame = tb.Frame(main_frame)
        button_frame.pack(pady=10)
        button_label = "Detect Deadlock" if self.mode.get() == "Detection" else "Prevent Deadlock"
        tb.Button(button_frame, text=button_label, command=self.process_deadlock, bootstyle="danger").pack(side="left", padx=5)
        tb.Button(button_frame, text="Save Config", command=self.save_config, bootstyle="info").pack(side="left", padx=5)
        tb.Button(button_frame, text="Load Config", command=self.load_config, bootstyle="info").pack(side="left", padx=5)
        tb.Button(button_frame, text="Back", command=self.confirm_back, bootstyle="secondary").pack(side="left", padx=5)

    def confirm_back(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to go back? Unsaved data will be lost."):
            self.create_main_widgets()

    def save_config(self):
        try:
            config = {
                "processes": self.p,
                "resources": self.r,
                "alloc": [[e.get() for e in row] for row in self.alloc_entries],
                "req": [[e.get() for e in row] for row in self.req_entries],
                "avail": [e.get() for e in self.available_entries]
            }
            with open("config.json", "w") as f:
                json.dump(config, f)
            messagebox.showinfo("Success", "Configuration saved!")
        except:
            messagebox.showerror("Error", "Failed to save configuration.")

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            
            if not all(key in config for key in ["processes", "resources", "alloc", "req", "avail"]):
                raise ValueError("Invalid configuration file: missing required keys.")
            if config["processes"] != self.p or config["resources"] != self.r:
                raise ValueError(f"Configuration mismatch: expected {self.p} processes and {self.r} resources, got {config['processes']} processes and {config['resources']} resources.")
            if len(config["alloc"]) != self.p or any(len(row) != self.r for row in config["alloc"]):
                raise ValueError("Allocation matrix size mismatch.")
            if len(config["req"]) != self.p or any(len(row) != self.r for row in config["req"]):
                raise ValueError("Request matrix size mismatch.")
            if len(config["avail"]) != self.r:
                raise ValueError("Available resources size mismatch.")

            self.master.config(cursor="wait")
            self.master.update()

            for i, row in enumerate(self.alloc_entries):
                for j, e in enumerate(row):
                    e.delete(0, tk.END)
                    e.insert(0, config["alloc"][i][j])

            for i, row in enumerate(self.req_entries):
                for j, e in enumerate(row):
                    e.delete(0, tk.END)
                    e.insert(0, config["req"][i][j])

            for j, e in enumerate(self.available_entries):
                e.delete(0, tk.END)
                e.insert(0, config["avail"][j])

            self.master.config(cursor="")
            messagebox.showinfo("Success", "Configuration loaded!")
        except ValueError as ve:
            self.master.config(cursor="")
            messagebox.showerror("Error", str(ve))
        except json.JSONDecodeError:
            self.master.config(cursor="")
            messagebox.showerror("Error", "Invalid configuration file format.")
        except FileNotFoundError:
            self.master.config(cursor="")
            messagebox.showerror("Error", "Configuration file not found.")
        except Exception as e:
            self.master.config(cursor="")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def process_deadlock(self):
        try:
            alloc = []
            for row in self.alloc_entries:
                row_vals = []
                for e in row:
                    if e.get().strip() == "":
                        raise ValueError("All fields must be filled.")
                    row_vals.append(int(e.get()))
                alloc.append(row_vals)
            
            req = []
            for row in self.req_entries:
                row_vals = []
                for e in row:
                    if e.get().strip() == "":
                        raise ValueError("All fields must be filled.")
                    row_vals.append(int(e.get()))
                req.append(row_vals)
            
            avail = []
            for e in self.available_entries:
                if e.get().strip() == "":
                    raise ValueError("All fields must be filled.")
                avail.append(int(e.get()))

            if any(x < 0 for row in alloc for x in row) or \
               any(x < 0 for row in req for x in row) or \
               any(x < 0 for x in avail):
                raise ValueError("Matrix values cannot be negative.")

            total_alloc = [sum(alloc[i][j] for i in range(self.p)) for j in range(self.r)]
            for j in range(self.r):
                if total_alloc[j] > avail[j] + total_alloc[j]:
                    raise ValueError(f"Total allocated R{j} exceeds system capacity.")
            for i in range(self.p):
                for j in range(self.r):
                    if req[i][j] > avail[j] + total_alloc[j]:
                        raise ValueError(f"Request for R{j} by P{i} exceeds available resources.")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        except:
            messagebox.showerror("Error", "Fill all fields with valid integers.")
            return

        if self.mode.get() == "Detection":
            is_safe, safe_seq, deadlocked = self.manager.detect_deadlock(alloc, req, avail)
            if is_safe:
                messagebox.showinfo("✅ Safe State", f"System is in Safe State.\nSafe Sequence: {' ➝ '.join(safe_seq)}")
            else:
                self.master.bell()
                winsound.Beep(1000, 500)  # Beep sound
                messagebox.showerror("❌ Deadlock Detected", f"Deadlock in: {', '.join(deadlocked) or 'None'} (Instance Mode: {self.instance_mode.get()})")
                recovery_proc = self.manager.recover_deadlock(alloc, req, avail)
                if recovery_proc:
                    messagebox.showinfo("Recovery Suggestion", f"Consider terminating {recovery_proc} to break deadlock.")
        else:
            is_safe, safe_seq, deadlocked = self.manager.prevent_deadlock(alloc, req, avail)
            if is_safe:
                messagebox.showinfo("✅ No Deadlock", f"Deadlock Prevented.\nSafe Order: {' ➝ '.join(safe_seq)}")
            else:
                messagebox.showwarning("⚠️ Partial Prevention", f"Could not prevent deadlock for: {', '.join(deadlocked) or 'None'}")

        GraphVisualizer.show_rag_graph(self.master, alloc, req, deadlocked, self.p, self.r)
        GraphVisualizer.show_charts(self.master, alloc, self.r)

if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = DeadlockGUI(root)
    root.mainloop()
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import urllib.request
import io
import datetime
import ttkbootstrap as tb
import time
from threading import Thread
from launchDataCollect import getData  
import matplotlib.pyplot as plt
import csv
from dbSetup import createDb

DB_NAME = "launchData.db"

# Global variables to store references
image_refs = {}
launches = []  # This will hold the list of launches
app = None  # Global variable to store app
search_timeout = None

def fetch_all_launches():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT Launch.id, Launch.rocketId, Launch.missionName, Launch.status,
               Launch.launchImageUrl, Launch.netTime, Rocket.name, Manufacturer.name
        FROM Launch
        JOIN Rocket ON Launch.rocketId = Rocket.id
        JOIN Manufacturer ON Rocket.manufacturerId = Manufacturer.id
    ''')
    launches = cursor.fetchall()
    conn.close()
    return launches

def fetch_full_launch_data(launch_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Launch WHERE id = ?', (launch_id,))
    launch = cursor.fetchone()

    rocket_id = launch[1]
    cursor.execute('SELECT * FROM Rocket WHERE id = ?', (rocket_id,))
    rocket = cursor.fetchone()

    manufacturer_id = rocket[13]
    cursor.execute('SELECT * FROM Manufacturer WHERE id = ?', (manufacturer_id,))
    manufacturer = cursor.fetchone()

    conn.close()
    return launch, rocket, manufacturer

def download_image(url, size=(150, 100)):
    try:
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        pil_image = Image.open(io.BytesIO(raw_data))
        thumbnail = pil_image.copy()
        thumbnail.thumbnail(size)
        return pil_image, ImageTk.PhotoImage(thumbnail)
    except Exception as e:
        print(f"Failed to download image: {e}")
        return None, None

def format_countdown(net_time_str):
    try:
        net_time = datetime.datetime.fromisoformat(net_time_str.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = net_time - now

        if delta.total_seconds() > 0:
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return "Launched"
    except Exception:
        return "Unknown"

def generate_pie_chart(tree):
    items = tree.get_children()
    rocket_names = [tree.set(item, "Rocket") for item in items]

    if not rocket_names:
        return

    from collections import Counter
    rocket_counts = Counter(rocket_names)

    plt.pie(rocket_counts.values(), labels=rocket_counts.keys(), autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title("Rocket Distribution")
    plt.show()

def update_treeview_countdown(tree, launches):
    for launch in launches:
        launch_id, rocket_id, mission_name, status, img_url, net_time, rocket_name, manufacturer_name = launch
        countdown = format_countdown(net_time)
        if tree.exists(launch_id):
            tree.item(launch_id, values=(rocket_name, mission_name, status, countdown, manufacturer_name))
    tree.after(1000, update_treeview_countdown, tree, launches)

def show_details(launch_id, rocket_image, manufacturer_logo):
    launch, rocket, manufacturer = fetch_full_launch_data(launch_id)

    detail_window = tk.Toplevel()
    detail_window.title("Launch Details")
    detail_window.geometry("950x850")

    notebook = ttk.Notebook(detail_window)
    notebook.pack(expand=True, fill="both")

    # Launch Tab
    launch_tab = ttk.Frame(notebook)
    notebook.add(launch_tab, text="Launch")

    labels = [
        ("Mission Name", launch[2]),
        ("Mission Description", launch[3]),
        ("Pad Name", launch[4]),
        ("Pad Location", launch[5]),
        ("Mission Orbit Abv", launch[6]),
        ("Mission Orbit", launch[7]),
        ("Status", launch[8]),
        ("Webcast Live", launch[9]),
        ("Launch Window Start", launch[10]),
        ("Launch Window End", launch[11]),
        ("Agencies", launch[13]),
        ("NET Time", launch[14]),
        ("Pad Description", launch[15]),
        ("Mission Type", launch[16]),
        ("Web Stream", launch[17]),
        ("Service Provider", launch[18]),
    ]

    for idx, (label, value) in enumerate(labels):
        ttk.Label(launch_tab, text=label + ":", font=('Helvetica', 11, 'bold')).grid(row=idx, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(launch_tab, text=value, font=('Helvetica', 11), wraplength=600, justify="left").grid(row=idx, column=1, sticky="w", padx=5, pady=2)

    # Rocket Tab
    rocket_tab = ttk.Frame(notebook)
    notebook.add(rocket_tab, text="Rocket")

    if rocket_image:
        pil_rocket = image_refs.get(launch_id, {}).get("pil_rocket")

        if pil_rocket:
            resized_pil = pil_rocket.resize((300, 200), Image.LANCZOS)
            resized_rocket_img = ImageTk.PhotoImage(resized_pil)

            img_label = ttk.Label(rocket_tab, image=resized_rocket_img)
            img_label.image = resized_rocket_img
            img_label.grid(row=0, column=1, pady=10)

    rocket_labels = [
        ("Rocket Name", rocket[1]),
        ("Variant", rocket[2]),
        ("Description", rocket[3]),
        ("Length (m)", rocket[4]),
        ("Diameter (m)", rocket[5]),
        ("Launch Mass (kg)", rocket[6]),
        ("Max Stages", rocket[7]),
        ("Thrust (kN)", rocket[8]),
        ("LEO Capacity (kg)", rocket[9]),
        ("GTO Capacity (kg)", rocket[10]),
        ("Total Launches", rocket[11]),
        ("Successful Launches", rocket[12])
    ]

    for idx, (label, value) in enumerate(rocket_labels):
        ttk.Label(rocket_tab, text=label + ":", font=('Helvetica', 11, 'bold')).grid(row=idx + 1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(rocket_tab, text=value, font=('Helvetica', 11), wraplength=600, justify="left").grid(row=idx + 1, column=1, sticky="w", padx=5, pady=2)

    # Manufacturer Tab
    manufacturer_tab = ttk.Frame(notebook)
    notebook.add(manufacturer_tab, text="Manufacturer")

    if manufacturer_logo:
        logo_label = ttk.Label(manufacturer_tab, image=manufacturer_logo)
        logo_label.image = manufacturer_logo
        logo_label.grid(row=0, column=1, pady=10)

    manufacturer_labels = [
        ("Manufacturer Name", manufacturer[1]),
        ("Description", manufacturer[2]),
        ("Country Code", manufacturer[4])
    ]

    for idx, (label, value) in enumerate(manufacturer_labels):
        ttk.Label(manufacturer_tab, text=label + ":", font=('Helvetica', 11, 'bold')).grid(row=idx + 1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(manufacturer_tab, text=value, font=('Helvetica', 11), wraplength=600, justify="left").grid(row=idx + 1, column=1, sticky="w", padx=5, pady=2)

def refresh_data_button_function(refresh_button, tree):
    def refresh_data():
        countdown_time = 30 * 60

        def update_button_text():
            nonlocal countdown_time
            minutes, seconds = divmod(countdown_time, 60)
            refresh_button.config(text=f"Timeout: {minutes:02}:{seconds:02}")
            countdown_time -= 1

            if countdown_time > 0:
                refresh_button.after(1000, update_button_text)
            else:
                refresh_button.config(state="normal", style="success.TButton", text="Refresh Data")

        refresh_button.config(state="disabled", style="TButton", text="Updating...")
        getData()
        global launches
        launches = fetch_all_launches()
        populate_tree(launches, tree)
        update_button_text()

    thread = Thread(target=refresh_data)
    thread.start()

def populate_tree(launches, tree, filter_text=""):
    tree.delete(*tree.get_children())

    for launch in launches:
        launch_id, rocket_id, mission_name, status, img_url, net_time, rocket_name, manufacturer_name = launch
        search_fields = f"{rocket_name} {mission_name} {status} {manufacturer_name}".lower()

        if filter_text.lower() not in search_fields:
            continue

        pil_img, rocket_thumb = download_image(img_url, size=(150, 100))

        if rocket_thumb:
            image_refs[launch_id] = {"rocket": rocket_thumb, "pil_rocket": pil_img}
            if tree.exists(launch_id):
                tree.item(launch_id, values=(rocket_name, mission_name, status, format_countdown(net_time), manufacturer_name), image=rocket_thumb)
            else:
                tree.insert("", "end", iid=launch_id, text="", image=rocket_thumb,
                            values=(rocket_name, mission_name, status, format_countdown(net_time), manufacturer_name))
        else:
            if tree.exists(launch_id):
                tree.item(launch_id, values=(rocket_name, mission_name, status, format_countdown(net_time), manufacturer_name), text="No Image")
            else:
                tree.insert("", "end", iid=launch_id, text="No Image",
                            values=(rocket_name, mission_name, status, format_countdown(net_time), manufacturer_name))

    update_treeview_countdown(tree, launches)
    if len(tree.get_children()) == 0:
        # Disable buttons if the tree is empty
        visualize_button.config(state="disabled")
        csvButton.config(state="disabled")
    else:
        # Enable buttons if the tree is not empty
        visualize_button.config(state="normal")
        csvButton.config(state="normal")

def on_search(*args):
    global search_timeout
    filter_text = search_var.get()

    if search_timeout:
        app.after_cancel(search_timeout)
    
    search_timeout = app.after(500, lambda: populate_tree(launches, tree, filter_text))

def show_message_async():
    # Run message box in a separate thread or after a small delay
    app.after(500, lambda: messagebox.showinfo("Data available", "Double click on items to view!"))


def main():
    createDb()
    global search_var, launches, tree, visualize_button, csvButton
    global app

    app = tb.Window(themename="darkly")
    app.title("Rocket Launch Viewer")
    app.geometry("1550x850")

    frame = ttk.Frame(app)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    frame.grid_columnconfigure(0, weight=1, minsize=200)
    frame.grid_columnconfigure(1, weight=0, minsize=150)

    search_var = tk.StringVar()
    search_entry = ttk.Entry(frame, textvariable=search_var, font=("Helvetica", 12))
    search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    refresh_button = ttk.Button(frame, text="Refresh Data", style="success.TButton", 
                                command=lambda: refresh_data_button_function(refresh_button, tree))
    refresh_button.grid(row=0, column=1, padx=5, pady=5)

    visualize_button = ttk.Button(frame, text="Visualize Rockets", style="info.TButton", command=lambda: generate_pie_chart(tree))
    visualize_button.grid(row=2, column=0, padx=5, pady=5)

    csvButton = ttk.Button(frame, text="Generate CSV", style="warning.TButton", command=lambda: exportToCsv(tree))
    csvButton.grid(row=2, column=1, padx=5, pady=5)

    columns = ("Rocket", "Mission", "Status", "Countdown", "Manufacturer")
    tree = ttk.Treeview(frame, columns=columns, show="tree headings", height=6)
    tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

    style = ttk.Style()
    style.configure("Treeview", rowheight=110, font=("Helvetica", 11))

    tree.heading("#0", text="Thumbnail")
    tree.column("#0", width=170, anchor="center")

    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_by(tree, _col, False))
        tree.column(col, width=210, anchor="center")

    launches = fetch_all_launches()
    populate_tree(launches, tree)

    def on_row_select(event):
        selected = tree.selection()
        if selected:
            launch_id = selected[0]
            _, rocket, manufacturer = fetch_full_launch_data(launch_id)
            manufacturer_logo = download_image(manufacturer[3], size=(240, 160))[1]
            rocket_image = image_refs.get(launch_id, {}).get("rocket")
            show_details(launch_id, rocket_image, manufacturer_logo)

    tree.bind("<Double-1>", on_row_select)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=1, column=2, sticky="ns")

    search_var.trace_add('write', lambda *args: on_search(*args))


    show_message_async()
    app.mainloop()

def sort_by(tree, col, descending):
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    try:
        data.sort(reverse=descending, key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0].lower())
    except Exception:
        data.sort(reverse=descending, key=lambda t: t[0].lower())

    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)

    tree.heading(col, command=lambda: sort_by(tree, col, not descending))

def exportToCsv(tree):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")],
                                             title="Save as")

    if not file_path:
        return  

    items = tree.get_children()

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Rocket", "Mission", "Status", "Countdown", "Manufacturer"])
        for item in items:
            values = tree.item(item, "values")
            writer.writerow(values)

if __name__ == "__main__":
    main()

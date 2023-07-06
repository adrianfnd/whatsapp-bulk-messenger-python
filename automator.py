from tkinter import Tk, Label, Button, filedialog, messagebox, Text, Scrollbar
from tkinter.ttk import Progressbar
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from urllib.parse import quote
import os

class WhatsAppMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Bulk Messenger")

        self.message = ""
        self.numbers = []
        self.total_number = 0

        self.create_widgets()

    def create_widgets(self):
        self.label_title = Label(self.root, text="WhatsApp Bulk Messenger", font=("Arial", 16, "bold"))
        self.label_title.pack(pady=20)

        self.message_label = Label(self.root, text="Pesan:")
        self.message_label.pack()

        self.message_input = Text(self.root, height=5, width=30)
        self.message_input.pack()

        self.btn_load_message = Button(self.root, text="Muat Pesan", command=self.load_message)
        self.btn_load_message.pack(pady=10)

        self.numbers_label = Label(self.root, text="Nomor:")
        self.numbers_label.pack()

        self.numbers_input = Text(self.root, height=5, width=30)
        self.numbers_input.pack()

        self.btn_load_numbers = Button(self.root, text="Muat Nomor", command=self.load_numbers)
        self.btn_load_numbers.pack(pady=10)

        self.progress_label = Label(self.root, text="Proses:")
        self.progress_label.pack()

        self.progress_bar = Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.btn_send_messages = Button(self.root, text="Kirim Pesan", command=self.send_messages)
        self.btn_send_messages.pack(pady=10)

    def load_message(self):
        file_path = filedialog.askopenfilename(filetypes=[("File Teks", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf8") as file:
                self.message = file.read()
            self.message_input.delete("1.0", "end")
            self.message_input.insert("end", self.message)
            messagebox.showinfo("Pesan Dimuat", "Pesan telah dimuat dengan berhasil.")

    def load_numbers(self):
        file_path = filedialog.askopenfilename(filetypes=[("File Teks", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                self.numbers = [line.strip() for line in file.read().splitlines() if line.strip() != ""]
            self.total_number = len(self.numbers)
            self.numbers_input.delete("1.0", "end")
            self.numbers_input.insert("end", "\n".join(self.numbers))
            messagebox.showinfo("Nomor Dimuat", f"{self.total_number} nomor telah dimuat dengan berhasil.")

    def send_messages(self):
        self.message = self.message_input.get("1.0", "end").strip()
        self.numbers = self.numbers_input.get("1.0", "end").strip().split("\n")

        if not self.message:
            messagebox.showerror("Error", "Tolong masukkan pesan.")
            return

        if not self.numbers:
            messagebox.showerror("Error", "Tolong masukkan nomor.")
            return

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--profile-directory=Default")
        options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

        os.system("")
        os.environ["WDM_LOG_LEVEL"] = "0"

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        messagebox.showinfo("Diperlukan Login", "Silakan masuk ke WhatsApp Web di jendela browser yang terbuka. Setelah masuk, klik OK untuk melanjutkan.")

        successful_numbers = []
        failed_numbers = []

        self.progress_bar["maximum"] = len(self.numbers)
        self.progress_bar["value"] = 0

        for idx, number in enumerate(self.numbers):
            self.progress_label.config(text=f"Proses: {idx+1}/{len(self.numbers)}")
            self.progress_bar["value"] = idx+1
            self.root.update()

            number = number.strip()
            if not number:
                continue

            try:
                url = f"https://web.whatsapp.com/send?phone={number}&text={quote(self.message)}"
                sent = False
                delay = 30

                for i in range(3):
                    if not sent:
                        driver.get(url)

                        try:
                            click_btn = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']")))
                        except Exception as e:
                            failed_numbers.append(number)
                            messagebox.showerror("Error", f"Gagal mengirim pesan ke: {number}\n\nPastikan ponsel dan komputer terhubung ke internet.")
                        else:
                            sleep(1)
                            click_btn.click()
                            sent = True
                            sleep(3)
                            break

                if sent:
                    successful_numbers.append(number)
                else:
                    failed_numbers.append(number)

            except Exception as e:
                failed_numbers.append(number)
                messagebox.showerror("Error", f"{e}")

        driver.close()

        self.progress_label.config(text="Proses: Selesai")
        self.progress_bar["value"] = 0
        self.root.update()

        messagebox.showinfo("Ringkasan Pengiriman Pesan", f"Pesan yang berhasil:\n\n{', '.join(successful_numbers)}\n\nPesan gagal:\n\n{', '.join(failed_numbers)}")


if __name__ == "__main__":
    root = Tk()
    app = WhatsAppMessenger(root)
    root.mainloop()

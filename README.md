```markdown
# 📂 File Management System (with Login & Registration)

A simple **Streamlit application** that allows users to **register, log in, and manage files** (create, delete, rename, copy, and move).  
The system includes basic user authentication using a text file (`users.txt`) for storing usernames and passwords.  

---

## 🚀 Features

✅ **User Authentication**  
- Register new users  
- Login with username & password  
- Session-based login state  

✅ **File Operations**  
- Create a new file with custom content  
- Delete files  
- Rename files  
- Copy files  
- Move files  

✅ **UI/UX**  
- Simple, interactive interface with Streamlit  
- Sidebar navigation (Login | Register | File Manager)  
- Success & error messages for all operations  

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – for the web interface  
- Python standard libraries: `os`, `shutil`  

---

## 📂 Project Structure

```

├── app.py          # Main Streamlit app
├── users.txt       # Stores registered users (username,password)
└── README.md       # Project documentation

````

---

## ▶️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/file-management-system.git
cd file-management-system
````

### 2. Install Dependencies

```bash
pip install streamlit
```

### 3. Run the App

```bash
streamlit run app.py
```

---

## 🖥️ Usage

1. **Register**

   * Go to `Register` tab in the sidebar
   * Enter a new username & password
   * Successfully registered users are saved in `users.txt`

2. **Login**

   * Go to `Login` tab
   * Enter username & password
   * On success, you’ll be redirected to File Manager

3. **Manage Files**

   * Create: Enter filename + content → click *Create File*
   * Delete: Enter filename → click *Delete File*
   * Rename: Enter old filename + new filename → click *Rename File*
   * Copy: Enter source filename + destination filename → click *Copy File*
   * Move: Enter source filename + destination path → click *Move File*
   * Logout anytime

---

## ⚠️ Notes & Limitations

* Passwords are stored as **plain text** in `users.txt` (⚠️ Not secure for production).
* Files are created relative to the project’s working directory.
* No role-based access control (all logged-in users can manage files).
* For real-world usage, consider:

  * Password hashing (e.g., `bcrypt`)
  * Database instead of text files
  * File permission handling

---

## 📌 Future Improvements

* 🔐 Secure password hashing
* 🗄️ Migrate users to a proper database (SQLite, PostgreSQL, etc.)
* 📤 File upload & download support
* 🎨 Better UI/UX with Streamlit components
* 📊 User-specific file access

---

## 👨‍💻 Author

Developed by **\Manish Kumar Sah** 🚀
Feel free to contribute, suggest improvements, or fork the repo!


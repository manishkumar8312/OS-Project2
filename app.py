import streamlit as st
import os
import shutil

USER_FILE = "users.txt"

# User management functions
def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username},{password}\n")

def user_exists(username):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r") as f:
        for line in f:
            if line.split(",")[0] == username:
                return True
    return False

def check_credentials(username, password):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r") as f:
        for line in f:
            user, pw = line.strip().split(",")
            if user == username and pw == password:
                return True
    return False

# File management functions
def create_file(filename, content):
    try:
        with open(filename, "w") as file:
            file.write(content)
        st.success(f"File '{filename}' created successfully.")
    except Exception as e:
        st.error(f"Errojjr creating file: {e}")

def delete_file(filename):
    try:
        os.remove(filename)
        st.success(f"File '{filename}' deleted successfully.")
    except FileNotFoundError:
        st.error(f"File '{filename}' not found.")
    except Exception as e:
        st.error(f"Error deleting file: {e}")

def rename_file(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        st.success(f"File '{old_name}' renamed to '{new_name}'.")
    except FileNotFoundError:
        st.error(f"File '{old_name}' not found.")
    except Exception as e:
        st.error(f"Error renaming file: {e}")

def copy_file(src, dest):
    try:
        shutil.copy(src, dest)
        st.success(f"File '{src}' copied to '{dest}'.")
    except FileNotFoundError:
        st.error(f"Source file '{src}' not found.")
    except Exception as e:
        st.error(f"Error copying file: {e}")

def move_file(src, dest):
    try:
        shutil.move(src, dest)
        st.success(f"File '{src}' moved to '{dest}'.")
    except FileNotFoundError:
        st.error(f"File '{src}' not found.")
    except Exception as e:
        st.error(f"Error moving file: {e}")

# Streamlit App
def main():
    st.title("File Management System")
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Menu", ["Login", "Register", "File Manager"])

    if menu == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_credentials(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")

    elif menu == "Register":
        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if user_exists(new_username):
                st.error("Username already exists.")
            else:
                save_user(new_username, new_password)
                st.success("User registered successfully!")

    elif menu == "File Manager":
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            st.subheader(f"Welcome, {st.session_state['username']}!")
            st.write("Use the options below to manage your files.")

            # File creation
            st.write("### Create File")
            filename = st.text_input("Filename")
            content = st.text_area("Content")
            if st.button("Create File"):
                create_file(filename, content)

            # File deletion
            st.write("### Delete File")
            del_filename = st.text_input("Filename to Delete")
            if st.button("Delete File"):
                delete_file(del_filename)

            # File renaming
            st.write("### Rename File")
            old_name = st.text_input("Old Filename")
            new_name = st.text_input("New Filename")
            if st.button("Rename File"):
                rename_file(old_name, new_name)

            # File copying
            st.write("### Copy File")
            src = st.text_input("Source File")
            dest = st.text_input("Destination File")
            if st.button("Copy File"):
                copy_file(src, dest)

            # File moving
            st.write("### Move File")
            move_src = st.text_input("Source File to Move")
            move_dest = st.text_input("Destination Path")
            if st.button("Move File"):
                move_file(move_src, move_dest)

            # Logout
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.success("Logged out successfully!")
        else:
            st.error("Please log in to access the File Manager.")

if __name__ == "__main__":
    main()
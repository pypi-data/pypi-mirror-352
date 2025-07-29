import questionary

choice = questionary.select(
    "What do you want to do?",
    choices=[
        "Start the app",
        "Settings",
        "Help",
        "Exit"
    ]
).ask()

print(f"You selected: {choice}")

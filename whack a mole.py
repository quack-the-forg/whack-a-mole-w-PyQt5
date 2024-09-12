import sys
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout, QHBoxLayout, 
                             QLCDNumber, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt

MIN_ROWS, MAX_ROWS = 3, 5
MIN_COLS, MAX_COLS = 3, 5
MIN_TIME, MAX_TIME = 15, 60

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Game Settings")
        self.layout = QFormLayout()

        # Input fields for duration, rows, and columns
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText(f"Enter duration ({MIN_TIME}-{MAX_TIME} seconds)")
        self.layout.addRow("Game Duration:", self.duration_input)
        self.rows_input = QLineEdit(self)
        self.rows_input.setPlaceholderText(f"Enter number of rows ({MIN_ROWS}-{MAX_ROWS})")
        self.layout.addRow("Number of Rows:", self.rows_input)

        self.cols_input = QLineEdit(self)
        self.cols_input.setPlaceholderText(f"Enter number of columns ({MIN_COLS}-{MAX_COLS})")
        self.layout.addRow("Number of Columns:", self.cols_input)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)

    def get_values(self):
        return self.duration_input.text(), self.rows_input.text(), self.cols_input.text()

class WhackAMoleGame(QWidget):
    def __init__(self, duration, rows, cols):
        super().__init__()
        
        # Load image of mole
        self.mole_pixmap = QPixmap("mole.png")

        # Game settings
        self.grid_size = (rows, cols)  # User-defined grid size
        self.mole_buttons = []
        self.score = 0
        self.time_left = duration

        # Set up UI
        self.initUI()

        # Set up a timer for moles to appear
        self.mole_timer = QTimer(self)
        self.mole_timer.timeout.connect(self.show_random_mole)
        self.mole_timer.start(1000)  # 1 second interval

        # Set up a timer for game time countdown
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_time)
        self.game_timer.start(1000)  # 1 second interval

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Score display
        score_layout = QHBoxLayout()
        self.score_label = QLabel(f"Score: {self.score}")
        score_layout.addWidget(self.score_label)

        # Timer display
        self.time_display = QLCDNumber()
        self.time_display.display(self.time_left)
        score_layout.addWidget(QLabel("Time Left:"))
        score_layout.addWidget(self.time_display)

        main_layout.addLayout(score_layout)

        # Grid layout for moles
        grid_layout = QGridLayout()

        # Set up the grid dynamically based on user input
        rows, cols = self.grid_size
        for i in range(rows):
            for j in range(cols):
                button = QPushButton(self)
                button.setFixedSize(100, 100)
                button.setText("")  # Initially no mole
                button.clicked.connect(self.hit_mole)
                self.mole_buttons.append(button)
                grid_layout.addWidget(button, i, j)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

        # Window settings
        self.setWindowTitle("Whack-a-Mole")
        self.resize(400, 400)

    def show_random_mole(self):
        # Clear all buttons
        for button in self.mole_buttons:
            button.setIcon(QIcon())  # Remove the icon (no mole)
            button.setEnabled(False)

        # Select a random button to be the mole
        mole = random.choice(self.mole_buttons)
        mole.setIcon(QIcon(self.mole_pixmap))  # Set mole image
        mole.setIconSize(mole.size())  # Resize the icon to fit the button
        mole.setEnabled(True)
        
    def hit_mole(self):
        sender = self.sender()
        if sender.isEnabled() and not sender.icon().isNull():  # Check if there's an icon (mole)
            self.score += 1
            self.score_label.setText(f"Score: {self.score}")
            sender.setIcon(QIcon())  # Remove the icon
            sender.setEnabled(False)
            self.show_random_mole()  # Move mole to a new square

    def update_time(self):
        self.time_left -= 1
        self.time_display.display(self.time_left)

        if self.time_left == 0:
            self.end_game()

    def end_game(self):
        self.mole_timer.stop()
        self.game_timer.stop()

        # Save the score to a file
        with open("score.txt", "a") as f:
            f.write(f"Score: {self.score}\n")

        # Display final score
        QMessageBox.information(self, "Game Over", f"Time's up! Your final score is {self.score}.")
        self.close()

def main():
    app = QApplication(sys.argv)

    while True:
        # Create and display the input dialog
        input_dialog = InputDialog()
        if input_dialog.exec_() == QDialog.Accepted:
            duration_text, rows_text, cols_text = input_dialog.get_values()

            # Convert input values to integers, handle validation
            try:
                duration = int(duration_text)
                rows = int(rows_text)
                cols = int(cols_text)

                if MIN_TIME <= duration <= MAX_TIME and MIN_ROWS <= rows <= MAX_ROWS and MIN_COLS <= cols <= MAX_COLS: # Grid has to be between 3x3 and 5x5
                    game = WhackAMoleGame(duration, rows, cols)
                    game.show()
                    app.exec_()  # Run the game loop
                    
                    # After the game ends, ask the user if they want to play again
                    replay = QMessageBox.question(None, "Play Again?", "Would you like to play another game?", 
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if replay == QMessageBox.No:
                        break  # Exit the loop and close the application
                else:
                    QMessageBox.warning(None, "Invalid Input", f"Please enter valid values for duration ({MIN_TIME}-{MAX_TIME}), rows ({MIN_ROWS}-{MAX_ROWS}), and columns ({MIN_COLS}-{MAX_COLS}).")
            except ValueError:
                QMessageBox.warning(None, "Invalid Input", "Please enter valid integer values.")
        else:
            break  # Exit the loop if the dialog is cancelled

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
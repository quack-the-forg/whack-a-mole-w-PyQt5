import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout, QHBoxLayout, QInputDialog, QLCDNumber, QMessageBox
from PyQt5.QtCore import QTimer, QTime, Qt

class WhackAMoleGame(QWidget):
    def __init__(self, duration):
        super().__init__()

        # Game settings
        self.grid_size = 3  # 3x3 grid
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

        for i in range(self.grid_size):
            for j in range(self.grid_size):
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
            button.setText("")
            button.setEnabled(False)

        # Select a random button to be the mole
        mole = random.choice(self.mole_buttons)
        mole.setText("mole")
        mole.setEnabled(True)

    def hit_mole(self):
        sender = self.sender()
        if sender.isEnabled() and sender.text() == "mole":
            self.score += 1
            self.score_label.setText(f"Score: {self.score}")
            sender.setText("")
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

    # Prompt the user to enter the game duration
    duration, ok = QInputDialog.getInt(None, "Game Duration", "Enter game duration (15-60 seconds):", 30, 15, 60)
    if not ok:
        sys.exit()

    game = WhackAMoleGame(duration)
    game.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
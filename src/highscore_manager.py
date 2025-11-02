import json
import os
from src import config
from src.utils import get_data_path

class HighScoreManager:
    def __init__(self, highscore_file='highscores.json'):
        self.highscore_file = get_data_path(highscore_file)
        self.scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(self.highscore_file):
            with open(self.highscore_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_scores(self):
        try:
            with open(self.highscore_file, 'w') as f:
                json.dump(self.scores, f)
        except IOError as e:
            print(f"Error saving high scores to {self.highscore_file}: {e}")

    def add_score(self, score):
        self.scores.append(score)
        self.scores.sort(reverse=True)
        self.scores = self.scores[:config.MAX_HIGH_SCORES]
        self.save_scores()

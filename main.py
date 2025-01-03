import pygame
import random
import pandas as pd
from datetime import datetime
import json
import os

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake Game Analytics')
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        
        # Game variables
        self.block_size = 20
        self.clock = pygame.time.Clock()
        self.fps = 15
        
        # Analytics data
        self.game_data = []
        self.current_game = {
            'timestamp': None,
            'score': 0,
            'duration': 0,
            'moves': 0,
            'food_positions': [],
            'death_position': None
        }
        
        self.reset_game()
        
    def reset_game(self):
        self.snake_pos = [[self.width/2, self.height/2]]
        self.snake_direction = [self.block_size, 0]
        self.food_pos = self.generate_food()
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.current_game = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': 0,
            'duration': 0,
            'moves': 0,
            'food_positions': [list(self.food_pos)],
            'death_position': None
        }
        
    def generate_food(self):
        while True:
            x = random.randrange(0, self.width, self.block_size)
            y = random.randrange(0, self.height, self.block_size)
            if [x, y] not in self.snake_pos:
                return [x, y]
    
    def move_snake(self):
        new_head = [self.snake_pos[0][0] + self.snake_direction[0],
                   self.snake_pos[0][1] + self.snake_direction[1]]
        
        # Check if snake ate food
        if new_head == self.food_pos:
            self.food_pos = self.generate_food()
            self.score += 1
            self.current_game['score'] = self.score
            self.current_game['food_positions'].append(list(self.food_pos))
        else:
            self.snake_pos.pop()
        
        self.snake_pos.insert(0, new_head)
        self.current_game['moves'] += 1
        
    def check_collision(self):
        head = self.snake_pos[0]
        
        # Wall collision
        if (head[0] >= self.width or head[0] < 0 or
            head[1] >= self.height or head[1] < 0):
            return True
            
        # Self collision
        if head in self.snake_pos[1:]:
            return True
            
        return False
    
    def save_game_data(self):
        self.current_game['duration'] = (pygame.time.get_ticks() - self.start_time) / 1000
        self.current_game['death_position'] = list(self.snake_pos[0])
        self.game_data.append(self.current_game)
        
        # Save to JSON file
        with open('game_data.json', 'w') as f:
            json.dump(self.game_data, f)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.snake_direction[1] != self.block_size:
                        self.snake_direction = [0, -self.block_size]
                    elif event.key == pygame.K_DOWN and self.snake_direction[1] != -self.block_size:
                        self.snake_direction = [0, self.block_size]
                    elif event.key == pygame.K_LEFT and self.snake_direction[0] != self.block_size:
                        self.snake_direction = [-self.block_size, 0]
                    elif event.key == pygame.K_RIGHT and self.snake_direction[0] != -self.block_size:
                        self.snake_direction = [self.block_size, 0]
            
            self.move_snake()
            
            if self.check_collision():
                self.save_game_data()
                self.reset_game()
            
            # Draw everything
            self.screen.fill(self.BLACK)
            
            # Draw snake
            for pos in self.snake_pos:
                pygame.draw.rect(self.screen, self.GREEN, 
                               pygame.Rect(pos[0], pos[1], self.block_size, self.block_size))
            
            # Draw food
            pygame.draw.rect(self.screen, self.RED,
                           pygame.Rect(self.food_pos[0], self.food_pos[1], 
                                     self.block_size, self.block_size))
            
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', True, self.WHITE)
            self.screen.blit(score_text, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()

# analytics.py
def analyze_game_data():
    try:
        with open('game_data.json', 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        analysis = {
            'total_games': len(df),
            'average_score': df['score'].mean(),
            'max_score': df['score'].max(),
            'average_duration': df['duration'].mean(),
            'total_moves': df['moves'].sum(),
            'moves_per_game': df['moves'].mean()
        }
        
        # Save analysis
        with open('game_analysis.json', 'w') as f:
            json.dump(analysis, f)
            
        return analysis
        
    except FileNotFoundError:
        return "No game data available yet."

# main.py
if __name__ == "__main__":
    game = SnakeGame()
    game.run()
    analysis = analyze_game_data()
    print("\nGame Analysis:")
    print(analysis)

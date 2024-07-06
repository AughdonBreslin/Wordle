import numpy as np
import time

from collections import Counter
from datetime import timedelta
from typing import Dict

from tree import Tree

APPROACHES = ['sl_buckets', 'info_theory']
MAX_INT = 1000000000

class WordleBot():
    def __init__(self, approach : str = 'info_theory'):
        self.approach = approach
        self.guesses : list[str] = open('data/candidate_guesses.csv', 'r').read().split('\n')
        self.solutions : list[str] = open('data/valid_solutions.csv', 'r').read().split('\n')
        self.solved_paths : Tree = Tree()
                                                           
    def wordle_response(self, guess : str, solution : str) -> str:
        '''
        guess: a string of 5 letters
        solution: a string of 5 letters
        return: a list of 5 integers where
        - 0 means the letter is not in the solution
        - 1 means the letter is in the solution but in the wrong position
        - 2 means the letter is in the solution and in the right position
        '''
        if len(guess) != len(solution):
            print(f"Error: Guess length of {len(guess)} does not match solution length of {len(solution)}.")
            return -1

        result = [0] * len(guess)
        letter_occurrences = Counter(solution)
        for i in range(len(guess)):
            if guess[i] == solution[i]:
                result[i] = 2
                letter_occurrences[guess[i]] -= 1
        for i in range(len(guess)):
            if result[i] != 2 and letter_occurrences[guess[i]] > 0:
                result[i] = 1
                letter_occurrences[guess[i]] -= 1
        return "".join(map(str, result))
    
    def guess_response_distributions(self, valid_solutions : list[str]) -> Dict[str, Counter]:
        '''
        Count the size of the buckets for each guess.
        valid_solutions: a list of valid solutions
        return: a dictionary of guesses and their corresponding response distributions
        '''
        guess_response_distributions = {}
        for guess in self.guesses:
            print(f"\t\t\tCounting size of buckets: {guess[0]}/z", end='\r')
            bucket_distribution = Counter()
            for solution in valid_solutions:
                response = self.wordle_response(guess, solution)
                bucket_distribution[response] += 1
            guess_response_distributions[guess] = bucket_distribution
        return guess_response_distributions

    def best_guess_sl_buckets(self, guess_response_distributions : Dict[str, Counter]):
        '''
        Smallest largest buckets, or sl_buckets.
        guess_response_distributions: a dictionary of guesses and their corresponding response distributions
        return: the guess with the smallest largest buckets
        '''
        best_distribution : list[tuple[str, int]] = [('_____', MAX_INT)]
        best_guess = ''
        for guess in guess_response_distributions:
            sorted_distribution : list[tuple[str, int]] = guess_response_distributions[guess].most_common()
            if sorted_distribution[0][1] == 1 and '22222' in sorted_distribution:
                best_distribution = sorted_distribution
                best_guess = guess
                return best_guess
            for i, (response, count) in enumerate(sorted_distribution):
                if count > best_distribution[i][1]:
                    # Larger ith largest bucket
                    break
                if count < best_distribution[i][1]:
                    best_distribution = sorted_distribution
                    best_guess = guess
                    break
                # if get to end, add in: no way! identical dist
        return best_guess
    
    def best_guess_info_theory(self, guess_response_distributions : Dict[str, Counter]):
        '''
        Information theory approach to finding the best guess: -Σp(x)lg(p(x))
        guess_response_distributions: a dictionary of guesses and their corresponding response distributions
        return: the guess with the highest expected information gain
        '''
        best_guess = ''
        max_expected_info = 0
        for guess in guess_response_distributions:
            p_x = [guess_response_distributions[guess][response]/sum(guess_response_distributions[guess].values()) for response in guess_response_distributions[guess]]
            info_gain = -sum([p_x[i] * np.log2(p_x[i]) for i in range(len(p_x))])
            if info_gain > max_expected_info:
                max_expected_info = info_gain
                best_guess = guess
        return best_guess

    def find_response_buckets(self, best_guess : str, valid_solutions : list) -> Dict[str, list]:
        '''
        Given a guess, find the solution words that fall into each response.
        best_guess: a string of 5 letters
        valid_solutions: a list of valid solutions
        return: a dictionary of responses and their corresponding potential solutions
        '''
        response_buckets = {}
        for solution in valid_solutions:
            response = self.wordle_response(best_guess, solution)
            if response not in response_buckets:
                response_buckets[response] = []
            response_buckets[response].append(solution)
        return response_buckets

    def find_path(self, solution, scoring_function):
        '''
        Find the path to the solution using the scoring function.
        solution: a string of 5 letters
        scoring_function: a function that takes in a dictionary of guesses and their corresponding response distributions and returns the best guess
        return: a list of guesses and their corresponding responses
        '''
        guess_info = []
        solutions : list[str] = self.solutions
        path = []

        while len(solutions) > 1:
            best_guess_node = self.solved_paths.search(path)
            if best_guess_node is None:
                guess_response_distributions : Dict[str, Counter] = self.guess_response_distributions(solutions)
                best_guess : str = scoring_function(guess_response_distributions)
                self.solved_paths.insert(best_guess, path)
            else:
                best_guess = best_guess_node.value
            
            response : str = self.wordle_response(best_guess, solution)
            response_buckets : Dict[str, list] = self.find_response_buckets(best_guess, solutions)
            solutions = response_buckets[response]
            guess_info.append([best_guess, response])
            path.append(response)
        guess_info.append([solutions[0], self.wordle_response(solutions[0], solution)])
        self.solved_paths.insert(solutions[0], path)
        return guess_info
    
    def solve_wordle(self):
        '''
        Solve the wordle game for all solutions.
        '''
        solve_times = []
        scoring_function = getattr(self, f"best_guess_{self.approach}")
        for i, solution in enumerate(self.solutions):
            print(f"{i}/{len(self.solutions)} solutions", end='\r')
            start = time.time()
            guess_info = self.find_path(solution, scoring_function)
            end = time.time()
            print(f"Solved {solution} in {len(guess_info)} guesses: {guess_info}")
            print(f"Solved {solution} in {timedelta(seconds=end-start)} seconds.")
            solve_times.append(len(guess_info))
        
        print(f"Expected number of guesses: {sum(solve_times)/len(self.solutions)}.")
        

    def save_solved_paths(self):
        '''
        Save the solved paths to a text file.
        '''
        with open(f'results/{self.approach}.json', 'w') as f:
            f.write(self.solved_paths.to_json())
            
if __name__ == '__main__':
    approach = 'info_theory'
    bot = WordleBot(approach)
    bot.solve_wordle()
    bot.save_solved_paths()




                

    
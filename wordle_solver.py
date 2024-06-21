import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns

from collections import Counter
from typing import Dict

MAX_INT = 1000000000

class WordleBot():
    def __init__(self):
        self.guesses : list[str] = open('candidate_guesses.csv', 'r').read().split('\n')
        if self.guesses[0] == 'word':
            self.guesses = self.guesses[1:]
        if self.guesses[-1] == '':
            self.guesses = self.guesses[:-1]
        self.solutions : list[str] = open('valid_solutions.csv', 'r').read().split('\n')
        if self.solutions[0] == 'word':
            self.solutions = self.solutions[1:]
        if self.solutions[-1] == '':
            self.solutions = self.solutions[:-1]
        self.solved_buckets : Dict[str, Dict] = {}
                                                           
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
            print(len(guess), len(solution))
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
        guess_response_distributions = {}

        best_guess = ''
        sl_bucket_size = MAX_INT
        for guess in self.guesses:
            print(f"\t\t\tTallying guess responses: {guess[0]}/z", end='\r')
            bucket_distribution = Counter()
            for solution in valid_solutions:
                response = self.wordle_response(guess, solution)
                bucket_distribution[response] += 1
            guess_response_distributions[guess] = bucket_distribution
        return guess_response_distributions

    def best_guess(self, guess_response_distributions : Dict[str, Counter]):
        best_distribution : list[tuple[str, int]] = [('00000', MAX_INT)]
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

    def find_response_buckets(self, best_guess : str, valid_solutions : list) -> Dict[str, list]:
        response_buckets = {}
        for solution in valid_solutions:
            response = self.wordle_response(best_guess, solution)
            if response not in response_buckets:
                response_buckets[response] = []
            response_buckets[response].append(solution)
        return response_buckets


    # Total flow:
    # Using the base best candidate 'raise', characterized by a tied smallest largest bucket and the smallest second largest bucket, as our root
    # Wait for a response from the user, and enter the response bucket corresponding to the wordle_feedback
    # With a restricted set of valid solutions, determine a new best candidate and repeat.

    # Note: when len(valid_solutions) == 1: it immediately becomes the best candidate.
    #  when 1 is the size of the largest bucket, if there exists a bucket with 22222, add it to the best candidates, then return one
    def solve(self, solution):
        guess_info = []
        solutions : list[str] = self.solutions
        while len(solutions) > 1:
            guess_response_distributions : Dict[str, Counter] = self.guess_response_distributions(solutions)
            best_guess : str = self.best_guess(guess_response_distributions)
            # print(f"\nBest Guess: {best_guess}, guess_response_dist: {guess_response_distributions[best_guess]}", end='\r')
            # depth = 0
            # for info in guess_info:
            #     if depth == 0:
            #         if info[0] not in self.solved_buckets:
            #             response_buckets : Dict[str, list] = self.find_response_buckets(best_guess, solutions)
            #             self.solved_buckets[best_guess] = response_buckets
            #         else:
            #             response_buckets = self.solved_buckets[best_guess]
            #     elif depth == 1:
            #         if info[0] not in self.solved_buckets[guess_info[depth-1][0]][best_guess]:
            #             response_buckets : Dict[str, list] = self.find_response_buckets(best_guess, solutions)
            #             self.solved_buckets[guess_info[depth-1][0]][best_guess] = response_buckets
            #         else:
            #             response_buckets = self.solved_buckets[guess_info[depth-1][0]][best_guess] 
            response_buckets : Dict[str, list] = self.find_response_buckets(best_guess, solutions)
            response : str = self.wordle_response(best_guess, solution)
            solutions = response_buckets[response]
            # print(f"\nRefined list of solutions after response {response} : {solutions}", end='\r')
            guess_info.append([best_guess, response])
        guess_info.append([solutions[0], self.wordle_response(solutions[0], solution)])
        return guess_info

if __name__ == '__main__':
    bob = WordleBot()
    solutions = open('valid_solutions.csv', 'r').read().split('\n')[1:]
    solve_times = []
    for i, solution in enumerate(solutions):
        print(f"{i}/{len(solutions)} solutions", end='\r')
        guess_info = bob.solve(solution)
        print(f"Solved {solution} in {len(guess_info)} guesses: {guess_info}")
        solve_times.append(len(guess_info) + 1)
    print(f"Method expected solve time: {sum(solve_times)/len(solutions)}.")



                

    
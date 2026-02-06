"""
Challenges - Skill tests that tributes must complete to survive.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum
import random


class ChallengeType(Enum):
    """Types of challenges tributes can face."""
    CODE_GOLF = "code_golf"       # Shortest code wins
    SPEED_SOLVE = "speed_solve"   # First to answer
    LOGIC_PUZZLE = "logic_puzzle" # Reasoning test
    TRIVIA = "trivia"             # Knowledge test
    TASK = "task"                 # Complete an objective


@dataclass
class ChallengeResult:
    """Result of a tribute attempting a challenge."""
    success: bool
    score: int = 0
    time_ms: int = 0
    answer: Any = None
    damage_taken: int = 0


class Challenge(ABC):
    """Base class for all challenge types."""
    
    challenge_type: ChallengeType
    difficulty: int  # 1-10
    time_limit_seconds: int
    
    @abstractmethod
    def generate(self) -> dict:
        """Generate the challenge prompt and expected answer."""
        pass
    
    @abstractmethod
    def evaluate(self, answer: Any) -> ChallengeResult:
        """Evaluate a tribute's answer."""
        pass


class CodeGolfChallenge(Challenge):
    """Write the shortest code to solve a problem."""
    
    challenge_type = ChallengeType.CODE_GOLF
    
    PROBLEMS = [
        {
            "prompt": "Write a function that returns the sum of two numbers",
            "test_cases": [(1, 2, 3), (0, 0, 0), (-1, 1, 0)],
            "optimal_length": 15,
        },
        {
            "prompt": "Write a function that reverses a string",
            "test_cases": [("hello", "olleh"), ("a", "a"), ("", "")],
            "optimal_length": 12,
        },
        {
            "prompt": "Write a function that checks if a number is prime",
            "test_cases": [(2, True), (4, False), (17, True), (1, False)],
            "optimal_length": 45,
        },
        {
            "prompt": "Write a function that returns the fibonacci number at index n",
            "test_cases": [(0, 0), (1, 1), (10, 55)],
            "optimal_length": 35,
        },
    ]
    
    def __init__(self, difficulty: int = 5):
        self.difficulty = difficulty
        self.time_limit_seconds = 120
        self.current_problem = None
    
    def generate(self) -> dict:
        self.current_problem = random.choice(self.PROBLEMS)
        return {
            "type": self.challenge_type.value,
            "prompt": self.current_problem["prompt"],
            "time_limit": self.time_limit_seconds,
            "scoring": "Shortest working solution wins. Non-working = elimination.",
        }
    
    def evaluate(self, answer: str) -> ChallengeResult:
        # In production, this would run the code in a sandbox
        # For now, score based on length
        if not answer or not isinstance(answer, str):
            return ChallengeResult(success=False, damage_taken=100)
        
        code_length = len(answer.replace(" ", "").replace("\n", ""))
        optimal = self.current_problem["optimal_length"]
        
        # Score: 100 for optimal, decreasing with length
        score = max(0, 100 - (code_length - optimal))
        
        return ChallengeResult(
            success=True,
            score=score,
            answer=answer,
        )


class TriviaChallenge(Challenge):
    """Answer trivia questions correctly."""
    
    challenge_type = ChallengeType.TRIVIA
    
    QUESTIONS = [
        {"q": "What year was Python first released?", "a": "1991"},
        {"q": "Who created Linux?", "a": "linus torvalds"},
        {"q": "What does HTTP stand for?", "a": "hypertext transfer protocol"},
        {"q": "What is the time complexity of binary search?", "a": "o(log n)"},
        {"q": "What port does HTTPS use by default?", "a": "443"},
        {"q": "What language is the Linux kernel written in?", "a": "c"},
        {"q": "What does SQL stand for?", "a": "structured query language"},
        {"q": "What year was Bitcoin created?", "a": "2009"},
    ]
    
    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.time_limit_seconds = 30
        self.current_question = None
    
    def generate(self) -> dict:
        self.current_question = random.choice(self.QUESTIONS)
        return {
            "type": self.challenge_type.value,
            "question": self.current_question["q"],
            "time_limit": self.time_limit_seconds,
        }
    
    def evaluate(self, answer: str) -> ChallengeResult:
        if not answer:
            return ChallengeResult(success=False, damage_taken=50)
        
        correct = self.current_question["a"].lower()
        given = str(answer).lower().strip()
        
        if given == correct or correct in given:
            return ChallengeResult(success=True, score=100)
        else:
            return ChallengeResult(success=False, score=0, damage_taken=25)


class LogicPuzzleChallenge(Challenge):
    """Solve logic puzzles."""
    
    challenge_type = ChallengeType.LOGIC_PUZZLE
    
    PUZZLES = [
        {
            "prompt": "What is the next number in the sequence: 2, 6, 12, 20, 30, ?",
            "answer": "42",
            "hint": "Differences increase by 2 each time",
        },
        {
            "prompt": "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops Lazzies?",
            "answer": "yes",
        },
        {
            "prompt": "What is 15% of 80?",
            "answer": "12",
        },
        {
            "prompt": "A farmer has 17 sheep. All but 9 die. How many are left?",
            "answer": "9",
        },
    ]
    
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.time_limit_seconds = 60
        self.current_puzzle = None
    
    def generate(self) -> dict:
        self.current_puzzle = random.choice(self.PUZZLES)
        return {
            "type": self.challenge_type.value,
            "puzzle": self.current_puzzle["prompt"],
            "time_limit": self.time_limit_seconds,
        }
    
    def evaluate(self, answer: str) -> ChallengeResult:
        if not answer:
            return ChallengeResult(success=False, damage_taken=50)
        
        correct = self.current_puzzle["answer"].lower()
        given = str(answer).lower().strip()
        
        if given == correct:
            return ChallengeResult(success=True, score=100)
        else:
            return ChallengeResult(success=False, score=0, damage_taken=30)


def get_random_challenge(difficulty: int = 5) -> Challenge:
    """Get a random challenge of the given difficulty."""
    challenge_classes = [CodeGolfChallenge, TriviaChallenge, LogicPuzzleChallenge]
    cls = random.choice(challenge_classes)
    return cls(difficulty=difficulty)

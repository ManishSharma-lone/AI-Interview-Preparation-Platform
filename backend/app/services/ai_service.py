import json
import logging
from typing import List, Dict, Any
from backend.app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIService")

class AIService:
    @staticmethod
    def _get_mock_questions(role_type: str, difficulty: str, interview_type: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generates realistic mock questions based on parameters."""
        logger.info(f"Generating mock questions for {role_type} | {difficulty} | {interview_type} (Count: {num_questions})")
        
        hr_questions = [
            "Tell me about a time you had a conflict with a team member and how you resolved it.",
            "Why do you want to join our company and what value do you bring?",
            "Describe a challenging project you worked on and how you handled setbacks.",
            "Where do you see yourself in five years and how does this role fit your career path?",
            "How do you prioritize your tasks when managing multiple tight deadlines?"
        ]

        tech_questions = {
            "Software Engineer": [
                "What is the difference between a process and a thread, and how do they handle memory?",
                "Explain the concepts of RESTful APIs and contrast them with GraphQL/gRPC.",
                "How do databases index columns, and what are the trade-offs of having too many indexes?",
                "What is dependency injection, and why is it useful in building scalable software?",
                "Describe how you would design a rate limiter for a high-traffic microservice."
            ],
            "Frontend Developer": [
                "Explain the critical rendering path in browsers and how you can optimize page load performance.",
                "What is the virtual DOM in React and how does the reconciliation algorithm work?",
                "Contrast cookie, localStorage, and sessionStorage in terms of security and storage capacity.",
                "How do CSS variables differ from preprocessor variables (like Sass), and what are the benefits?",
                "Explain event delegation in JavaScript and why it is beneficial for performance."
            ],
            "Backend Developer": [
                "Explain database normalization up to 3NF and when you would choose to denormalize.",
                "How do you handle race conditions in multi-threaded database transactions?",
                "Explain the differences between SQL and NoSQL databases, and when to use which.",
                "What is connection pooling, and why is it critical for high-throughput backends?",
                "Describe the architectural benefits and challenges of adopting microservices."
            ],
            "Python Developer": [
                "What are Python generators and decorators, and how do they work under the hood?",
                "Explain global interpreter lock (GIL) in Python and how to bypass it for parallel tasks.",
                "What is the difference between mutable and immutable types in Python? Give examples.",
                "How does Python's memory management and garbage collection work?",
                "Describe the difference between deepcopy and shallow copy in Python."
            ],
            "Data Analyst": [
                "What is the difference between an inner join, left join, and outer join in SQL?",
                "Explain the difference between descriptive, predictive, and prescriptive analytics.",
                "How do you handle missing values or outliers in a dataset before conducting analysis?",
                "What is A/B testing, and how do you calculate statistical significance?",
                "Explain the concept of overfitting in statistical models and how you can prevent it."
            ]
        }

        coding_questions = {
            "default": [
                {
                    "text": "Write a Python function `reverse_string(s: str) -> str` that takes a string and returns its reverse. Do not use slice notation (e.g., s[::-1]).",
                    "code_template": "def reverse_string(s: str) -> str:\n    # Write your code here\n    pass\n",
                    "test_cases": json.dumps([
                        {"name": "Empty String", "input": "''", "expected": "''"},
                        {"name": "Standard String", "input": "'hello'", "expected": "'olleh'"},
                        {"name": "Palindrome", "input": "'racecar'", "expected": "'racecar'"}
                    ])
                },
                {
                    "text": "Write a Python function `is_prime(n: int) -> bool` that checks if a given integer is a prime number. Return True if it is prime, and False otherwise.",
                    "code_template": "def is_prime(n: int) -> bool:\n    # Write your code here\n    pass\n",
                    "test_cases": json.dumps([
                        {"name": "Zero and One", "input": "1", "expected": "False"},
                        {"name": "Prime Number", "input": "7", "expected": "True"},
                        {"name": "Composite Number", "input": "12", "expected": "False"},
                        {"name": "Negative and Even Prime", "input": "2", "expected": "True"}
                    ])
                },
                {
                    "text": "Write a Python function `two_sum(nums: list, target: int) -> list` that returns indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
                    "code_template": "def two_sum(nums: list, target: int) -> list:\n    # Write your code here\n    pass\n",
                    "test_cases": json.dumps([
                        {"name": "Simple Case", "input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"},
                        {"name": "Unordered List", "input": "[3, 2, 4], 6", "expected": "[1, 2]"},
                        {"name": "Duplicate Values", "input": "[3, 3], 6", "expected": "[0, 1]"}
                    ])
                }
            ]
        }

        # Fallback to Software Engineer if role is not mapped
        role_tech = tech_questions.get(role_type, tech_questions["Software Engineer"])
        role_coding = coding_questions.get("default")

        questions = []
        for i in range(num_questions):
            q_num = i + 1
            # Distribute question types based on interview_type
            if interview_type == "HR":
                q_text = hr_questions[i % len(hr_questions)]
                q_type = "HR"
            elif interview_type == "Coding":
                cq = role_coding[i % len(role_coding)]
                questions.append({
                    "text": cq["text"],
                    "question_type": "Coding",
                    "difficulty": difficulty,
                    "code_template": cq["code_template"],
                    "test_cases": cq["test_cases"]
                })
                continue
            elif interview_type == "Technical":
                q_text = role_tech[i % len(role_tech)]
                q_type = "Technical"
            else: # Mixed
                if i % 3 == 0:
                    q_text = hr_questions[(i // 3) % len(hr_questions)]
                    q_type = "HR"
                elif i % 3 == 1:
                    q_text = role_tech[(i // 3) % len(role_tech)]
                    q_type = "Technical"
                else:
                    cq = role_coding[(i // 3) % len(role_coding)]
                    questions.append({
                        "text": cq["text"],
                        "question_type": "Coding",
                        "difficulty": difficulty,
                        "code_template": cq["code_template"],
                        "test_cases": cq["test_cases"]
                    })
                    continue
            
            questions.append({
                "text": f"Q{q_num}: {q_text}",
                "question_type": q_type,
                "difficulty": difficulty,
                "code_template": None,
                "test_cases": None
            })

        return questions

    @staticmethod
    def generate_questions(role_type: str, difficulty: str, interview_type: str, num_questions: int) -> List[Dict[str, Any]]:
        # Check provider
        provider = settings.AI_PROVIDER.lower()
        
        # If API keys are empty, fall back to mock
        if provider == "gemini" and not settings.GEMINI_API_KEY:
            logger.warning("Gemini provider selected but GEMINI_API_KEY is missing. Falling back to Mock.")
            provider = "mock"
        elif provider == "openai" and not settings.OPENAI_API_KEY:
            logger.warning("OpenAI provider selected but OPENAI_API_KEY is missing. Falling back to Mock.")
            provider = "mock"

        if provider == "mock":
            return AIService._get_mock_questions(role_type, difficulty, interview_type, num_questions)

        prompt = f"""
        You are an expert technical interviewer. Generate exactly {num_questions} interview questions for the role: {role_type}.
        Difficulty level: {difficulty}
        Interview type requested: {interview_type} (Must be HR, Technical, Coding, or Mixed).

        Format instructions:
        Return ONLY a JSON list of objects. Each object must have these EXACT keys:
        - "text": The interview question.
        - "question_type": "HR", "Technical", or "Coding".
        - "difficulty": "{difficulty}".
        - "code_template": string (only if type is Coding, provide a boilerplate function. Otherwise null).
        - "test_cases": string (only if type is Coding, a JSON string containing a list of test case dicts with keys "name", "input", and "expected". Otherwise null).

        Coding question guidelines:
        - Coding questions must ask the candidate to write a Python function.
        - The "code_template" should provide the starting def line and docstring, ending with "pass".
        - Provide 3-4 standard input/output test cases. Make sure "input" represents arguments in Python format (e.g. "'hello'" or "[1,2,3], 5") and "expected" matches the output.

        Do not wrap in markdown ```json blocks. Return raw JSON string only.
        """

        try:
            if provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                content = response.text.strip()
            else: # openai
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                content = response.choices[0].message.content.strip()

            # Clean markdown code blocks if the LLM outputted them anyway
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            return json.loads(content)
        except Exception as e:
            logger.error(f"Error calling {provider} API: {str(e)}. Falling back to mock questions.")
            return AIService._get_mock_questions(role_type, difficulty, interview_type, num_questions)

    @staticmethod
    def evaluate_answer(question_text: str, question_type: str, answer_text: str) -> Dict[str, Any]:
        """Evaluates candidate response and returns a structured feedback dictionary."""
        provider = settings.AI_PROVIDER.lower()
        
        if provider == "gemini" and not settings.GEMINI_API_KEY:
            provider = "mock"
        elif provider == "openai" and not settings.OPENAI_API_KEY:
            provider = "mock"

        if provider == "mock":
            # Generate simulated feedback based on answer length and simple keywords
            word_count = len(answer_text.split())
            overall = min(10.0, max(2.0, word_count / 15.0 + 3.5))
            
            # Adjust score if user left it blank or said "I don't know"
            lower_answer = answer_text.lower().strip()
            if not lower_answer or "don't know" in lower_answer or "no idea" in lower_answer or len(lower_answer) < 10:
                overall = 1.0

            comm = min(10.0, overall + 0.5)
            tech = min(10.0, overall - 0.5) if question_type != "HR" else overall
            prob = overall
            conf = min(10.0, overall + 0.2)

            weak = ["System Design"] if question_type == "Technical" else ["Public Speaking"]
            strong = ["Logical Explanation"] if question_type != "HR" else ["Empathy & Communication"]

            return {
                "overall_score": round(overall, 1),
                "communication_score": round(comm, 1),
                "technical_score": round(tech, 1),
                "problem_solving_score": round(prob, 1),
                "confidence_score": round(conf, 1),
                "grammar_feedback": "Sentence structure is correct. Minor punctuation adjustments could be made.",
                "fluency_feedback": "Speech pacing is appropriate. Ideas are clearly connected.",
                "suggestions": "Try to elaborate more on real-world examples and keep responses concise.",
                "weak_topics": weak,
                "strong_topics": strong,
                "correct_approach": "Structure your answers using the STAR method (Situation, Task, Action, Result) for behavioral questions, and explain complexities/time-complexity for technical ones.",
                "better_answer": "A more structured and comprehensive answer would detail the architectural choices, discuss edge cases, and elaborate on trade-offs. For example, explain how indexing speeds up reads but slows down write operations."
            }

        prompt = f"""
        You are an expert interviewer evaluating a candidate's answer.
        
        Question asked: "{question_text}"
        Question type: {question_type}
        Candidate's Answer: "{answer_text}"

        Analyze the answer and evaluate the candidate. Return a JSON object with these EXACT keys:
        - "overall_score": float (from 0.0 to 10.0)
        - "communication_score": float (from 0.0 to 10.0)
        - "technical_score": float (from 0.0 to 10.0)
        - "problem_solving_score": float (from 0.0 to 10.0)
        - "confidence_score": float (from 0.0 to 10.0)
        - "grammar_feedback": string (grammar critique)
        - "fluency_feedback": string (fluency critique)
        - "suggestions": string (actionable improvement tips)
        - "weak_topics": list of strings (topics they showed weak understanding of)
        - "strong_topics": list of strings (topics they showed strong understanding of)
        - "correct_approach": string (explanation of the best way to approach this question)
        - "better_answer": string (an example of a model 10/10 answer)

        Format: Return ONLY the raw JSON string. Do not wrap in markdown ```json blocks.
        """

        try:
            if provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                content = response.text.strip()
            else: # openai
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            return json.loads(content)
        except Exception as e:
            logger.error(f"Error calling {provider} for evaluation: {str(e)}")
            # Return basic mock instead of failing
            return {
                "overall_score": 5.0,
                "communication_score": 5.0,
                "technical_score": 5.0,
                "problem_solving_score": 5.0,
                "confidence_score": 5.0,
                "grammar_feedback": "Unable to connect to AI server for grammar checks.",
                "fluency_feedback": "Fluent, but mock evaluator placeholder active.",
                "suggestions": f"Review key principles. Service error detail: {str(e)[:50]}",
                "weak_topics": ["Error Handling"],
                "strong_topics": ["System Basics"],
                "correct_approach": "Review the core concepts regarding this topic.",
                "better_answer": "Refer to the textbook definition and best practices."
            }

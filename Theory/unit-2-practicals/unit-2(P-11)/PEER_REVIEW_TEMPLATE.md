# Peer Review: Assignment-I

| | |
|---|---|
| Author (peer) | |
| Reviewer (you) | |
| Repository / folder reviewed | |
| Date | |

**Honest note:** a review only counts if it is about your peer's real code. Everything below is blank for you to fill in after you read their solution with `CODE_REVIEW_CHECKLIST.md` next to it. The worked example in section 3 is there to show the level of detail expected; delete it before submitting.

## 1. Summary (2 to 3 sentences)
What does the project do, what stack is used, and what is your overall impression?

## 2. Checklist score
Copy the scoring table from `CODE_REVIEW_CHECKLIST.md` here.

| Criteria | Weight | Score |
|---|---|---|
| Database Design | 20 | |
| Code Quality | 25 | |
| API Design | 20 | |
| Security | 15 | |
| Documentation | 10 | |
| Testing | 10 | |
| **Total** | 100 | |

## 3. Areas for improvement (at least 3)
For each: where it is, why it matters, and a concrete fix.

### Improvement 1: (title)
- **Where:** `file.py`, line
- **Problem:**
- **Why it matters:**
- **Suggested fix:**
```python
# before

# after
```

### Improvement 2: (title)
- **Where:**
- **Problem:**
- **Why it matters:**
- **Suggested fix:**

### Improvement 3: (title)
- **Where:**
- **Problem:**
- **Why it matters:**
- **Suggested fix:**

---
### Worked example (delete before submitting)
### Improvement: secret key is hard-coded
- **Where:** `auth.py`, line 5: `SECRET_KEY = "mysecret"`
- **Problem:** the signing key is in the source code, so anyone who can read the repository can forge tokens for any user, including an admin.
- **Why it matters:** this is the "Hardcoded secrets" mistake from the lecture's Security table; it is also committed to git history.
- **Suggested fix:** read it from the environment and refuse to start without it in production.
```python
# before
SECRET_KEY = "mysecret"

# after (config.py)
class Settings(BaseSettings):
    SECRET_KEY: str            # no default: the app fails to start if it is missing
    model_config = SettingsConfigDict(env_file=".env")
settings = Settings()
```
Then rotate the leaked key and add `.env` to `.gitignore`.
---

## 4. Strengths
List at least two things that were done well (a good schema, clean error handling, thorough tests...).

## 5. Discussion points for the class
Questions or trade-offs worth discussing (for example: PUT vs PATCH, offset vs cursor pagination, where to put business logic).

## 6. Where to look first (common problems in Assignment-I solutions, from the lecture)
| Area | Typical mistakes to look for |
|---|---|
| Database | missing foreign keys or indexes, no `UNIQUE` email, over-normalisation |
| API | verbs in URLs, always returning 200, no pagination, inconsistent errors |
| Security | plain-text or weakly hashed passwords, tokens that never expire, no input validation, no rate limiting, secrets in code |
| Code quality | everything in one `main.py`, no type hints, magic numbers, `print` instead of logging, no tests |

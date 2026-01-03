async def generate_with_openrouter(prompt: str, max_tokens: int, temperature: float):
    # Fake response only for testing
    return """
User Story: As a registered user, I want to reset my password using email so that I can regain access to my account securely.

Acceptance Criteria:
- The user can request a password reset using a registered email address.
- A reset email is sent only if the email exists in the system.
- The reset link expires after a defined time.
- The user must enter a new password that meets security rules.
- An error message is shown for invalid or expired links.
    """.strip()

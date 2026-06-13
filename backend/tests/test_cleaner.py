from app.services.cleaner import clean_website_text

def test_cleaner_removes_short_noise_and_duplicates():
    text = """
    Menu
    Login
    Nike makes performance shoes for runners and athletes.
    Nike makes performance shoes for runners and athletes.
    Cookie preferences accept all.
    """
    cleaned = clean_website_text(text)
    assert "Menu" not in cleaned
    assert "Cookie" not in cleaned
    assert cleaned.count("performance shoes") == 1

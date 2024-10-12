def lot_of_text(page, average):
    text = page.extract_text()
    return text and len(text.strip()) >= average * 0.1
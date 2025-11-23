from tools.pdf_generator import generate_pdf

payload = {
    'session_id': 'test123',
    'rti_letter_english': 'This is a test RTI letter.',
    'pio_address': 'PIO, Municipal Corporation, TestCity'
}

pdf_meta = generate_pdf(payload)
print(pdf_meta)

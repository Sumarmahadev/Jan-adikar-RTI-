import json
from unittest.mock import patch, MagicMock
from pathlib import Path

RUNTIME = Path.cwd() / 'runtime'

@patch('agents.agent_a.genai')
def test_agent_a_parse(mock_genai):
    mock_upload = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({'raw_transcript':'...','english_transcript':'...','language':'hi','user_name':None,'city':None,'issue_summary':'Road broken','followups':[]})
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_resp
    mock_genai.upload_file.return_value = mock_upload
    mock_genai.GenerativeModel.return_value = mock_model

    from agents.agent_a import process_audio_file
    mp3 = RUNTIME / 'dummy.mp3'
    mp3.write_text('dummy')
    out = process_audio_file(str(mp3), 'testsession')
    assert 'issue_summary' in out

@patch('tools.pio_finder.GoogleSearch')
def test_pio_finder(mock_search):
    mock_search.return_value.get_dict.return_value = {'organic_results':[{'snippet':'PIO snippet','link':'https://gov.in/pio'}]}
    from tools.pio_finder import find_pio
    res = find_pio('Municipal Corporation','TestCity')
    assert 'pio_address' in res

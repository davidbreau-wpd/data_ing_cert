import pytest
import pandas as pd
import fitz
import camelot
from camelot.core import Table

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'test': [1, 2, 3],
        'other': ['a', 'b', 'c']
    })

@pytest.fixture
def empty_dataframe():
    return pd.DataFrame()

@pytest.fixture
def mock_camelot_table(mocker):
    mock_table = mocker.MagicMock(spec=camelot.core.Table)
    mock_table.flavor = 'stream'
    mock_table.df = pd.DataFrame({
        0: ['1', '2'],
        1: ['Item', 'Another item'],
        2: ['OK', 'NOK']
    })
    mock_table.pdf_size = (595, 842)  # Format A4 en points
    return mock_table

@pytest.fixture
def test_pdf_path(tmp_path):
    # Créer un dossier temporaire pour les tests
    test_dir = tmp_path / "test_pdfs"
    test_dir.mkdir()
    
    pdf_path = test_dir / "test.pdf"
    doc = fitz.open()
    
    # Page 1 - Order type
    page = doc.new_page()
    page.insert_text((50, 50), "MASTER SERVICE ORDER")
    
    # Page 2 - Details with table-like structure
    page = doc.new_page()
    # Create a more structured table that Camelot can detect
    y_start = 40
    for y in range(y_start, 731, 30):  # Fill most of the page
        page.draw_line((20, y), (600, y))  # Horizontal lines
    
    # Vertical lines for columns
    page.draw_line((20, y_start), (20, 730))
    page.draw_line((65, y_start), (65, 730))
    page.draw_line((450, y_start), (450, 730))
    page.draw_line((600, y_start), (600, 730))
    
    # Add content
    page.insert_text((25, 60), "No.")
    page.insert_text((70, 60), "Check Item")
    page.insert_text((455, 60), "Result")
    
    page.insert_text((25, 90), "1")
    page.insert_text((70, 90), "Check 1")
    page.insert_text((455, 90), "OK")
    
    page.insert_text((25, 120), "2")
    page.insert_text((70, 120), "Check 2")
    page.insert_text((455, 120), "NOK")
    
    # Page 3 - Defects summary
    page = doc.new_page()
    # Create similar structured table
    y_start = 40
    for y in range(y_start, 731, 30):
        page.draw_line((20, y), (600, y))
    
    page.draw_line((20, y_start), (20, 730))
    page.draw_line((65, y_start), (65, 730))
    page.draw_line((330, y_start), (330, 730))
    page.draw_line((600, y_start), (600, 730))
    
    # Add content
    page.insert_text((25, 60), "No.")
    page.insert_text((70, 60), "Defect")
    page.insert_text((335, 60), "Status")
    
    page.insert_text((25, 90), "1")
    page.insert_text((70, 90), "Issue 1")
    page.insert_text((335, 90), "Fixed")
    
    doc.save(str(pdf_path))
    doc.close()
    
    yield str(pdf_path)
    
    if pdf_path.exists():
        pdf_path.unlink()
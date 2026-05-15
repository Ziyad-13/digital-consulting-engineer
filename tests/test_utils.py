import os
from datetime import datetime

import pytest

import utils

def test_generate_payment_certificate(mocker, tmp_path):
    # Mocking time.time and datetime to ensure deterministic test results
    mocker.patch('utils.time.time', return_value=1234567890)
    mock_datetime = mocker.patch('utils.datetime')
    mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)

    # Mock database to prevent actual database write operations
    mock_db_save = mocker.patch('utils.db.save_payment_certificate')

    # Patch UPLOAD_ROOT so file saving happens in the temp dir instead of real filesystem
    mocker.patch('utils.UPLOAD_ROOT', str(tmp_path))

    project = {
        'id': 42,
        'name': 'Test Project',
        'budget': 100000.0
    }
    phase_number = 1
    milestone_name = 'Foundation Completed'
    percentage = 25.0

    # Execute
    cert_no, file_path, amount = utils.generate_payment_certificate(
        project=project,
        phase_number=phase_number,
        milestone_name=milestone_name,
        percentage=percentage
    )

    # Asserts
    expected_cert_no = "PC-0042-P1-1234567890"
    assert cert_no == expected_cert_no
    assert amount == 25000.0

    # Ensure upload directory was created under the mocked tmp_path root
    expected_folder = os.path.join(str(tmp_path), "project_42", "phase_1", "certificates")
    expected_file_path = os.path.join(expected_folder, f"{expected_cert_no}.txt")

    assert file_path == expected_file_path
    assert os.path.exists(file_path)

    # Verify file contents
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # English parts
    assert "PAYMENT CERTIFICATE" in content
    assert "Certificate No. : PC-0042-P1-1234567890" in content
    assert "Project         : Test Project (#42)" in content
    assert "Percentage      : 25.0%" in content
    assert "Amount (SAR)    : 25,000.00" in content

    # Arabic parts
    assert "شهادة دفع" in content
    assert "رقم الشهادة     : PC-0042-P1-1234567890" in content
    assert "المشروع         : Test Project (#42)" in content
    assert "النسبة          : 25.0٪" in content
    assert "المبلغ (ر.س)    : 25,000.00" in content

    # Database function must be called with right params
    mock_db_save.assert_called_once_with(
        42, 1, expected_cert_no, 25.0, 25000.0, expected_file_path
    )

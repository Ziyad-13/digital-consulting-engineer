import tempfile
import os
import unittest.mock

import database as db

def test_save_payment_certificate():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        with unittest.mock.patch("database.DB_PATH", db_path):
            db.init_db()

            # create a test project
            pid = db.create_project("Test Project", 1000.0)

            cert = db.PaymentCertificate(
                project_id=pid,
                phase=1,
                certificate_no="CERT-123",
                percentage=10.0,
                amount=100.0,
                file_path="/path/to/cert.txt",
            )

            db.save_payment_certificate(cert)

            certs = db.get_payment_certificates(pid)
            assert len(certs) == 1
            assert certs[0]["project_id"] == pid
            assert certs[0]["phase_number"] == 1
            assert certs[0]["certificate_no"] == "CERT-123"
            assert certs[0]["percentage"] == 10.0
            assert certs[0]["amount"] == 100.0
            assert certs[0]["file_path"] == "/path/to/cert.txt"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

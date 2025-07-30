import datetime
from dateutil.parser import isoparse
import unittest

from trivium_python_sdk.security import verify_trivium_callback_request

class TestSecurity(unittest.TestCase):
    """Security tests"""

    def test_security_single_signature(self):
        """given public key and signature encoded in Base64, timestamp and body, when verify_trivium_callback_request is called then it should return true"""

        public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqgdWNgGR+kR5sA7+oAXghDwXOPQAqo780XqRhP5R9kBid65I25pe+IIDT2bDlGs+uZtQnGdlg9GzWglpVs+gtIglalOVD96xv1cor+IWGRSRuBZolsq00LbWYuJBOJ1TW1M/u1+jNNjlML/WRvxpXbL3hMgp5Jk5FSq/Mj5BCc+I+SmPJBlIo/4+toJu4T41+Y29+h/C0L8WsUcUoP32cxQMCl/sRdFMGrRAFFIx1NtyXCmQDSUCtEwQ24o3oMnk3h0kTzmNNRPhk30Px4UaP/2NuECsuQIdC3Qm9OToHlrF2hDg073phthleZTZ/+4asb265l0cIBLv8x/AjIqU7wIDAQAB"
        # public_key = ""
        signature = "fqBLlQaFAW1kUaPGxw76YklkIKQ2QRZVUkwMxhsIvbYg3F8nb1t7O3/c23Y9P6c6RIV/iT8RcUE94E6Wz3n8clDGmCJVSICKBe+BfJajxOp/ITTgHWYGwl6aPzd2ENoqVPmVBwtTYk4qFhxCsOORMHXXWQm5z+tGl3JSAe9gpUiqIHpElDdnNSy87KSUTA+pjuoHc5XWAmOI4MADp3PAeVI0qq90sQfYaH6W6CxbJnRilFwHfAwWuCt4ctlROeJ9mYSo+49Bq4lRcJo8xv5vSyq5aejWQ2czpGq0zNrY+lwq4EbRl/zy/5V/gS4PrZCcCzeG28eCV49JYfaKwPgW7A=="
        timestamp = "2024-07-20T06:02:07.566947Z"
        raw_body = '{"userId":"84d68dda-da91-4ae6-a21a-6faee2f6c8ad"}'

        assert verify_trivium_callback_request(
            signature_from_header=signature,
            raw_webhook_request_body=raw_body,
            timestamp_from_header=timestamp,
            public_key_base64_encoded=public_key,
            now=isoparse(timestamp)
        ) == True

    def test_security_multiple_signatures(self):
        """given public key and multiple signatures encoded in Base64, timestamp and body, when verify_trivium_callback_request is called then it should return true"""

        public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqgdWNgGR+kR5sA7+oAXghDwXOPQAqo780XqRhP5R9kBid65I25pe+IIDT2bDlGs+uZtQnGdlg9GzWglpVs+gtIglalOVD96xv1cor+IWGRSRuBZolsq00LbWYuJBOJ1TW1M/u1+jNNjlML/WRvxpXbL3hMgp5Jk5FSq/Mj5BCc+I+SmPJBlIo/4+toJu4T41+Y29+h/C0L8WsUcUoP32cxQMCl/sRdFMGrRAFFIx1NtyXCmQDSUCtEwQ24o3oMnk3h0kTzmNNRPhk30Px4UaP/2NuECsuQIdC3Qm9OToHlrF2hDg073phthleZTZ/+4asb265l0cIBLv8x/AjIqU7wIDAQAB"
        signature_1 = "fqBLlQaFAW1kUaPGxw76YklkIKQ2QRZVUkwMxhsIvbYg3F8nb1t7O3/c23Y9P6c6RIV/iT8RcUE94E6Wz3n8clDGmCJVSICKBe+BfJajxOp/ITTgHWYGwl6aPzd2ENoqVPmVBwtTYk4qFhxCsOORMHXXWQm5z+tGl3JSAe9gpUiqIHpElDdnNSy87KSUTA+pjuoHc5XWAmOI4MADp3PAeVI0qq90sQfYaH6W6CxbJnRilFwHfAwWuCt4ctlROeJ9mYSo+49Bq4lRcJo8xv5vSyq5aejWQ2czpGq0zNrY+lwq4EbRl/zy/5V/gS4PrZCcCzeG28eCV49JYfaKwPgW7A=="
        signature_2 = "nt96lInRn75XamYlarwGqOGnqBAYrPzDb6pUL8bk5CMDcjDZ/guEYOQPYYSs/Ed6LRiVQCbZBUOfYQaIZEBDg1uZwWPXU3e/OtgKseEZvtzhkBTBC0z1EMTDmpDMFZkMh7guzsdrTsmcqTn+gssa3R92N/eKHpxcMawuTBVCP3X97xTXeGKdvgd1y8I6hEYwayKuf7AI+gjIZGTDIeeVD5QFRmJHL30h2o3egWZpEtHFoIgOvHvyEKwwR6zRuxOH74scBrBy2i+JaxR2ossjuISGcFQLJYEsN2quLULZZi5C5FTbZ30k1F3EbNHyDvhYsNfDKFJEz2SB7FWTBOaryw=="
        timestamp = "2024-07-20T06:03:42.420161Z"
        raw_body = '{"userId":"84d68dda-da91-4ae6-a21a-6faee2f6c8ad"}'

        assert verify_trivium_callback_request(
            signature_from_header=f"{signature_1},{signature_2}",
            raw_webhook_request_body=raw_body,
            timestamp_from_header=timestamp,
            public_key_base64_encoded=public_key,
            now=isoparse(timestamp)
        ) == True

    def test_security_expired_timestamp(self):
        """given timestamp that is too far in the past, return false"""

        public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqgdWNgGR+kR5sA7+oAXghDwXOPQAqo780XqRhP5R9kBid65I25pe+IIDT2bDlGs+uZtQnGdlg9GzWglpVs+gtIglalOVD96xv1cor+IWGRSRuBZolsq00LbWYuJBOJ1TW1M/u1+jNNjlML/WRvxpXbL3hMgp5Jk5FSq/Mj5BCc+I+SmPJBlIo/4+toJu4T41+Y29+h/C0L8WsUcUoP32cxQMCl/sRdFMGrRAFFIx1NtyXCmQDSUCtEwQ24o3oMnk3h0kTzmNNRPhk30Px4UaP/2NuECsuQIdC3Qm9OToHlrF2hDg073phthleZTZ/+4asb265l0cIBLv8x/AjIqU7wIDAQAB"
        signature = "fqBLlQaFAW1kUaPGxw76YklkIKQ2QRZVUkwMxhsIvbYg3F8nb1t7O3/c23Y9P6c6RIV/iT8RcUE94E6Wz3n8clDGmCJVSICKBe+BfJajxOp/ITTgHWYGwl6aPzd2ENoqVPmVBwtTYk4qFhxCsOORMHXXWQm5z+tGl3JSAe9gpUiqIHpElDdnNSy87KSUTA+pjuoHc5XWAmOI4MADp3PAeVI0qq90sQfYaH6W6CxbJnRilFwHfAwWuCt4ctlROeJ9mYSo+49Bq4lRcJo8xv5vSyq5aejWQ2czpGq0zNrY+lwq4EbRl/zy/5V/gS4PrZCcCzeG28eCV49JYfaKwPgW7A==";
        timestamp = "2024-07-20T06:02:07.566947Z"
        raw_body = '{"userId":"84d68dda-da91-4ae6-a21a-6faee2f6c8ad"}'
        past = isoparse(timestamp)
        now = past + datetime.timedelta(hours=1)

        assert verify_trivium_callback_request(
            signature_from_header=signature,
            raw_webhook_request_body=raw_body,
            timestamp_from_header=timestamp,
            public_key_base64_encoded=public_key,
            now=now
        ) == False

if __name__ == '__main__':
    unittest.main()
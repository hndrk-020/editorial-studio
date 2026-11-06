"""No external networking: numeric-address/TLS mocks and killable dummy workers."""
import socket
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
import image_transport as transport
import photo_researcher as importer
from engine import PublicationError


class DownloadSecurityTests(unittest.TestCase):
    def test_mixed_public_private_dns_answers_fail_closed(self):
        answers=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,443)) for ip in ('8.8.8.8','127.0.0.1')]
        with patch.object(transport.socket,'getaddrinfo',return_value=answers):
            with self.assertRaises(transport.DownloadError):transport._public_addresses('example.com')

    def test_connect_uses_validated_numeric_address_and_tls_original_hostname(self):
        raw=Mock();raw.getpeername.return_value=('8.8.8.8',443)
        context=Mock()
        with patch.object(transport.ssl,'create_default_context',return_value=context),patch.object(transport.socket,'create_connection',return_value=raw) as connect:
            connection=transport._PinnedHTTPSConnection('images.example.com','8.8.8.8',2)
            connection.connect()
            connect.assert_called_once_with(('8.8.8.8',443),2)
            context.wrap_socket.assert_called_once_with(raw,server_hostname='images.example.com')

    def test_unreachable_address_falls_back_without_new_dns_lookup(self):
        first=Mock();first.connect.side_effect=OSError('Unreachable synthetic address')
        second=Mock()
        with patch.object(transport,'_PinnedHTTPSConnection',side_effect=[first,second]) as create,patch.object(transport.socket,'getaddrinfo') as dns:
            result=transport._connect_public('images.example.com',['2606:4700:4700::1111','8.8.8.8'],time.monotonic()+18)
        self.assertIs(result,second)
        self.assertEqual([c.args[1] for c in create.call_args_list],['2606:4700:4700::1111','8.8.8.8'])
        first.close.assert_called_once();dns.assert_not_called()

    def test_redirect_to_private_address_never_connects(self):
        response=Mock(status=302);response.getheader.return_value='https://127.0.0.1/private'
        connection=Mock();connection.getresponse.return_value=response
        with patch.object(transport,'_public_addresses',return_value=['8.8.8.8']),patch.object(transport,'_PinnedHTTPSConnection',return_value=connection) as create:
            with self.assertRaises(transport.DownloadError):transport._download_image('https://example.com/photo')
            self.assertEqual(create.call_count,1)
            connection.close.assert_called_once()

    def test_oversized_response_is_rejected_before_body_read(self):
        response=Mock(status=200)
        response.getheader.side_effect=lambda name,default=None:{'Content-Type':'image/jpeg','Content-Length':str(transport.MAX_IMAGE_BYTES+1)}.get(name,default)
        connection=Mock();connection.getresponse.return_value=response
        with patch.object(transport,'_public_addresses',return_value=['8.8.8.8']),patch.object(transport,'_PinnedHTTPSConnection',return_value=connection):
            with self.assertRaises(transport.DownloadError):transport._download_image('https://example.com/photo')
        response.read1.assert_not_called()

    def test_total_deadline_terminates_blocked_worker(self):
        with tempfile.TemporaryDirectory() as temp:
            worker=Path(temp)/'dummy_worker.py'
            worker.write_text('import time\ntime.sleep(10)\n')
            start=time.monotonic()
            with patch.object(importer,'DOWNLOAD_WORKER',worker),patch.object(importer,'MAX_DOWNLOAD_SECONDS',0.2):
                with self.assertRaisesRegex(PublicationError,'timed out'):
                    importer._download_image('https://example.com/synthetic.png')
            self.assertLess(time.monotonic()-start,3)

    def test_malformed_url_rejected_before_worker_start(self):
        with patch.object(importer.subprocess,'run') as run:
            for url in ('https://example.com:bad/a','https://u:p@example.com/a','https://example.com/a\r\nInjected:yes'):
                with self.assertRaises(PublicationError):importer._download_image(url)
            run.assert_not_called()

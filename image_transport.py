"""Bounded HTTPS transport worker. No project data, model tools or image decoders."""
from ipaddress import ip_address
import socket,ssl,time,sys
from http.client import HTTPSConnection
from urllib.parse import urlparse,urljoin
MAX_IMAGE_BYTES=14_000_000
MAX_REDIRECTS=2
MAX_DOWNLOAD_SECONDS=18
class DownloadError(Exception):
    pass

def safe_photo_url(url: str, *, dns: bool = False) -> str:
    value=str(url).strip()
    if len(value)>8192 or any(ord(c)<33 or ord(c)==127 for c in value):
        raise DownloadError('Invalid photo URL')
    u=urlparse(value)
    if u.scheme != 'https' or not u.hostname or u.username or u.password:
        raise DownloadError('Photo URL must be a direct https:// image address without login details')
    if u.port not in (None,443):
        raise DownloadError('Only standard HTTPS image URLs are supported')
    host=u.hostname.lower().rstrip('.')
    if host == 'localhost' or host.endswith(('.local','.internal','.localhost')):
        raise DownloadError('Private/local network addresses are not allowed')
    try:
        ip=ip_address(host)
        if not ip.is_global:
            raise DownloadError('Local or private IP addresses are not allowed')
    except ValueError:
        pass
    if dns:
        try:
            ips={v[4][0] for v in socket.getaddrinfo(host,443,proto=socket.IPPROTO_TCP)}
        except OSError as ex:
            raise DownloadError('Could not resolve the image server hostname') from ex
        if not ips or not all(ip_address(x).is_global for x in ips):
            raise DownloadError('The image URL resolves to a private or restricted network address')
    return u.geturl()


class _PinnedHTTPSConnection(HTTPSConnection):
    """Connect only to the already validated address; retain TLS hostname checks."""
    def __init__(self, host, address, timeout):
        super().__init__(host, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            if not ip_address(raw.getpeername()[0]).is_global:
                raise DownloadError('Image connection reached a restricted address')
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def _public_addresses(host):
    try:
        addresses = list(dict.fromkeys(v[4][0] for v in socket.getaddrinfo(host,443,proto=socket.IPPROTO_TCP)))
    except OSError as ex:
        raise DownloadError('Could not resolve the image server hostname') from ex
    if not addresses or not all(ip_address(a).is_global for a in addresses):
        raise DownloadError('The image URL resolves to a private or restricted network address')
    return addresses


def _connect_public(host, addresses, deadline):
    """Try only the validated addresses, without a second hostname lookup."""
    last_error=None
    for address in addresses:
        remaining=deadline-time.monotonic()
        if remaining<=0:raise DownloadError('Photo download timed out')
        connection=_PinnedHTTPSConnection(host,address,min(5,remaining))
        try:
            connection.connect()
            return connection
        except OSError as ex:
            last_error=ex
            connection.close()
    raise DownloadError('Could not connect to the image host') from last_error


def _download_image(url: str) -> bytes:
    deadline = time.monotonic() + MAX_DOWNLOAD_SECONDS
    for _ in range(MAX_REDIRECTS+1):
        url = safe_photo_url(url)
        parsed = urlparse(url)
        host = parsed.hostname.rstrip('.')
        addresses = _public_addresses(host)
        remaining = deadline-time.monotonic()
        if remaining <= 0:raise DownloadError('Photo download timed out')
        connection = _connect_public(host,addresses,deadline)
        try:
            target = parsed.path or '/'
            if parsed.query:target += '?' + parsed.query
            connection.request('GET',target,headers={'User-Agent':'EditorialStudio/1.0','Accept':'image/jpeg,image/png,image/webp'})
            response = connection.getresponse()
            if response.status in (301,302,303,307,308):
                location=response.getheader('Location')
                if not location:raise DownloadError('Image redirect has no destination')
                url=safe_photo_url(urljoin(url,location))
                continue
            if response.status != 200:raise DownloadError(f'Photo host returned HTTP {response.status}')
            ctype=response.getheader('Content-Type','').split(';')[0].strip().lower()
            if ctype not in ('image/jpeg','image/png','image/webp','application/octet-stream'):
                raise DownloadError('URL did not return a supported image')
            try:declared=int(response.getheader('Content-Length','0'))
            except ValueError as ex:raise DownloadError('Invalid image Content-Length') from ex
            if declared<0 or declared>MAX_IMAGE_BYTES:raise DownloadError('Photo file exceeds 14 MB')
            parts=[];size=0
            while True:
                remaining=deadline-time.monotonic()
                if remaining<=0:raise DownloadError('Photo download timed out')
                if connection.sock:connection.sock.settimeout(remaining)
                chunk=response.read1(min(256_000,MAX_IMAGE_BYTES-size+1))
                if not chunk:break
                size+=len(chunk)
                if size>MAX_IMAGE_BYTES:raise DownloadError('Photo download exceeded 14 MB')
                parts.append(chunk)
            data=b''.join(parts)
            return data
        except (OSError,ValueError) as ex:
            raise DownloadError('Photo download failed; download the image manually') from ex
        finally:
            connection.close()
    raise DownloadError('Photo URL redirected too many times')



if __name__ == '__main__':
    try:
        value=sys.stdin.buffer.read(8193)
        if len(value)>8192:raise DownloadError('Photo URL is too long')
        data=_download_image(value.decode('utf-8'))
        sys.stdout.buffer.write(data)
    except Exception:
        print('The selected image could not be downloaded safely.',file=sys.stderr)
        raise SystemExit(1)

import json
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from time import time
from urllib.parse import urlsplit

from .errors import BootstrapError, UnsupportedError
from .logger import get_logger
from .overrides import iana_overrides
from .utils import (
    get_async_client,
    get_session,
    http_request,
    http_request_async,
    is_subnet_of,
)


log = get_logger('bootstrap')


class BaseBootstrap:

    # Where we get bootstrap data from
    BOOTSTRAP_URLS = {
        'asn': 'https://data.iana.org/rdap/asn.json',
        'dns': 'https://data.iana.org/rdap/dns.json',
        'ipv4': 'https://data.iana.org/rdap/ipv4.json',
        'ipv6': 'https://data.iana.org/rdap/ipv6.json',
        'object': 'https://data.iana.org/rdap/object-tags.json',
    }
    # RDAP by default must be over HTTPS, but can be toggled to allow HTTP
    SECURE_RDAP_PROTOCOLS = ('https',)
    INSECURE_RDAP_PROTOCOLS = ('http', 'https')
    # Servers to fall back to in the event of failing to resolve the correct server
    DEFAULT_RDAP_FALLBACKS = (
        'https://rdap.arin.net/registry/',
        'https://rdap.db.ripe.net/',
        'https://rdap.apnic.net/'
    )
    # Map of RIR RDAP endpoints
    RIR_RDAP_ENDPOINTS = {
        'afnic': 'https://rdap.nic.fr/',
        'afrinic': 'https://rdap.afrinic.net/rdap/',
        'arin': 'https://rdap.arin.net/registry/',
        'apnic': 'https://rdap.apnic.net/',
        'jpnic': 'https://jpnic.rdap.apnic.net/',
        'idnic': 'https://idnic.rdap.apnic.net/',
        'krnic': 'https://krnic.rdap.apnic.net/',
        'lacnic': 'https://rdap.lacnic.net/rdap/',
        'registro.br': 'https://rdap.registro.br/',
        'ripe': 'https://rdap.db.ripe.net/',
        'twnic': 'https://twnic.rdap.apnic.net/',
    }
    # Map of entity prefix and postfixes to RIRs, used to guess entity RIR
    RIR_ENTITY_PREFIXES = {
        'AFNIC': 'afnic',
        'AFRINIC': 'afrinic',
        'ARIN': 'arin',
        'AP': 'apnic',
        'JPNIC': 'jpnic',
        'KR': 'krnic',
        'ID': 'idnic',
        'LACNIC': 'lacnic',
        'BR': 'registro.br', # registro.br currently does not use entity prefixes
        'RIPE': 'ripe',
        'TW': 'twnic',
    }

    def __init__(self):
        self.bootstrap_parsers = {
            'asn': self.parse_asn_data,
            'dns': self.parse_dns_data,
            'ipv4': self.parse_ipv4_data,
            'ipv6': self.parse_ipv6_data,
            'object': self.parse_object_data,
        }
        self.rir_endpoints_by_domain = {}
        for name, url in self.RIR_RDAP_ENDPOINTS.items():
            url_parts = urlsplit(url)
            self.rir_endpoints_by_domain[url_parts.netloc] = name
        self._allow_insecure = False
        self._is_bootstrapped = False
        self._bootstrap_timestamp = 0
        self._expected_items = set(self.BOOTSTRAP_URLS.keys())
        self._data = {}
        self._parsed_data = {}
        self._use_iana_overrides = False
        self.clear_bootstrapping()

    def is_using_overrides(self):
        return self._use_iana_overrides

    def is_allowing_insecure_endpoints(self):
        return self._allow_insecure

    def is_bootstrapped(self):
        return self._is_bootstrapped

    def clear_bootstrapping(self):
        self._data = {}
        self._parsed_data = {}
        for k in self.BOOTSTRAP_URLS.keys():
            self._data[k] = {}
        self._is_bootstrapped = False
        self._use_iana_overrides = False
        log.debug('Cleared bootstrap data')

    def _bootstrap(self, overrides=False, allow_insecure=False):
        if self.is_bootstrapped():
            return True
        self._use_iana_overrides = bool(overrides)
        self._allow_insecure = bool(allow_insecure)
        items_loaded = set()
        for name, url in self.BOOTSTRAP_URLS.items():
            response = yield url
            yield
            if response.status_code != 200:
                raise BootstrapError(f'Failed to download bootstrap URL: {url}, got '
                                     f'non-200 response code: {response.status_code}')
            data = False
            try:
                data = response.json()
            except Exception as e:
                raise BootstrapError(f'Failed to parse data in URL: {url} '
                                     f'as JSON: {e}') from e
            if data:
                self._data[name] = data
                items_loaded.add(name)
        if items_loaded == self._expected_items:
            self._bootstrap_timestamp = int(time())
            self._is_bootstrapped = True
            self.parse_bootstrap_data()
            log.debug('Bootstrapped')
            return True
        else:
            items_missing = self._expected_items - items_loaded
            raise BootstrapError(f'Failed to load some bootstrap data, '
                                 f'missing data: {items_missing}')

    def save_bootstrap_data(self, as_json=True):
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        rtn = {'timestamp': self._bootstrap_timestamp}
        for name, data in self._data.items():
            rtn[name] = data
        if as_json:
            return json.dumps(rtn)
        return rtn


    def load_bootstrap_data(self, data, overrides=False, allow_insecure=False, from_json=True):
        if self.is_bootstrapped():
            raise BootstrapError('Already bootstrapped, cannot load more data')
        if not isinstance(data, str) and from_json:
            raise BootstrapError(f'Unable to load bootstrap data, data must be a '
                                 f'string, got: {type(data)}')
        elif not isinstance(data, dict) and not from_json:
            raise BootstrapError(f'Unable to load bootstrap data, data must be a '
                                 f'dict, got: {type(data)}')
        self._use_iana_overrides = bool(overrides)
        self._allow_insecure = bool(allow_insecure)
        try:
            if from_json:
                data = json.loads(data)
        except Exception as e:
            raise BootstrapError(f'Unable to load bootstrap data, failed to parse '
                                 f'as JSON: {e}') from e
        timestamp = data.get('timestamp', None)
        if not isinstance(timestamp, int):
            raise BootstrapError(f'Unable to load bootstrap data, missing or '
                                 f'invalid timestamp')
        items_loaded = set()
        for name, item in data.items():
            if name == 'timestamp':
                continue
            self._data[name] = item
            items_loaded.add(name)
        if items_loaded == self._expected_items:
            self._bootstrap_timestamp = int(timestamp)
            self._is_bootstrapped = True
            self.parse_bootstrap_data()
            return True
        else:
            self.clear_bootstrapping()
            items_missing = self._expected_items - items_loaded
            raise BootstrapError(f'Failed to load some bootstrap data, '
                                 f'missing data: {items_missing}')

    def bootstrap_is_older_than(self, days):
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        if not isinstance(days, int):
            raise BootstrapError(f'Days must be an integer, got: {type(days)}')
        day = 60 * 60 * 24
        age_in_seconds = int(time()) - self._bootstrap_timestamp
        age_in_days = age_in_seconds / day
        log.debug(f'Bootstrap data age in days: {age_in_days} > {days}')
        return age_in_days > days

    def parse_bootstrap_data(self):
        '''
            The bootstrap data itself is not organised in a way that can be quickly
            resolved. Parse each bootstrap objects data to make fast lookups possible.
        '''
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        self._parsed_data = {}
        for item, parser in self.bootstrap_parsers.items():
            log.debug(f'Parsing {item} data with parser {parser}')
            services = self._data[item].get('services', [])
            if not services:
                raise BootstrapError(f'Unable to parse "{item}" bootstrap data, '
                                     f'no "services" found')
            self._parsed_data[item] = parser(services)
        return True

    def validate_rdap_urls(self, urls):
        allowed_schemes = (self.INSECURE_RDAP_PROTOCOLS if self._allow_insecure
                           else self.SECURE_RDAP_PROTOCOLS)
        insecure_scheme = False
        validated_urls = []
        for url in urls:
            url = str(url).strip()
            url_parts = urlsplit(url)
            url_scheme = url_parts.scheme.lower()
            if url_scheme in allowed_schemes:
                validated_urls.append(url)
                insecure_scheme = url_scheme in self.INSECURE_RDAP_PROTOCOLS
        if not validated_urls:
            if insecure_scheme:
                insecure_str = (' (insecure scheme, try '
                                'whoisit.bootstrap(allow_insecure=True))')
            else:
                insecure_str = ''
            log.debug(f'No valid RDAP service URLs could be parsed '
                      f'from: {urls}{insecure_str}')
        return validated_urls

    def parse_asn_data(self, services):
        parsed = {}
        for selector, urls in services:
            validated_urls = self.validate_rdap_urls(urls)
            if not validated_urls:
                continue
            for asnrange in selector:
                parts = asnrange.split('-')
                num_parts = len(parts)
                if num_parts == 1:
                    range_start = int(parts[0])
                    range_end = int(parts[0])
                    parsed[(range_start, range_end)] = validated_urls
                elif num_parts == 2:
                    range_start = int(parts[0])
                    range_end = int(parts[1])
                    parsed[(range_start, range_end)] = validated_urls
                else:
                    raise BootstrapError(f'Invalid ASN range selector: {asnrange}')
        return parsed

    def parse_dns_data(self, services):
        parsed = {}
        for selector, urls in services:
            validated_urls = self.validate_rdap_urls(urls)
            if not validated_urls:
                continue
            for tld in selector:
                tld = tld.strip()
                parsed[tld] = validated_urls
        return parsed

    def parse_ipv4_data(self, services):
        parsed = {}
        for selector, urls in services:
            validated_urls = self.validate_rdap_urls(urls)
            if not validated_urls:
                continue
            for prefix in selector:
                network = IPv4Network(prefix, strict=True)
                parsed[network] = validated_urls
        return parsed

    def parse_ipv6_data(self, services):
        parsed = {}
        for selector, urls in services:
            validated_urls = self.validate_rdap_urls(urls)
            if not validated_urls:
                continue
            for prefix in selector:
                network = IPv6Network(prefix, strict=True)
                parsed[network] = validated_urls
        return parsed

    def parse_object_data(self, services):
        # Bootstrap entity information doesn't contain any mappings to RIR endpoints
        # so just ignore it and return an empty dict
        return {}

    def get_fallback_endpoints(self):
        return self.DEFAULT_RDAP_FALLBACKS

    def get_asn_endpoints(self, asn):
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        if not isinstance(asn, int):
            raise BootstrapError('asn must be an int')
        for (range_start, range_end), endpoints in self._parsed_data['asn'].items():
            if range_start <= asn <= range_end:
                log.debug(f'Mapped ASN "{asn}" as between "{range_start}-{range_end}" '
                          f'and to endpoints: {endpoints}')
                return endpoints, True
        log.debug(f'Failed to map ASN "{asn}" to an endpoint, using a fallback')
        return self.get_fallback_endpoints(), False

    def get_dns_endpoints(self, tld):
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        if not isinstance(tld, str):
            raise BootstrapError('tld must be an str')
        if self._use_iana_overrides:
            domain_overrides = iana_overrides.get('domain', {})
            override_endpoints = domain_overrides.get(tld, None)
            if override_endpoints:
                log.debug(f'Mapped TLD "{tld}" to override endpoints: '
                          f'{override_endpoints}')
                return override_endpoints, False
        endpoints = self._parsed_data['dns'].get(tld, None)
        if endpoints:
            log.debug(f'Mapped TLD "{tld}" to endpoints: {endpoints}')
            return endpoints, True
        # Domains have no fallback endpoints
        raise UnsupportedError(f'TLD "{tld}" has no known RDAP endpoint '
                               f'and is unsupported. It may be supported by '
                               f'overrides, try using whoisit.bootstrap(overrides=True)')

    def get_ipv4_endpoints(self, ipv4):
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        if not isinstance(ipv4, (IPv4Address, IPv4Network)):
            raise BootstrapError('ipv4 must be a IPv4Address or a IPv4Network')
        if ipv4.is_private:
            raise BootstrapError(f'IPv4Address {ipv4} is private')
        if isinstance(ipv4, IPv4Address):
            for prefix, endpoints in self._parsed_data['ipv4'].items():
                if ipv4 in prefix:
                    log.debug(f'Mapped IPv4 address "{ipv4}" as in prefix "{prefix}" '
                              f'and to endpoints: {endpoints}')
                    return endpoints, True
        else:
            for prefix, endpoints in self._parsed_data['ipv4'].items():
                if ipv4 == prefix:
                    log.debug(f'Mapped IPv4 prefix "{ipv4}" exactly to endpoints: '
                              f'{endpoints}')
                    return endpoints, True
                elif is_subnet_of(ipv4, prefix):
                    log.debug(f'Mapped IPv4 prefix "{ipv4}" as a subnet of prefix '
                              f'"{prefix}" and to endpoints: {endpoints}')
                    return endpoints, True
        return self.get_fallback_endpoints(), False
    
    def get_ipv6_endpoints(self, ipv6):
        if not self.is_bootstrapped():
            raise BootstrapError('No bootstrap data is loaded')
        if not isinstance(ipv6, (IPv6Address, IPv6Network)):
            raise BootstrapError('ipv6 must be a IPv6Address or IPv6Network')
        if ipv6.is_private:
            raise BootstrapError(f'IPv6Address {ipv6} is private')
        if isinstance(ipv6, IPv6Address):
            for prefix, endpoints in self._parsed_data['ipv6'].items():
                if ipv6 in prefix:
                    log.debug(f'Mapped IPv6 address "{ipv6}" as in prefix "{prefix}" '
                              f'and to endpoints: {endpoints}')
                    return endpoints, True
        else:
            for prefix, endpoints in self._parsed_data['ipv6'].items():
                if ipv6 == prefix:
                    log.debug(f'Mapped IPv6 prefix "{ipv6}" exactly to endpoints: '
                              f'{endpoints}')
                    return endpoints, True
                elif is_subnet_of(ipv6, prefix):
                    log.debug(f'Mapped IPv6 prefix "{ipv6}" as a subnet of prefix '
                              f'"{prefix}" and to endpoints: {endpoints}')
                    return endpoints, True
        return self.get_fallback_endpoints(), False

    def get_entity_endpoints(self, entity):
        entity = entity.strip().upper()
        # Attempt to match a prefix or postfix to an RIR, for example many entities have
        # names such as RIPE-NAME or EXAMPLE-AP, we can use these prefixes and postfixes
        # to attempt to guess the correct RIR to query
        for part, rir_name in self.RIR_ENTITY_PREFIXES.items():
            if entity.startswith(f'{part}-') or entity.endswith(f'-{part}'):
                endpoint = self.RIR_RDAP_ENDPOINTS.get(rir_name)
                endpoints = [endpoint]
                log.debug(f'Mapped entity "{entity}" to RIR "{rir_name}" and to '
                          f'endpoints: {endpoints}')
                return endpoints, True
        # No match found, as querying a random RIR RDAP endpoint for a likely unknown
        # entity is almost certainly going to fail, raise it as unsupported
        raise UnsupportedError(f'Entity "{entity}" has no detectable RDAP endpoint, '
                               f'try specifying one manually with rir=...')

    def get_rir_endpoint(self, name):
        # allow 'ripencc' as an alias
        if name == 'ripencc':
            name = 'ripe'
        try:
            return self.RIR_RDAP_ENDPOINTS[name]
        except KeyError:
            raise BootstrapError(f'Invalid RIR endpoint name: {name}, must be '
                                 f'one of: {self.get_rir_endpoint_names()}')

    def get_rir_endpoint_names(self):
        return tuple(self.RIR_RDAP_ENDPOINTS.keys())

    def get_rir_name_by_endpoint_url(self, url):
        """
            A reverse lookup that maps endpoint URLs like https://rdap.arin.net/whatever
            to a name like 'arin'.
        """
        url_parts = urlsplit(url)
        try:
            return self.rir_endpoints_by_domain[url_parts.netloc]
        except KeyError:
            raise BootstrapError(f'Unknown endpoint URL: {url}')


class Bootstrap(BaseBootstrap):

    def __init__(self, session=None, allow_insecure_ssl=False, do_super_init=True):
        if do_super_init:
            BaseBootstrap.__init__(self)
        self.session = get_session(session, allow_insecure_ssl=allow_insecure_ssl)

    def bootstrap(self, overrides=False, allow_insecure=False):
        gen = self._bootstrap(overrides, allow_insecure)
        for url in gen:
            response = http_request(self.session, url)
            gen.send(response)


class BootstrapAsync(BaseBootstrap):

    def __init__(self, client=None, allow_insecure_ssl=False, do_super_init=True):
        if do_super_init:
            BaseBootstrap.__init__(self)
        self.client = get_async_client(client, allow_insecure_ssl)

    async def bootstrap_async(self, overrides=False, allow_insecure=False):
        gen = self._bootstrap(overrides, allow_insecure)
        for url in gen:
            response = await http_request_async(self.client, url)
            gen.send(response)


class _BootstrapMainModule(Bootstrap, BootstrapAsync):

    def __init__(self) -> None:
        Bootstrap.__init__(self, do_super_init=True)
        BootstrapAsync.__init__(self, do_super_init=False)

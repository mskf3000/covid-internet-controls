#! /usr/bin/python3

import sys
import os

def fix_path():
    newpath = [os.path.join(os.path.dirname(__file__), 'lib')]
    newpath.extend(p for p in sys.path if p)
    sys.path[:] = newpath
fix_path()

import argparse
import ast
import codecs
import datetime
import collections
import configparser
import csv
import html.parser
import json
import multiprocessing
import re
import time
import urllib.parse

import Levenshtein as leven
from datasketch import MinHash, MinHashLSHEnsemble

import jslex
import csslex

#
# progress reports
#

start = None
def progress(msg):
    global start
    now = time.time()
    if start is None:
        start = now
    delta = datetime.timedelta(seconds = now - start)
    sys.stderr.write("{}: {}\n".format(delta, msg))

#
# tokenization of "uncertain" responses for classification
#

LOOKS_LIKE_A_URL = re.compile(
    r"(?i)^['\"]*(?:https?:/|//(?:[a-z0-9-]+\.)+[a-z0-9-]+)")

def _urlsplit_forced_encoding(url):
    try:
        return urllib.parse.urlsplit(url)
    except UnicodeDecodeError:
        return urllib.parse.urlsplit(url.decode("utf-8", "surrogateescape"))

_enap_re = re.compile(br'[\x00-\x20\x7F-\xFF]|'
                      br'%(?!(?:[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}))')
def _encode_nonascii_and_percents(segment):
    segment = segment.encode("utf-8", "surrogateescape")
    return _enap_re.sub(
        lambda m: "%{:02X}".format(ord(m.group(0))).encode("ascii"),
        segment).decode("ascii")

def canon_url_syntax(url):
    """Syntactically canonicalize a URL.  This makes the following
       transformations:
         - scheme and hostname are lowercased
         - hostname is punycoded if necessary
         - vacuous user, password, and port fields are stripped
         - ports redundant to the scheme are also stripped
         - path becomes '/' if empty
         - paths like '//', '///', etc are collapsed to '/'
         - characters outside the printable ASCII range in path,
           query, fragment, user, and password are %-encoded, as are
           improperly used % signs
       The return value is a urllib.parse.SplitResult object.
    """

    exploded = _urlsplit_forced_encoding(url)
    if not exploded.hostname:
        # Remove extra slashes after the scheme and retry.
        corrected = re.sub(r'(?i)^([a-z]+):///+', r'\1://', url)
        exploded = _urlsplit_forced_encoding(corrected)

    scheme = exploded.scheme or ''
    host   = exploded.hostname or ''
    user   = _encode_nonascii_and_percents(exploded.username or "")
    passwd = _encode_nonascii_and_percents(exploded.password or "")
    port   = exploded.port
    path   = _encode_nonascii_and_percents(exploded.path)
    query  = _encode_nonascii_and_percents(exploded.query)
    frag   = _encode_nonascii_and_percents(exploded.fragment)

    # note: this is true for the empty string
    if all(c == "/" for c in path):
        path = "/"

    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        pass

    if port is None:
        port = ""
    elif ((port == 80  and scheme == "http") or
          (port == 443 and scheme == "https")):
        port = ""
    else:
        port = ":{}".format(port)

    # We don't have to worry about ':' or '@' in the user and password
    # strings, because urllib.parse does not do %-decoding on them.
    if user == "" and passwd == "":
        auth = ""
    elif passwd == "":
        auth = "{}@".format(user)
    else:
        auth = "{}:{}@".format(user, passwd)
    netloc = auth + host + port

    return urllib.parse.SplitResult(scheme, netloc, path, query, frag)

def url_tokens(url):
    """Tokenize a URL for classification."""
    split = canon_url_syntax(url.strip("\'\""))
    if split.scheme:   yield split.scheme
    if split.hostname: yield split.hostname
    if split.username: yield split.username
    if split.password: yield split.password
    if split.port:     yield str(split.port)
    if split.path:     yield split.path
    if split.query:
        for q in split.query.split("&"):
            for r in q.split("="):
                for s in r.split(";"):
                    yield s
    if split.fragment:
        yield split.fragment

DISCARD_VALUE_HEADERS = frozenset((
    "content-length",
    "eagleeye-traceid",
    "fastly-debug-digest",
    "request-id",
    "x-amz-id-2",
    "x-amz-request-id",
    "x-cache-hits",
    "x-server-id",
    "x-timer"
))

DISCARD_VALUE_ATTRS = frozenset((
    "data-adblockkey",
))
CONTENT_ATTRS = frozenset((
    "href", "src", "alt", "title", "summary",
))
SCRIPT_ATTRS = frozenset((
    "onabort", "onautocomplete", "onautocompleteerror", "onblur", "oncancel",
    "oncanplay", "oncanplaythrough", "onchange", "onclick", "onclose",
    "oncontextmenu", "oncuechange", "ondblclick", "ondrag", "ondragend",
    "ondragenter", "ondragexit", "ondragleave", "ondragover", "ondragstart",
    "ondrop", "ondurationchange", "onemptied", "onended", "onerror",
    "onfocus", "oninput", "oninvalid", "onkeydown", "onkeypress", "onkeyup",
    "onload", "onloadeddata", "onloadedmetadata", "onloadstart",
    "onmousedown", "onmouseenter", "onmouseleave", "onmousemove",
    "onmouseout", "onmouseover", "onmouseup", "onmousewheel", "onpause",
    "onplay", "onplaying", "onprogress", "onratechange", "onreset",
    "onresize", "onscroll", "onseeked", "onseeking", "onselect", "onshow",
    "onsort", "onstalled", "onsubmit", "onsuspend", "ontimeupdate",
    "ontoggle", "onvolumechange", "onwaiting",
))
META_DISCARD_CONTENT_NAMES = frozenset((
))
META_CONTENT_CONTENT_NAMES = frozenset((
    "author", "creator", "publisher", "description", "keywords",
))

class LossyHTMLTokenizer(html.parser.HTMLParser):

    def __init__(self):
        super().__init__()
        self._jslexer = jslex.JsLexer()

    def reset(self):
        super().reset()
        self._structure = []
        self._content = []
        self._partial_script = None
        self._partial_style = None

    def close(self):
        super().close()
        return (self._structure, self._content)

    def process_script(self, script):
        self._jslexer.reset()
        for ty, val in self._jslexer.lex(script):
            if ty == 'string':
                try:
                    val = ast.literal_eval(val)
                except SyntaxError:
                    pass
                if LOOKS_LIKE_A_URL.match(val):
                    self._content.extend(url_tokens(val))
                else:
                    self._structure.append(val)

    def process_style(self, style):
        for ty, val in csslex.tokenize(style):
            if ty == 'url':
                self._content.extend(url_tokens(val))
            else:
                self._structure.append(val)

    def _process_attr(self, name, value):
        self._structure.append(name)
        if not value: return
        if name == "style":
            self.process_style(value)
        elif name in SCRIPT_ATTRS:
            self.process_script(value)
        elif name in DISCARD_VALUE_ATTRS:
            return
        else:
            is_content = name in CONTENT_ATTRS
            tokens = value.split()
            for tok in tokens:
                if LOOKS_LIKE_A_URL.match(tok):
                    self._content.extend(url_tokens(value))
                elif is_content:
                    self._content.append(tok)
                else:
                    self._structure.append(tok)

    def handle_starttag(self, tag, attrs):
        self._structure.append("<" + tag)
        if tag == "meta":
            mname  = None
            mvalue = None
            for name, value in attrs:
                if name == "content":
                    mvalue = value
                elif name in ("http-equiv", "name"):
                    self._structure.append(name)
                    mname = value.lower()
                else:
                    self._process_attr(name, value)

            if mname and mvalue:
                self._structure.append(mname)
                if mname == "refresh":
                    tu = mvalue.split(";url=", 1)
                    if len(tu) > 0 and tu[0]:
                        time = tu[0].strip()
                        if time:
                            self._structure.append(time)
                    if len(tu) > 1 and tu[1]:
                        url = tu[1].strip()
                        if url:
                            self._content.extend(url_tokens(url))
                elif mname == "viewport":
                    self._structure.extend(x.strip() for x in mvalue.split(","))
                elif mname in META_CONTENT_CONTENT_NAMES:
                    self._content.extend(mvalue.split())
                else:
                    self._structure.extend(mvalue.split())

        else:
            if tag == "script":
                self._partial_script = " "

            elif tag == "style":
                self._partial_style = " "

            for name, value in attrs:
                self._process_attr(name, value)

    def handle_endtag(self, tag):
        if tag == "script":
            self.process_script(self._partial_script)
            self._partial_script = None
        elif tag == "style":
            self.process_style(self._partial_style)
            self._partial_style = None
        self._structure.append(tag + ">")

    def handle_data(self, data):
        if self._partial_script:
            self._partial_script += data
        elif self._partial_style:
            self._partial_style += data
        else:
            for tok in data.split():
                if LOOKS_LIKE_A_URL.match(tok):
                    self._content.extend(url_tokens(tok))
                else:
                    self._content.append(tok)

def tokenize_html(body):
    tk = LossyHTMLTokenizer()
    tk.feed(body)
    return tk.close()

def tokenize_script(body):
    tk = LossyHTMLTokenizer()
    tk.process_script(body)
    return tk.close()

def tokenize_style(body):
    tk = LossyHTMLTokenizer()
    tk.process_style(body)
    return tk.close()

def tokenize_plain(body):
    return [], body.split()

def tokenize_other(body):
    return [], []

TokenizedPayload = collections.namedtuple("TokenizedPayload", (
    "flags", "status", "reason", "http_ver",
    "structure", "structure_t", "content", "content_t"))

def tokenize_payload(flags, payload):
    sp = payload.split("\n\n", 1)
    if len(sp) == 2:
        headers, body = sp
        headers = headers.splitlines()
        # ["HTTP/1.1", "200", "Document follows"]
        vsr = headers[0].split(None, 2)
        ver = vsr[0]
        status = vsr[1] if len(vsr) > 1 else '0'
        reason = vsr[2] if len(vsr) > 2 else ''
    else:
        headers = []
        body = payload
        ver = ''
        status = '0'
        reason = ''

    structure_tokens = [flags, ver, status, reason]
    content_tokens = []
    tokenize_typed_body = None
    for h in headers[1:]:
        kv = h.split(":", 1)
        name = kv[0].strip().lower()
        structure_tokens.append(name)
        if name not in DISCARD_VALUE_HEADERS:
            value = kv[1].strip() if len(kv) > 1 else ''
            for tk in value.split():
                if LOOKS_LIKE_A_URL.match(tk):
                    ut = list(url_tokens(tk))
                    content_tokens.extend(ut)
                else:
                    structure_tokens.append(tk)
            if name == 'content-type' and tokenize_typed_body is None:
                if value.startswith('text/html'):
                    tokenize_typed_body = tokenize_html
                elif '/javascript' in value or '/x-javascript' in value:
                    tokenize_typed_body = tokenize_script
                elif value.startswith('text/css'):
                    tokenize_typed_body = tokenize_style
                elif value.startswith('text/'):
                    tokenize_typed_body = tokenize_plain
                else:
                    tokenize_typed_body = tokenize_other

    if tokenize_typed_body is None:
        tokenize_typed_body = tokenize_html

    body_structure, body_content = tokenize_typed_body(body)
    structure_tokens.extend(body_structure)
    content_tokens.extend(body_content)

    return TokenizedPayload(
        flags, int(status), reason, ver,
        ' '.join(structure_tokens), structure_tokens,
        ' '.join(content_tokens), content_tokens)

#
# Clustering of token sequences
#

ObsvLocation = collections.namedtuple("ObsvLocation", (
    "url", "country", "timestamp", "as_owner", "vpn_provider"))

class SuspiciousPayloadClusters:
    def __init__(self, mcp):
        self.tok_payloads   = {}
        self.hashes         = {}
        self.locations      = collections.defaultdict(list)
        self.mcp            = mcp
        self.m_content      = collections.defaultdict(set)
        self.m_content_t    = set()
        self.m_structure    = collections.defaultdict(set)
        self.m_structure_t  = set()
        self.discarded      = set()

    def read_observations(self, ifp):
        rd = csv.DictReader(ifp)
        count = 0
        for row in rd:
            if row == rd._fieldnames:
                continue

            count += 1
            if count % 100000 == 0:
                progress(str(count))

            location = ObsvLocation(
                canon_url_syntax(row["url"]).geturl(),
                row["country"], row["timestamp"],
                row["as.owner"], row["vpn"])

            flags = row["flags"]
            pld = row["payload"]
            key = flags + "|" + pld

            if key in self.tok_payloads:
                tp = self.tok_payloads[key]
            else:
                self.tok_payloads[key] = tp = tokenize_payload(flags, pld)

            if key in self.discarded:
                continue

            discard, m_content, m_structure = self.mcp.match(tp, location)
            if discard:
                self.discarded.add(key)
                continue

            self.locations[tp.structure].append(location)
            self.locations[tp.content].append(location)

            if m_content:
                self.m_content_t.add(tp.content)
                for m in m_content:
                    self.m_content[m].add(tp.content)

            elif tp.content not in self.hashes:
                ch = MinHash(num_perm=128)
                for ct in tp.content_t:
                    ch.update(ct.encode('utf-8'))
                self.hashes[tp.content] = (ch, len(tp.content_t))

            if m_structure:
                self.m_structure_t.add(tp.structure)
                for m in m_structure:
                    self.m_structure[m].add(tp.structure)
            elif tp.structure not in self.hashes:
                sh = MinHash(num_perm=128)
                for st in tp.structure_t:
                    sh.update(st.encode('utf-8'))
                self.hashes[tp.structure] = (sh, len(tp.structure_t))

        progress(str(count))

    def expand_pc_to_oc(self, clusters):
        # Expand a group of payload clusters to a group of
        # observation+location clusters.
        ocs = []
        for clust in clusters:
            variations = []
            locations = []
            pages = set()
            countries = set()

            for tokens in clust:
                loc = self.locations[tokens]

                variations.append((len(loc), tokens))
                locations.extend(loc)
                for l in loc:
                    pages.add(l.url)
                    countries.add(l.country)

            variations.sort(key = lambda c: -c[0])
            ocs.append({
                "countries": sorted(countries),
                "pages": sorted(pages),
                "score": len(pages)/len(countries),
                "var": variations,
                "loc": locations,
            })
        ocs.sort(
            key=lambda c:
            (-c["score"], -len(c["countries"]), -len(c["pages"])))
        return ocs

    def expand_manual_to_oc(self, clusters):
        # Expand a group of manual payload clusters, ditto.
        ocs = []
        for tag, clust in clusters.items():
            variations = []
            locations = []
            pages = set()
            countries = set()

            for tokens in clust:
                loc = self.locations[tokens]
                variations.append((len(loc), tokens))
                locations.extend(loc)
                for l in loc:
                    pages.add(l.url)
                    countries.add(l.country)

            variations.sort(key = lambda c: -c[0])
            ocs.append({
                "tag": tag,
                "countries": sorted(countries),
                "pages": sorted(pages),
                "score": len(pages)/len(countries),
                "var": variations,
                "loc": locations,
            })
        ocs.sort(
            key=lambda c:
            (-c["score"], -len(c["countries"]), -len(c["pages"])))
        return ocs

    def cluster_obs_group(self, candidates):
        ensemble = MinHashLSHEnsemble(threshold=0.95, num_perm=128)
        ensemble.index((c,) + self.hashes[c]
                       for c in candidates
                       if self.hashes[c][1] > 0)

        clusters = []
        while candidates:
            rep = candidates.pop()
            clus = [rep]
            h, l = self.hashes[rep]
            if l == 0:
                # An empty representative will cause division by
                # zero in ensemble.query(); instead, group it with
                # all the other empty candidates, and no others.
                for other in list(candidates):
                    if self.hashes[other][1] == 0:
                        clus.append(other)
                        candidates.discard(other)
            else:
                for other in ensemble.query(h, l):
                    if other in candidates:
                        clus.append(other)
                        candidates.discard(other)
            clusters.append(clus)
        return clusters

    def cluster_observations(self):
        # Split the observations by HTTP response code: 200, 3xx, and
        # everything else.  Cluster each both by content and by
        # structure.
        groups = { k: set() for k in [
            '200_c', '3xx_c', '145_c',  '200_s', '3xx_s', '145_s'
        ]}

        for key, tp in self.tok_payloads.items():
            if key in self.discarded:
                continue

            if tp.status == 200:
                grp = '200'
            elif 300 <= tp.status < 399:
                grp = '3xx'
            else:
                grp = '145'

            if tp.content not in self.m_content_t:
                groups[grp + '_c'].add(tp.content)
            if tp.structure not in self.m_structure_t:
                groups[grp + '_s'].add(tp.structure)

        progress("expanding automatic groups")
        clusters = {
            tag: self.expand_pc_to_oc(self.cluster_obs_group(grp))
            for tag, grp in groups.items()
        }
        progress("expanding manual groups")
        clusters["manual_c"] = self.expand_manual_to_oc(self.m_content)
        clusters["manual_s"] = self.expand_manual_to_oc(self.m_structure)
        return clusters

ManualClusterPattern = collections.namedtuple(
    "ManualClusterPattern",
    ("name", "pattern", "match", "discard", "only_for_urls"))

class ManualClusterPatterns:
    def __init__(self, cfg):
        parser = configparser.RawConfigParser()
        with open(cfg, "rt") as fp:
            parser.read_file(fp)

        patterns = []
        for name, data in parser.items():
            if name == "DEFAULT": continue
            pat = re.compile(" ".join(data["pattern"].split()).lower(),
                             re.IGNORECASE)

            match = data["match"]
            if match != "content" and match != "structure":
                raise RuntimeError("don't know what to do with " + name)

            discard = data.get("discard", "false") == "true"
            only = data.get("only_for_urls")
            if only is not None:
                only = re.compile(" ".join(only.split()).lower(),
                                  re.IGNORECASE)

            patterns.append(ManualClusterPattern(
                name, pat, match, discard, only))

        self.patterns = patterns

    def match(self, tp, location):
        content_matches = set()
        structure_matches = set()
        discard = False
        for pat in self.patterns:
            only = pat.only_for_urls
            if only is not None and not only.match(location.url):
                continue
            if pat.match == "content":
                target = tp.content
                group = content_matches
            else:
                target = tp.structure
                group = structure_matches
            if pat.pattern.search(target):
                if pat.discard:
                    discard = True
                    break
                else:
                    group.add(pat.name)
        return discard, content_matches, structure_matches

def main():
    progress("loading cluster patterns")
    mcp = ManualClusterPatterns("spc_patterns.cf")
    spc = SuspiciousPayloadClusters(mcp)
    progress("reading observations")
    with sys.stdin as ifp:
        spc.read_observations(ifp)
    progress("clustering observations")
    clusters = spc.cluster_observations()
    progress("writing out clusters")
    with sys.stdout as ofp:
        json.dump(clusters, ofp, indent=2, ensure_ascii=False)
    progress("done.")

main()

#! /usr/bin/python3

import argparse
import collections
import configparser
import contextlib
import csv
import datetime
import os
import random
import re
import sys
import zlib

import psycopg2
from psycopg2.extras import DictCursor

#
# Interpretation of raw packets on the wire.
#
# We look for complete HTTP responses in a single packet; this is a
# trigger heuristic, based on the observation that censorship by TCP
# payload injection needs to do that or it won't work reliably.
#
# For ease of further processing, we also decode transfer and text
# encoding at this stage.  The logic for doing this vaguely mimics
# What Browsers Do as described in the WHATWG's various standards,
# notably <https://encoding.spec.whatwg.org/>,
# <https://mimesniff.spec.whatwg.org/>, and
# <https://html.spec.whatwg.org/multipage/parsing.html>.
#
# Some attention has also been paid to RFC 7230 (the current rev of
# the HTTP/1.1 spec), but observed server behavior deviates from this
# spec substantially.  In particular, many of the regexes below
# anticipate sloppy generation of HTTP response headers.
#
# HTTP/2 (as she is spoke) is always transmitted under TLS encryption,
# which means the censor cannot forge it (unless they have subverted a
# CA, which we look for separately), so we do not need to worry about
# it.
#

# Table of encoding labels supported by Web browsers; unfortunately
# this is not the same as the table of encoding labels recognized by
# Python.  The values on the RHS have been adjusted to the Pythonic
# canonical encoding names, which don't always agree either, and the
# encodings mapped to 'replacement' and 'x-user-defined' have been
# dropped (see below).
ENCODING_LABELS = {
    'big5'                : 'big5',
    'big5-hkscs'          : 'big5',
    'cn-big5'             : 'big5',
    'csbig5'              : 'big5',
    'x-x-big5'            : 'big5',
    'cp1250'              : 'cp1250',
    'windows-1250'        : 'cp1250',
    'x-cp1250'            : 'cp1250',
    'cp1251'              : 'cp1251',
    'windows-1251'        : 'cp1251',
    'x-cp1251'            : 'cp1251',
    'ansi_x3.4-1968'      : 'cp1252',
    'ascii'               : 'cp1252',
    'cp1252'              : 'cp1252',
    'cp819'               : 'cp1252',
    'csisolatin1'         : 'cp1252',
    'ibm819'              : 'cp1252',
    'iso_8859-1:1987'     : 'cp1252',
    'iso_8859-1'          : 'cp1252',
    'iso-8859-1'          : 'cp1252',
    'iso8859-1'           : 'cp1252',
    'iso88591'            : 'cp1252',
    'iso-ir-100'          : 'cp1252',
    'l1'                  : 'cp1252',
    'latin1'              : 'cp1252',
    'us-ascii'            : 'cp1252',
    'windows-1252'        : 'cp1252',
    'x-cp1252'            : 'cp1252',
    'cp1253'              : 'cp1253',
    'windows-1253'        : 'cp1253',
    'x-cp1253'            : 'cp1253',
    'cp1254'              : 'cp1254',
    'csisolatin5'         : 'cp1254',
    'iso_8859-9:1989'     : 'cp1254',
    'iso_8859-9'          : 'cp1254',
    'iso-8859-9'          : 'cp1254',
    'iso8859-9'           : 'cp1254',
    'iso88599'            : 'cp1254',
    'iso-ir-148'          : 'cp1254',
    'l5'                  : 'cp1254',
    'latin5'              : 'cp1254',
    'windows-1254'        : 'cp1254',
    'x-cp1254'            : 'cp1254',
    'cp1255'              : 'cp1255',
    'windows-1255'        : 'cp1255',
    'x-cp1255'            : 'cp1255',
    'cp1256'              : 'cp1256',
    'windows-1256'        : 'cp1256',
    'x-cp1256'            : 'cp1256',
    'cp1257'              : 'cp1257',
    'windows-1257'        : 'cp1257',
    'x-cp1257'            : 'cp1257',
    'cp1258'              : 'cp1258',
    'windows-1258'        : 'cp1258',
    'x-cp1258'            : 'cp1258',
    '866'                 : 'cp866',
    'cp866'               : 'cp866',
    'csibm866'            : 'cp866',
    'ibm866'              : 'cp866',
    'dos-874'             : 'cp874',
    'iso-8859-11'         : 'cp874',
    'iso8859-11'          : 'cp874',
    'iso885911'           : 'cp874',
    'tis-620'             : 'cp874',
    'windows-874'         : 'cp874',
    'cseucpkdfmtjapanese' : 'euc_jp',
    'euc-jp'              : 'euc_jp',
    'x-euc-jp'            : 'euc_jp',
    'cseuckr'             : 'euc_kr',
    'csksc56011987'       : 'euc_kr',
    'euc-kr'              : 'euc_kr',
    'iso-ir-149'          : 'euc_kr',
    'korean'              : 'euc_kr',
    'ks_c_5601-1987'      : 'euc_kr',
    'ks_c_5601-1989'      : 'euc_kr',
    'ksc_5601'            : 'euc_kr',
    'ksc5601'             : 'euc_kr',
    'windows-949'         : 'euc_kr',
    'gb18030'             : 'gb18030',
    'chinese'             : 'gbk',
    'csgb2312'            : 'gbk',
    'csiso58gb231280'     : 'gbk',
    'gb_2312-80'          : 'gbk',
    'gb_2312'             : 'gbk',
    'gb2312'              : 'gbk',
    'gbk'                 : 'gbk',
    'iso-ir-58'           : 'gbk',
    'x-gbk'               : 'gbk',
    'csiso2022jp'         : 'iso2022_jp',
    'iso-2022-jp'         : 'iso2022_jp',
    'csisolatin6'         : 'iso8859_10',
    'iso-8859-10'         : 'iso8859_10',
    'iso8859-10'          : 'iso8859_10',
    'iso885910'           : 'iso8859_10',
    'iso-ir-157'          : 'iso8859_10',
    'l6'                  : 'iso8859_10',
    'latin6'              : 'iso8859_10',
    'iso-8859-13'         : 'iso8859_13',
    'iso8859-13'          : 'iso8859_13',
    'iso885913'           : 'iso8859_13',
    'iso-8859-14'         : 'iso8859_14',
    'iso8859-14'          : 'iso8859_14',
    'iso885914'           : 'iso8859_14',
    'csisolatin9'         : 'iso8859_15',
    'iso_8859-15'         : 'iso8859_15',
    'iso-8859-15'         : 'iso8859_15',
    'iso8859-15'          : 'iso8859_15',
    'iso885915'           : 'iso8859_15',
    'l9'                  : 'iso8859_15',
    'iso-8859-16'         : 'iso8859_16',
    'csisolatin2'         : 'iso8859_2',
    'iso_8859-2:1987'     : 'iso8859_2',
    'iso_8859-2'          : 'iso8859_2',
    'iso-8859-2'          : 'iso8859_2',
    'iso8859-2'           : 'iso8859_2',
    'iso88592'            : 'iso8859_2',
    'iso-ir-101'          : 'iso8859_2',
    'l2'                  : 'iso8859_2',
    'latin2'              : 'iso8859_2',
    'csisolatin3'         : 'iso8859_3',
    'iso_8859-3:1988'     : 'iso8859_3',
    'iso_8859-3'          : 'iso8859_3',
    'iso-8859-3'          : 'iso8859_3',
    'iso8859-3'           : 'iso8859_3',
    'iso88593'            : 'iso8859_3',
    'iso-ir-109'          : 'iso8859_3',
    'l3'                  : 'iso8859_3',
    'latin3'              : 'iso8859_3',
    'csisolatin4'         : 'iso8859_4',
    'iso_8859-4:1988'     : 'iso8859_4',
    'iso_8859-4'          : 'iso8859_4',
    'iso-8859-4'          : 'iso8859_4',
    'iso8859-4'           : 'iso8859_4',
    'iso88594'            : 'iso8859_4',
    'iso-ir-110'          : 'iso8859_4',
    'l4'                  : 'iso8859_4',
    'latin4'              : 'iso8859_4',
    'csisolatincyrillic'  : 'iso8859_5',
    'cyrillic'            : 'iso8859_5',
    'iso_8859-5:1988'     : 'iso8859_5',
    'iso_8859-5'          : 'iso8859_5',
    'iso-8859-5'          : 'iso8859_5',
    'iso8859-5'           : 'iso8859_5',
    'iso88595'            : 'iso8859_5',
    'iso-ir-144'          : 'iso8859_5',
    'arabic'              : 'iso8859_6',
    'asmo-708'            : 'iso8859_6',
    'csiso88596e'         : 'iso8859_6',
    'csiso88596i'         : 'iso8859_6',
    'csisolatinarabic'    : 'iso8859_6',
    'ecma-114'            : 'iso8859_6',
    'iso_8859-6:1987'     : 'iso8859_6',
    'iso-8859-6-e'        : 'iso8859_6',
    'iso-8859-6-i'        : 'iso8859_6',
    'iso_8859-6'          : 'iso8859_6',
    'iso-8859-6'          : 'iso8859_6',
    'iso8859-6'           : 'iso8859_6',
    'iso88596'            : 'iso8859_6',
    'iso-ir-127'          : 'iso8859_6',
    'csisolatingreek'     : 'iso8859_7',
    'ecma-118'            : 'iso8859_7',
    'elot_928'            : 'iso8859_7',
    'greek8'              : 'iso8859_7',
    'greek'               : 'iso8859_7',
    'iso_8859-7:1987'     : 'iso8859_7',
    'iso_8859-7'          : 'iso8859_7',
    'iso-8859-7'          : 'iso8859_7',
    'iso8859-7'           : 'iso8859_7',
    'iso88597'            : 'iso8859_7',
    'iso-ir-126'          : 'iso8859_7',
    'sun_eu_greek'        : 'iso8859_7',
    'csiso88598e'         : 'iso8859_8',
    'csisolatinhebrew'    : 'iso8859_8',
    'hebrew'              : 'iso8859_8',
    'iso_8859-8:1988'     : 'iso8859_8',
    'iso-8859-8-e'        : 'iso8859_8',
    'iso_8859-8'          : 'iso8859_8',
    'iso-8859-8'          : 'iso8859_8',
    'iso8859-8'           : 'iso8859_8',
    'iso88598'            : 'iso8859_8',
    'iso-ir-138'          : 'iso8859_8',
    'visual'              : 'iso8859_8', # Dropped the distinction between -8
    'csiso88598i'         : 'iso8859_8', # and -8i because this does not
    'iso-8859-8-i'        : 'iso8859_8', # affect the actual encoding, only
    'logical'             : 'iso8859_8', # the text layout direction.
    'cskoi8r'             : 'koi8_r',
    'koi8'                : 'koi8_r',
    'koi8_r'              : 'koi8_r',
    'koi8-r'              : 'koi8_r',
    'koi'                 : 'koi8_r',
    'koi8-ru'             : 'koi8_u',
    'koi8-u'              : 'koi8_u',
    'csmacintosh'         : 'macintosh',
    'macintosh'           : 'macintosh',
    'mac'                 : 'macintosh',
    'x-mac-roman'         : 'macintosh',
    'x-mac-cyrillic'      : 'mac_cyrillic',
    'x-mac-ukrainian'     : 'mac_cyrillic',
    'csshiftjis'          : 'shift_jis',
    'ms932'               : 'shift_jis',
    'ms_kanji'            : 'shift_jis',
    'shift_jis'           : 'shift_jis',
    'shift-jis'           : 'shift_jis',
    'sjis'                : 'shift_jis',
    'windows-31j'         : 'shift_jis',
    'x-sjis'              : 'shift_jis',
    'utf-16be'            : 'utf_16_be',
    'utf-16le'            : 'utf_16_le',
    'utf-16'              : 'utf_16_le',
    'unicode-1-1-utf-8'   : 'utf_8',
    'utf-8'               : 'utf_8',
    'utf8'                : 'utf_8',
}

NONWHITE_CONTROL_RE = re.compile(
    "[\u0000-\u0008\u000B\u000E-\u001F\u007F-\u009F]")
def try_decode(text, encoding):
    # We may have a truncated string, so if the problem we
    # encounter is "unexpected end of data", chop off characters
    # until it stops happening.
    trail = b""
    result = ""
    while text:
        try:
            result = text.decode(encoding)
            break
        except UnicodeDecodeError as e:
            if e.reason != "unexpected end of data":
                raise
            trail = text[-1:] + trail
            text = text[:-1]
    result = result + trail.decode("ascii", "backslashreplace")
    if not result:
        return result
    if result[0] == '\uFEFF':
        result = result[1:]

    return NONWHITE_CONTROL_RE.sub(
        lambda m: "\\x{:02x}".format(ord(m.group(0))),
        result.strip().replace("\r\n", "\n"))

CONTENT_TYPE_CHARSET_RE = re.compile(r"""(?imx)
    \bcharset[ \t\n\r\f]*=[ \t\n\r\f]*
    ( [^;]*
    | " [^"\\]* (?:\\.[^"\\]*)* "
    | ' [^'\\]* (?:\\.[^'\\]*)* '
    )""")

META_CHARSET_RE = re.compile(br"""(?ix)
    <meta\b[^>]*?\bcharset[ \t\n\r\f]*=[ \t\n\r\f]*
    ( [^;]*
    | " [^"\\]* (?:\\.[^"\\]*)* "
    | ' [^'\\]* (?:\\.[^'\\]*)* '
    )""")

def decode_body_text(body, headers):
    # This is _not_ the algorithm specified in the HTML standard for
    # character set sniffing; oddly enough, that algorithm is too
    # picky in certain respects.  (It's a long story.)

    # Try UTF first.  If the first few bytes of the body
    # smell like UTF-16, use that, otherwise UTF-8.
    encoding = 'utf-8'
    if len(body) >= 2:
        if body[0] == 0xFE and body[1] == 0xFF:
            encoding = 'utf_16_be'
        elif body[0] == 0xFF and body[1] == 0xFE:
            encoding = 'utf_16_le'
    if len(body) >= 4:
        if (body[0] == 0 and body[1] > 0 and
            body[2] == 0 and body[3] > 0):
            encoding = 'utf_16_be'
        elif (body[0] > 0 and body[1] == 0 and
              body[2] > 0 and body[3] == 0):
            encoding = 'utf_16_le'

    try:
        return try_decode(body, encoding)
    except UnicodeDecodeError:
        pass

    if 'content-type' in headers:
        content_type, _, ct_params  = headers['content-type'][0].partition(";")

        # Don't try any harder to decode things that are declared as
        # not text.
        if not (content_type.startswith("text/")
                or content_type in ("application/javascript",
                                    "application/x-javascript")):
            return body.decode("ascii", "backslashreplace")

        # If there is a character encoding declared in the content-type
        # header, try using that.
        m = CONTENT_TYPE_CHARSET_RE.search(ct_params)
        if m:
            try:
                return try_decode(
                    body, encoding_labels[m.group(1).strip().lower()])
            except Exception:
                pass

    # Failing that, look for any form of <meta charset=...> tag.
    try:
        m = meta_charset_re.match(body)
        if m:
            return try_decode(
                body, encoding_labels[m.group(1).strip().lower()])
    except Exception:
        pass

    return body.decode("ascii", "backslashreplace")

#
# HTTP header preprocessing
#


# Most HTTP response headers' values are, in principle, a list of strings
# separated by commas, which is equivalent to sending the header multiple
# times with different values. Commas can be quoted by putting them inside
# double-quoted strings.
#
# The first two branches of this regex cannot match an empty string.
# The third branch matches only empty strings, but only at the very
# beginning of the text or immediately after a comma, and only when
# the other two branches couldn't.  This means that "Foo: ,a,,b,"
# becomes ['', 'a', '', 'b', ''] and "Foo: a,b" becomes ['a', 'b'].
VALUE_SEGMENT_RE = re.compile(r"""
    [^,"]+ (?: " [^"\\]* (?: \\. [^"\\]* )* " [^,"]* )* |
    [^,"]* (?: " [^"\\]* (?: \\. [^"\\]* )* " [^,"]* )+ |
    (?:\A | (?<=,) )
""", re.VERBOSE)
def split_value(value):
    return [v.strip() for v in VALUE_SEGMENT_RE.findall(value)]

# Some HTTP headers' values are not interesting and will only add
# undesirable noise to the clustering process.  Others need specific
# parts of their values masked.  And others simply should not go
# through the above comma-splitting process.
#
# Note: all value-masking functions must return a list.
def mask_entire(value):
    return ["xx"] if value else [""]
def mask_cookie(value):
    masked = []
    for token in value.split(";"):
        k, e, v = token.partition("=")
        k = k.strip().lower()
        if e and v:
            if k in ("domain", "path"):
                v = v.strip()
            else:
                v = "xx"
        masked.append(k + e + v)
    return [" ".join(masked)]

VALUE_MASKS = {
    "set-cookie":    mask_cookie,
    "cf-ray":        mask_entire,
    "date":          mask_entire,
    "etag":          mask_entire,
    "expires":       mask_entire,
    "last-modified": mask_entire,
    "rlogid":        mask_entire,
    "x-adblock-key": mask_entire,
    "x-cache":       mask_entire,
    "x-request-id":  mask_entire,
    "x-varnish":     mask_entire,
}
def mask_field_value(name, value):
    return VALUE_MASKS.get(name, split_value)(value)

def decode_field_value(value):
    """Officially (RFC 7230 §3.2.4, last paragraph) field values are
       "historically allowed" to be ISO-8859-1, but SHOULD be
       restricted to US-ASCII, with RFC 2047 coding if necessary to go
       beyond that.  In practice, people just shove UTF-8 and/or
       Windows-1252 in there without any preamble, and I've never seen
       RFC 2047 coding.
    """
    try:
        return value.decode("utf_8")
    except UnicodeDecodeError:
        pass
    try:
        return value.decode("cp1252")
    except UnicodeDecodeError:
        pass
    return value.decode("ascii", "backslashreplace")

# Values can be "folded" over multiple physical text lines a la RFC
# 822, although this feature is deprecated.
UNFOLD_VALUE_RE = re.compile(br"\r?\n[ \t]+")

def munge_http_header(name, value):
    name = name.lower().decode("ascii")
    return (name,
            mask_field_value(name, decode_field_value(
                UNFOLD_VALUE_RE.sub(b" ", value))))

HEADER_LINE_RE = re.compile(
    br"""
        ([-!#$%&'*+.^_`|~0-9a-z]+) [ \t]* : [ \t]*
        ( [^\r\n]+ (?: \r? \n [ \t]+ [^\r\n]+ )* ) \r? \n
    """,
    re.ASCII | re.IGNORECASE | re.VERBOSE)

def parse_http_header(packet, headers):
    m = HEADER_LINE_RE.match(packet)
    if not m:
        raise ValueError("couldn't parse a header line")
    name, value = munge_http_header(*m.groups())
    headers[name].extend(value)
    return packet[m.end():]


#
# HTTP response body preprocessing
#

CHUNK_PREFIX_RE = re.compile(br"\r?\n?([0-9a-fA-F]+)[ \t]*(?:;[^\r\n]*)?\r?\n")
def decode_chunked(body, headers):
    decoded = b""
    while body:
        m = CHUNK_PREFIX_RE.match(body)
        if not m:
            raise ValueError("syntax error in chunk prefix - " +
                             repr(body[:16]))
        cstart = m.end()
        clen = int(m.group(1), 16)
        if clen == 0:
            body = body[cstart:]
            break
        cend = cstart + clen
        if len(body) < cend:
            raise ValueError("chunk truncated")
        decoded += body[cstart:cend]
        body = body[cend:]

    # trailers
    while body and body != b'\r\n' and body != b'\n':
        body = parse_http_header(body, headers)

    return decoded

def decode_compress(body, headers):
    raise ValueError("(Content|Transfer)-Encoding: compress not implemented")

def decode_deflate(body, headers):
    # The magic number 47 means to accept any size of history buffer and
    # either "zlib" or "gzip" headers and trailers.
    return zlib.decompress(body, 47)

def decode_brotli(body, headers):
    raise ValueError("(Content|Transfer)-Encoding: brotli not implemented")

DECODE_TE = {
    "br":       decode_brotli,
    "compress": decode_compress,
    "deflate":  decode_deflate,
    "gzip":     decode_deflate,
    "x-gzip":   decode_deflate,
    "chunked":  decode_chunked,
    "identity": (lambda x: x)
}
def decode_response_body(body, headers):
    if not body:
        return ""

    if 'transfer-encoding' in headers:
        for enc in reversed(headers['transfer-encoding']):
            body = DECODE_TE[enc](body, headers)

    elif 'content-length' in headers:
        if len(body) < int(headers['content-length'][0], 10):
            raise ValueError("truncated response body")

    if 'content-encoding' in headers:
        for enc in reversed(headers['content-encoding']):
            body = DECODE_TE[enc](body, headers)

    return decode_body_text(body, headers)

ParsedHTTPResponse = collections.namedtuple("ParsedHTTPResponse", (
    "version", "status", "reason", "headers", "body"))

STATUS_LINE_RE = re.compile(
    br"(http/[0-9].[0-9])[ \t]+([0-9]{3,})[ \t]*([^\r\n]*?)[ \t]*\r?\n",
    re.ASCII | re.IGNORECASE)

def parse_http_response(packet):
    # RFC 7230 section 3:
    # http-response =
    #    HTTP-version SP status-code SP reason-phrase CRLF
    #    *( field-name ":" OWS field-value OWS CRLF )
    #    CRLF
    #    [ message-body ]
    m = STATUS_LINE_RE.match(packet)
    if not m:
        raise ValueError("couldn't parse a status line")

    version, status, reason = m.groups()
    version = version.decode("ascii")
    status = int(status, 10)
    reason = decode_field_value(reason)
    packet = packet[m.end():]

    headers = collections.defaultdict(list)
    while packet:
        if packet[:2] == b'\r\n':
            packet = packet[2:]
            break
        if packet[:1] == b'\n':
            packet = packet[1:]
            break
        packet = parse_http_header(packet, headers)

    return ParsedHTTPResponse(version, status, reason,
                              headers,
                              decode_response_body(packet, headers))

def serialize_http_response(pr):
    text = "{} {} {}\n".format(pr.version, pr.status, pr.reason)
    for name, values in pr.headers.items():
        text += "{}: {}\n".format(name, ", ".join(values))
    text += "\n"
    text += pr.body
    return text

ESCAPED_OCTET_RE = re.compile(r"\\(\\|[xX][0-9a-fA-F]{2})")
def recover_raw_packet(payload):
    r"""The "payload" field of an anomaly record is a text string, but it
       _represents_ the actual TCP payload, which is properly a byte
       string; recover the original.

       Octets with values 32 through 126 inclusive were serialized as
       ASCII characters, and other octets were serialized as \xXX.
       Unfortunately, \ was _not_ serialized as \\ (but, fortunately,
       it almost never shows up in the data); this is a bug in bro and
       we pretend it actually did the right thing.

       Python's "iso_8859_1" encoding maps U+0000 through U+00FF
       directly to byte values 0x00 through 0xFF.  This is a slight
       deviation from the actual ISO 8859.1 standard, which leaves a
       few byte values unassigned, but it's exactly what we want.
    """
    def decode_octet(m):
        c = m.group(1)
        if c == '\\': return '\\'
        else: return chr(int(c[1:], 16))

    return ESCAPED_OCTET_RE.sub(decode_octet, payload).encode('iso_8859_1')

#
# Database interaction
#

PacketRec = collections.namedtuple("PacketRec", (
    "seq", "ipid", "ttl", "flags", "dl", "payload"))
AnomalyEntry = collections.namedtuple("AnomalyEntry", (
    "timestamp", "vpn", "country", "as_owner", "url", "packets"))


def read_entries_for_query(db, query, limit, rejects):
    entries = []
    cid = None
    ce  = None
    cp  = None
    n   = 0

    with db, db.cursor("export_entries_" + str(os.getpid())) as cur:
        cur.execute(query)
        for row in cur:
            try:
                payload = parse_http_response(
                    recover_raw_packet(row["payload"]))
            except Exception as e:
                if (rejects is not None and
                    (not isinstance(e, ValueError) or
                     e.args[0] != "couldn't parse a status line" or
                     row["payload"][:4] == "HTTP")):
                    rejects[type(e).__name__ + ': ' + str(e)].append(
                        row["payload"])
                continue

            if row["id"] == cid:
                cp.append(PacketRec(row["seq"], row["ipid"], row["ttl"],
                                    row["flags"], row["dl"], payload))
            else:
                if cid is not None:
                    if limit is None or len(entries) < limit:
                        entries.append(ce)
                    else:
                        m = random.randrange(n)
                        if m < limit:
                            entries[m] = ce
                    n += 1

                cid = row["id"]
                cp  = [PacketRec(row["seq"], row["ipid"], row["ttl"],
                                 row["flags"], row["dl"], payload)]
                ce = AnomalyEntry(row["time_stamp"], row["vpn_provider"],
                                  row["country"], row["as_owner"],
                                  row["url"], cp)

        if cid is not None:
            if limit is None or len(entries) < limit:
                entries.append(ce)
            else:
                m = random.randrange(n)
                if m < limit:
                    entries[m] = ce

        return entries

def postprocess_entries(entries):
    entries.sort(key=lambda e: (e.url, e.country, e.timestamp))
    for e in entries:
        e.packets.sort(key=lambda p: p.seq)

    rows = [["url", "country", "timestamp", "vpn", "as.owner",
             "seq", "ipid", "ttl", "flags", "payload"]]
    for e in entries:
        for p in e.packets:
            rows.append([
                e.url, e.country, e.timestamp, e.vpn, e.as_owner,
                p.seq, p.ipid, p.ttl, p.flags,
                serialize_http_response(p.payload)
            ])
    return rows

def export_entries(db, args, rejects):
    query = """
        SELECT a.id, a.time_stamp, a.vpn_provider, a.country, a.as_owner,
               a.url, p.*
          FROM packet_anomalies a,
               jsonb_to_recordset(a.packets) AS p(
                   seq BIGINT, ipid TEXT, ttl TEXT,
                   flags TEXT, dl TEXT, payload TEXT,
                   payload_collision BOOLEAN,
                   ttl_anomaly BOOLEAN)
         WHERE (a.payload_collision OR a.ttl_anomaly)
           AND p.dl <> '0'
           AND (p.payload_collision OR p.ttl_anomaly)
    """
    if args.from_date is not None:
        query += " AND time_stamp >= '{}'".format(args.from_date.isoformat())
    if args.to_date is not None:
        query += " AND time_stamp < '{}'".format(args.to_date.isoformat())
    query += " ORDER BY a.id, p.seq";

    entries = read_entries_for_query(db, query, args.limit, rejects)
    rows = postprocess_entries(entries)
    if args.output is None:
        outf = sys.stdout
    else:
        outf = open(args.output, "wt")
    with outf:
        wr = csv.writer(outf, dialect='unix', quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            wr.writerow(row)


def open_database(conn_config_f, cursor_factory=None):
    with open(conn_config_f, "rt") as fp:
        parser = configparser.RawConfigParser()
        parser.read_file(fp)
        return contextlib.closing(psycopg2.connect(
            dsn=None,
            connection_factory=None,
            cursor_factory=cursor_factory,
            async=False,
            **parser['conn']))

def dump_rejects(rejects, reject_f):
    rejects = sorted(rejects.items(),
                     key = lambda kv: (len(kv[1]), kv[0]))
    with open(reject_f, "wt") as fp:
        for why, examples in rejects:
            fp.write("{}:\n".format(why))
            for ex in examples:
                fp.write("\t{}\n".format(ex))
            fp.write("\n")

def main():
    def posint(s):
        s = int(s)
        if s <= 0: raise ValueError("argument must be a positive integer")
        return s

    def date(s, _date_re=re.compile(r"^([0-9]{4,})-([0-9]{2})-([0-9]{2})$")):
        m = _date_re.match(s)
        if not m: raise ValueError("argument must be a date in YYYY-MM-DD form")
        return datetime.date(year=int(m.group(1)),
                             month=int(m.group(2)),
                             day=int(m.group(3)))

    ap = argparse.ArgumentParser()
    ap.add_argument("database",
                    help="File specifying how to connect to the database")
    ap.add_argument("-o", "--output",
                    help="Output file (default: stdout)")
    ap.add_argument("-l", "--limit", type=posint, default=None,
                    help="Maximum number of entries to export. "
                    "If this is fewer than the number of entries there are, "
                    "a uniformly random subsample will be taken.")
    ap.add_argument("-f", "--from-date", type=date,
                    help="Process entries on or after this date (YYYY-MM-DD)")
    ap.add_argument("-t", "--to-date", type=date,
                    help="Process entries up to but not this date (YYYY-MM-DD)")
    ap.add_argument("-r", "--rejects",
                    help="File to dump rejected payloads into")
    ap.add_argument("--test", metavar="STRING",
                    help="Test payload extractor on STRING")
    ap.add_argument("--decode", metavar="STRING",
                    help="Test packet decoder on STRING")

    args = ap.parse_args()
    if args.test:
        print(serialize_http_response(
            parse_http_response(
                recover_raw_packet(args.test))))
    elif args.decode:
        print(recover_raw_packet(args.decode)
              .decode("ascii", "backslashreplace"))
    else:
        rejects = collections.defaultdict(list) if args.rejects else None

        with open_database(args.database, cursor_factory=DictCursor) as db:
            export_entries(db, args, rejects)

        if rejects:
            dump_rejects(rejects, args.rejects)

main()

"""Text XML, Android binary XML and AAPT2 protobuf XmlNode decoding."""

from __future__ import annotations

import struct
import xml.etree.ElementTree as ET


class SafeBuilder(ET.TreeBuilder):
    def doctype(self, name, pubid, system):
        raise ValueError("XML document types are unsupported")


def plain(data: bytes):
    return ET.fromstring(data, parser=ET.XMLParser(target=SafeBuilder()))


def varint(buf: bytes, i: int) -> tuple[int, int]:
    n = 0
    for shift in range(0, 70, 7):
        if i >= len(buf):
            break
        b = buf[i]
        i += 1
        n |= (b & 127) << shift
        if not b & 128:
            return n, i
    raise ValueError("Invalid protobuf integer")


def fields(buf: bytes):
    i = 0
    while i < len(buf):
        tag, i = varint(buf, i)
        key, wire = tag >> 3, tag & 7
        if key == 0 or wire not in (0, 1, 2, 5):
            raise ValueError("Invalid protobuf tag")
        if wire == 0:
            value, i = varint(buf, i)
        else:
            if wire == 2:
                length, i = varint(buf, i)
            else:
                length = 8 if wire == 1 else 4
            if length > len(buf) - i:
                raise ValueError("Truncated protobuf field")
            value = buf[i : i + length]
            i += length
        yield key, value


def string(value) -> str:
    if not isinstance(value, bytes):
        raise TypeError("Expected a protobuf string")
    return value.decode("utf-8")


def expanded(uri: str, name: str) -> str:
    return f"{{{uri}}}{name}" if uri else name


def compiled(data: bytes) -> str:
    for kind, obj in fields(data):
        if kind not in (1, 2, 3, 7):
            continue
        props = dict(fields(obj))
        if kind == 1:
            prefix = "?" if props.get(1) == 1 else "@"
            if 3 in props:
                return prefix + string(props[3])
            if 2 in props:
                return prefix + format(props[2], "08X")
        if kind in (2, 3):
            return string(props.get(1, b""))
        if kind == 7:
            for t, n in props.items():
                if t == 8:
                    return "true" if n else "false"
                if t in (6, 7):
                    n &= 0xFFFFFFFF
                    return str(n - 2**32 if n >= 2**31 else n)
                if t in (9, 10, 11, 12):
                    return f"#{n:08x}"
                if t == 3:
                    return str(struct.unpack("<f", n)[0])
                if t in (13, 14):
                    mantissa = n >> 8
                    if mantissa & 0x800000:
                        mantissa -= 1 << 24
                    amount = mantissa / (1, 128, 32768, 8388608)[(n >> 4) & 3]
                    units = (
                        ("px", "dp", "sp", "pt", "in", "mm") if t == 13 else ("%", "%p")
                    )
                    if (n & 15) < len(units):
                        return f"{amount * (100 if t == 14 else 1):g}{units[n & 15]}"
    return "[unresolved compiled attribute]"


def proto(data: bytes, depth: int = 0):
    if depth >= 128:
        raise ValueError("XML depth limit reached")
    node = dict(fields(data))
    if 1 not in node:
        if 2 in node:
            return string(node[2])
        raise ValueError("Missing protobuf XML node")
    tag, uri, attributes, children = "", "", {}, []
    for key, value in fields(node[1]):
        if key == 2:
            uri = string(value)
        elif key == 3:
            tag = string(value)
        elif key == 4:
            a = dict(fields(value))
            attr = expanded(string(a.get(1, b"")), string(a[2]))
            attributes[attr] = (
                string(a[3]) if a.get(3) else compiled(a[6]) if 6 in a else ""
            )
        elif key == 5:
            children.append(proto(value, depth + 1))
    if not tag:
        raise ValueError("Missing protobuf XML element name")
    root = ET.Element(expanded(uri, tag), attributes)
    for child in children:
        if isinstance(child, str):
            if len(root):
                root[-1].tail = (root[-1].tail or "") + child
            else:
                root.text = (root.text or "") + child
        else:
            root.append(child)
    return root


def parse(data: bytes, bundle: bool):
    if data.startswith(b"\x03\x00\x08\x00"):
        from androguard.core.axml import AXMLPrinter
        from loguru import logger

        logger.disable("androguard")
        obj = AXMLPrinter(data)
        if not obj.is_valid() or obj.get_xml_obj() is None:
            raise ValueError("Invalid or noncanonical binary XML")
        return obj.get_xml_obj(), (
            "android-binary-xml with decoder warnings"
            if obj.is_packed()
            else "android-binary-xml"
        )
    if bundle and data[:1] == b"\x0a" and not data.lstrip().startswith(b"<"):
        root = proto(data)
        if isinstance(root, str):
            raise ValueError("Missing document element")
        return root, "aapt2-protobuf-xml"
    return plain(data), "text-xml"

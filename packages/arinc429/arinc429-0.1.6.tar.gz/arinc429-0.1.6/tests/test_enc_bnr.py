from arinc429 import Encoder
import pytest

def test_enc_bnr_zero():
    a429 = Encoder()
    a429.encode(encoding="BNR")
    assert(a429.bword== b"\x80\x00\x00\x00")

def test_enc_brn_std():
    a429 = Encoder()
    det={
            "label":0o205,
            "value":100,
            "ssm": 0x03,
            "sdi":0,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert(a429.bword== b"\xe0\x01\x90\xa1")
    assert(a429.word== 0xe00190a1)

def test_enc_brn_ssm1():
    a429 = Encoder()
    det={
            "label":0o206,
            "value":105,
            "ssm": 0x01,
            "sdi":0,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert(a429.bword== b"\xa0\x01\xa4\x61")
    assert(a429.word== 0xa001a461)

def test_enc_brn_msb_lsb():
    a429 = Encoder()
    det={
            "label":0o321,
            "value":50,
            "ssm": 0x03,
            "sdi":0,
            "msb": 25,
            "lsb": 15,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert(a429.bword== b"\x60\x0c\x80\x8b")
    assert(a429.word== 0x600c808b)

def test_enc_brn_msb_lsb2():
    a429 = Encoder()
    det={
            "label":0o333,
            "value":127.7,
            "ssm": 0x03,
            "sdi":0,
            "msb": 23,
            "lsb": 16,
            "scale":1,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert(a429.bword== b"\x60\x3F\x80\xdb")
    assert(a429.word== 0x603f80db)
def test_enc_bnr_mult():
    a429 = Encoder()
    det={
            "label":0o333,
            "value":127.7,
            "ssm": 0x03,
            "sdi":0,
            "msb": 26,
            "lsb": 19,
            "scale":1,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert a429.word== 0x61FC00DB
    assert a429.bword== b"\x61\xFC\x00\xdb"
    a429.add_bnr(
            value=127.7,
            msb =18,
            lsb = 11,
            scale = 1,
            offset= 0)
    assert a429.bword== b"\xE1\xFD\xFC\xDB"
    assert a429.word== 0xE1FDFCDB

def test_enc_slice():
    a429 = Encoder()
    det={
            "label":0o333,
            "value":127.7,
            "ssm": 0x03,
            "sdi":0,
            "msb": 26,
            "lsb": 19,
            "scale":1,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert a429.word== 0x61FC00DB
    assert a429.bword== b"\x61\xFC\x00\xdb"
    a429.add_bnr(
            value=127.7,
            msb =18,
            lsb = 11,
            scale = 1,
            offset= 0)
    assert a429[0].word== 0x61FC00DB
    assert a429[1].word== 0xE1FDFCDB
    assert a429[-1].word== 0xE1FDFCDB


def test_enc_brn_msb_not_enough_bits():
    a429 = Encoder()
    det={
            "label":0o333,
            "value":127.7,
            "ssm": 0x03,
            "sdi":0,
            "msb": 21,
            "lsb": 16,
            "encoding":"BNR"
            }
    with pytest.raises(ValueError):
        a429.encode(**det)
# TODO: Implement test_enc_bnr_msb_lsb_more_info_no_sdi
# Note: this encodes soemthing like longitude  by using the SDI for the extra precision
@pytest.mark.skip(reason="Not implemented")
def test_enc_bnr_msb_lsb_more_info_no_sdi():
    a429 = Encoder()
    det={
            "label":0o110,
            "value":42.2431231,
            "ssm": 0x03,
            "sdi":0,
            "msb": 29,
            "lsb": 9,
            "scale":1,
            "offset":0,
            "encoding":"BNR"
            }
    a429.encode(**det)
    assert(a429.bword== b"\x60\x3F\x80\xdb")
    assert(a429.word== 0x603f80db)



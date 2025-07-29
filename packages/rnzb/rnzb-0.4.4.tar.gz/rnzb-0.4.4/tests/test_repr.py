from pathlib import Path

from rnzb import Nzb

NZB_DIR = Path(__file__).parent.resolve() / "nzbs"


def test_repr() -> None:
    nzb = Nzb.from_file(NZB_DIR / "spec_example.nzb")
    assert (
        repr(nzb.meta)
        == str(nzb.meta)
        == 'Meta(title="Your File!", passwords=("secret",), tags=("HD",), category="TV")'
    )
    assert repr(nzb.meta.passwords) == str(nzb.meta.passwords) == "('secret',)"
    assert repr(nzb.meta.tags) == str(nzb.meta.tags) == "('HD',)"
    assert (
        repr(nzb.file.segments[0])
        == str(nzb.file.segments[0])
        == 'Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com")'
    )
    assert (
        repr(nzb.file.segments)
        == str(nzb.file.segments)
        == '(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com"))'
    )
    assert (
        repr(nzb.file)
        == str(nzb.file)
        == 'File(poster="Joe Bloggs <bloggs@nowhere.example>", posted_at="2003-12-17T15:28:02+00:00", subject="Here\'s your file!  abc-mr2a.r01 (1/2)", groups=("alt.binaries.mojo", "alt.binaries.newzbin"), segments=(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com")))'
    )
    assert (
        repr(nzb.files)
        == str(nzb.files)
        == '(File(poster="Joe Bloggs <bloggs@nowhere.example>", posted_at="2003-12-17T15:28:02+00:00", subject="Here\'s your file!  abc-mr2a.r01 (1/2)", groups=("alt.binaries.mojo", "alt.binaries.newzbin"), segments=(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com"))),)'
    )
    assert (
        repr(nzb)
        == str(nzb)
        == 'Nzb(meta=Meta(title="Your File!", passwords=("secret",), tags=("HD",), category="TV"), files=(File(poster="Joe Bloggs <bloggs@nowhere.example>", posted_at="2003-12-17T15:28:02+00:00", subject="Here\'s your file!  abc-mr2a.r01 (1/2)", groups=("alt.binaries.mojo", "alt.binaries.newzbin"), segments=(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com"))),))'
    )


def test_repr_2() -> None:
    nzb = Nzb.from_file(NZB_DIR / "spec_example_with_multiple_meta.nzb")
    assert (
        repr(nzb.meta)
        == str(nzb.meta)
        == 'Meta(title="Your File!", passwords=(), tags=("HD", "1080p", "FLAC"), category="TV")'
    )
    assert repr(nzb.meta.passwords) == str(nzb.meta.passwords) == "()"
    assert repr(nzb.meta.tags) == str(nzb.meta.tags) == "('HD', '1080p', 'FLAC')"
    assert (
        repr(nzb.file.segments[0])
        == str(nzb.file.segments[0])
        == 'Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com")'
    )
    assert (
        repr(nzb.file.segments)
        == str(nzb.file.segments)
        == '(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com"))'
    )
    assert (
        repr(nzb.file)
        == str(nzb.file)
        == 'File(poster="Joe Bloggs <bloggs@nowhere.example>", posted_at="2003-12-17T15:28:02+00:00", subject="Here\'s your file!  abc-mr2a.r01 (1/2)", groups=("alt.binaries.mojo", "alt.binaries.newzbin"), segments=(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com")))'
    )
    assert (
        repr(nzb.files)
        == str(nzb.files)
        == '(File(poster="Joe Bloggs <bloggs@nowhere.example>", posted_at="2003-12-17T15:28:02+00:00", subject="Here\'s your file!  abc-mr2a.r01 (1/2)", groups=("alt.binaries.mojo", "alt.binaries.newzbin"), segments=(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com"))),)'
    )
    assert (
        repr(nzb)
        == str(nzb)
        == 'Nzb(meta=Meta(title="Your File!", passwords=(), tags=("HD", "1080p", "FLAC"), category="TV"), files=(File(poster="Joe Bloggs <bloggs@nowhere.example>", posted_at="2003-12-17T15:28:02+00:00", subject="Here\'s your file!  abc-mr2a.r01 (1/2)", groups=("alt.binaries.mojo", "alt.binaries.newzbin"), segments=(Segment(size=102394, number=1, message_id="123456789abcdef@news.newzbin.com"), Segment(size=4501, number=2, message_id="987654321fedbca@news.newzbin.com"))),))'
    )

import defusedxml.ElementTree

from django_wikipedia_connector.models.page import Page

FAKE_XML = """
<page>
  <title>Some amazing title</title>
  <ns>0</ns>
  <id>20</id>
  <revision>
    <id>10999565</id>
    <parentid>10999561</parentid>
    <timestamp>2025-03-03T11:56:13Z</timestamp>
    <contributor>
      <ip>1.2.3.4</ip>
    </contributor>
    <origin>10999565</origin>
    <model>wikitext</model>
    <format>text/x-wiki</format>
    <text bytes="18736" sha1="k3roap9er1p2k21ulgirz15i3yt14dv" xml:space="preserve">Ah, my amazing text!

[[Κατηγορία:Amazing texts!]]</text>
      <sha1>k3roap9er1p2k21ulgirz15i3yt14dv</sha1>
    </revision>
  </page>
"""


def test_page():
    parsed = defusedxml.ElementTree.fromstring(FAKE_XML)
    page = Page(parsed)
    assert page.title == "Some amazing title"
    assert page.id == "20"
    assert page.text == "Ah, my amazing text!\n\n[[Κατηγορία:Amazing texts!]]"
    assert not page.is_category
    assert str(page) == "Some amazing title"

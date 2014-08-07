import markdown, unittest

class MarkdownTest(unittest.TestCase):

    def setUp(self):

        self.wiki_index = """

An h1 header
============

Paragraphs are separated by a blank line.

2nd paragraph. *Italic*, **bold**, and `monospace`. Itemized lists
look like:

  * this one
  * that one
  * the other one

           Makerspace Wiki Index
           =================

            Markdown *bold* --italic--

[[Index]]
[[AnotherPage]]

            """


    def test_index(self):
        print markdown.markdown(self.wiki_index)

    def test_index2(self):

        md = markdown.Markdown(extensions=['wikilinks(base_url=/wiki/,html_class=myclass)'])
        print md.convert(self.wiki_index)


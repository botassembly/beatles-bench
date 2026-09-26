# Context from a Wikipedia article

The worked examples hand Jev one catalog entry as context. This page hands it a whole Wikipedia article instead. Three answers Jev missed from memory turn right once the song's own article goes in as the text. The ThinkThen talk shows these three on its slide "Context fixes the answer."

No Wikipedia text is stored in this repository (`data/SOURCES.md`). This page keeps each answer's labels and probabilities and nothing else. The runs used `--no-cache` and kept no recording, so no test replays them.

## The three articles

Each article is read at the revision the bench pins in `data/pins/pages.tsv`:

| Song | Revision | Page |
| --- | --- | --- |
| Octopus's Garden | 1372890980 | https://en.wikipedia.org/w/index.php?oldid=1372890980 |
| She Loves You | 1363639274 | https://en.wikipedia.org/w/index.php?oldid=1363639274 |
| A Day in the Life | 1370458648 | https://en.wikipedia.org/w/index.php?oldid=1370458648 |

## The fetch rule

The text is the article's prose paragraphs from the MediaWiki parse API. The rule keeps the text of each `<p>` element and drops `<sup>` and `<style>` elements, so reference marks such as "[1]" go. It squeezes each run of spaces to one space, drops empty paragraphs, and joins the paragraphs with a blank line. Infoboxes, tables, lists, headings, and captions are left out.

```sh
curl -s 'https://en.wikipedia.org/w/api.php?action=parse&oldid=1372890980&prop=text&format=json' | python3 prose.py > octopus.txt
```

`prose.py`:

```python
import json
import sys
from html.parser import HTMLParser


class Prose(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paragraphs, self.current, self.skip = [], None, 0

    def handle_starttag(self, tag, attrs):
        if tag == "p" and self.current is None:
            self.current = []
        elif self.current is not None and tag in ("sup", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if self.current is not None and tag in ("sup", "style") and self.skip:
            self.skip -= 1
        elif tag == "p" and self.current is not None:
            text = " ".join("".join(self.current).split())
            if text:
                self.paragraphs.append(text)
            self.current = None

    def handle_data(self, data):
        if self.current is not None and not self.skip:
            self.current.append(data)


page = json.load(sys.stdin)["parse"]["text"]
prose = Prose()
prose.feed(page["*"] if isinstance(page, dict) else page)
sys.stdout.write("\n\n".join(prose.paragraphs))
```

The prose runs 3,844 characters for Octopus's Garden, 24,012 for She Loves You, and 28,346 for A Day in the Life.

## The commands

Run these commands from the top folder. Each article goes out as one record, and `--field /text` sends only its prose. The questions open "The text is a Wikipedia article about a song by the Beatles." `article-card.json` is `functions/annotate/annotate-context-card.json` with that opening in place of the catalog one.

```sh
Q='The text is a Wikipedia article about a song by the Beatles.'
sed "s/The text gives a catalog entry and then names a song by the Beatles./$Q/" functions/annotate/annotate-context-card.json > article-card.json

jq -Rsc "{title: \"Octopus's Garden\", text: .}" octopus.txt |
  thinkthen annotate article-card.json --jsonl --field /text --details --no-cache
jq -Rsc '{title: "She Loves You", text: .}' she-loves-you.txt |
  thinkthen choose "$Q Who sings the lead vocal on it?" John Paul George Ringo 'John and Paul duet' --jsonl --field /text --details --no-cache
jq -Rsc '{title: "A Day in the Life", text: .}' a-day-in-the-life.txt |
  thinkthen decide "$Q It appears on the album Abbey Road." --jsonl --field /text --details --no-cache
```

## The answers

Jev 1.13.0 answered on 2026-09-25, in calls made for the ThinkThen talk. The fetch rule above rebuilds the text of those calls byte for byte. Each cold answer is the matching one from the examples in `functions/`.

Octopus's Garden, `annotate`, 1,475 input tokens. Cold, the album was not sure: Revolver 0.39 and the White Album 0.58 ([annotate](walkthroughs/annotate.md)).

```text
singer: John 0.0, Paul 0.0, George 0.0, Ringo 1.0
album:  Help! 0.0, Rubber Soul 0.0, Revolver 0.0, White Album 0.0, Abbey Road 1.0
year:   1965 0.0, 1966 0.0, 1967 0.0, 1968 0.0, 1969 1.0
```

She Loves You, `choose`, 6,174 input tokens. Cold, John got 0.3 and the duet 0.29 ([choose](walkthroughs/choose.md)).

```text
John 0.01, Paul 0.0, George 0.0, Ringo 0.0, John and Paul duet 0.99
```

A Day in the Life, `decide`, 7,035 input tokens. Cold, yes got 0.93 on the same question in [filter](walkthroughs/filter.md) and 0.94 in [decide](walkthroughs/decide.md).

```text
probability of yes: 0.02
```

All three turn right. `data/songs.tsv` gives Octopus's Garden to Starr on Abbey Road in 1969, She Loves You to Lennon and McCartney, and A Day in the Life to Sgt. Pepper's Lonely Hearts Club Band.

The article costs more than the catalog entry. She Loves You took 6,174 input tokens with its article and 382 with its catalog entry, and both runs picked the duet.

## Why no recording

A recording holds the request, and the request holds the article. Ian confirmed on 2026-09-25 that the rule in `data/SOURCES.md` stands: no Wikipedia text in the repository. So these three answers cannot replay, and the tests leave this page out.

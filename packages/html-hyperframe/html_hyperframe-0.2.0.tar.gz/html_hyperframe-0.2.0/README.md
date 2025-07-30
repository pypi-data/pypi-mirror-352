# HyperFrame

HyperFrame structures related information in an HTML document by searching for recurrent patterns in its element tree.

## An example

Install the package with

```sh
pip install html-hyperframe
```

You can then extract hyperframes from an HTML document with

```python
import requests
from hyperframe import find_and_create_hyperframes

r = requests.get("https://wellhung.co.uk/")
hyperframes = find_and_create_hyperframes(r.content)
hyperframes[22]

...

  (div, class)                                  (div, 0, a, href) (div, 0, a, rel)                 (div, 0, a, title)               (div, 0, a, 0, text) (div, 2, small, class) (div, 2, small, 0, text) (div, 2, small, 1, a, href) (div, 2, small, 1, a, 0, text)
0        title          https://wellhung.co.uk/product/bombshell/         bookmark                          Bombshell                          Bombshell                 artist                       by      /artists/cassandra-yap                  Cassandra Yap
1        title  https://wellhung.co.uk/product/great-vibes-gol...         bookmark  Great Vibes – Gold Chrome Edition  Great Vibes – Gold Chrome Edition                 artist                       by          /artists/ben-rider                      Ben Rider
2        title  https://wellhung.co.uk/product/great-vibes-neo...         bookmark         Great Vibes – Neon Edition         Great Vibes – Neon Edition                 artist                       by          /artists/ben-rider                      Ben Rider
3        title  https://wellhung.co.uk/product/cest-nes-pas-ba...         bookmark              C’est N’es Pas Banana              C’est N’es Pas Banana                 artist                       by               /artists/luap                           LUAP
4        title             https://wellhung.co.uk/product/voyeur/         bookmark                             Voyeur                             Voyeur                 artist                       by      /artists/cassandra-yap                  Cassandra Yap
5        title  https://wellhung.co.uk/product/i-fucking-love-...         bookmark                 I Fucking Love You                 I Fucking Love You                 artist                       by   /artists/carrie-reichardt               Carrie Reichardt
6        title  https://wellhung.co.uk/product/dont-believe-ev...         bookmark  Dont Believe Everything you Think  Dont Believe Everything you Think                 artist                       by   /artists/carrie-reichardt               Carrie Reichardt
7        title            <https://wellhung.co.uk/product/be-kind/>         bookmark                            Be Kind                            Be Kind                 artist                       by   /artists/carrie-reichardt               Carrie Reichardt
```

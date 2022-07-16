# hTXT Viewer

A set of tools for viewing Hebrew DOS Text files. 

This tool supports viewing old DOS plaintext files written in Hebrew (*[Code page 862](https://en.wikipedia.org/wiki/Code_page_862)*, a.k.a *MS-DOS Hebrew* or *OEM Hebrew*). 

Basic ASCII Art via *[Code page 437](https://en.wikipedia.org/wiki/Code_page_437)* is supported as well, as well as some [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code). In order to accurately display the ASCII art, a fixed width font ([Classic Console Neue](http://webdraft.hu/fonts/classic-console/)) is used.

## Tools

### Online Viewer

An online viewer can be found [here](https://dvd848.github.io/hTXT-Viewer/hTXT.html). The viewer converts the old text files to UTF-8, and allows exporting the result to an image. Since Code Page 437 was frequently used in [NFO Files](https://en.wikipedia.org/wiki/.nfo), this tool can be considered a basic **Online NFO Viewer** as well.

![](images/online_tool.png)


### Python Script

The Python script under `scripts` can be used to convert the text files to images. 

```console
$ python3 hTXT.py -h
usage: hTXT.py [-h] -i INPUT [-o OUTPUT] [-w CONSOLE_WIDTH] [-s]

Decode old Hebrew text files encoded with Code Page 862

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file
  -o OUTPUT, --output OUTPUT
                        Output file
  -w CONSOLE_WIDTH, --console-width CONSOLE_WIDTH
                        Console width
  -s, --skip_ansi       Skip ANSI Color codes
```

The script depends on the `Pillow` (`PIL` fork) library:

```console
$ python3 -m pip install --upgrade Pillow
```

## Examples

These examples were contributed by Uri Tidhar (Anaesthesia BBS Archive) and received from [@hananc](https://twitter.com/hananc) as part of the [Israeli Digital History Preservation Project](https://digital-archive.org.il/). 

If you have additional materials, please [contact Hanan](https://digital-archive.org.il/donate-materials/) and help preserve the history of Israeli computing!

![](examples/AREA3x.png)

![](examples/D_AGE.png)

![](examples/EARTH01.png)

![](examples/TAKANON.png)

![](examples/TOPLINK.png)

![](examples/ULTI-01.png)

![](examples/ULTI-20.png)

The original text files are available under the `examples` folder.

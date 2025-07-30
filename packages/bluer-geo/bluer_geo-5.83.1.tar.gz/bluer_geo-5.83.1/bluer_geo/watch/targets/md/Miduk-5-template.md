# 🌐 Miduk-5

```bash
@select geo-watch-$(@@timestamp)
@geo watch - \
  target=Miduk-5 - \
  to=localflow - - .

@assets publish \
  download,extensions=gif,push .
```

```bash
@select geo-watch-diff-$(@@timestamp)
@geo watch - \
  target=Miduk-5 algo=diff \
  to=localflow - - .

@assets publish \
  download,extensions=gif,push .
```

set:::object5_name geo-watch-2025-06-03-ghm6t0
set:::object5_diff_name geo-watch-diff-2025-06-03-7v1z3v

| | |
|-|-|
| assets:::get:::object5_name/get:::object5_name.gif | assets:::get:::object5_diff_name/get:::object5_diff_name.gif |

--urls--

--footer--
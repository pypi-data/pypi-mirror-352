# sphinx-localtime: automatic local timezone HTML conversion

This allows you to define a time with a timezone, and HTML renders
will show it converted to the apparent local timezone, with a tooltip
with the original time.

How it works:

* The role contains a date and optional format:

  ```rst
  :localtime:`10:00 August 8, 2024 +03:00`
  :localtime:`10:00 August 8, 2024 +03:00 (HH:mm)`
  ```
* At build time (all server-side), `python-dateutil` parses those
  dates and converts it to UTC.
* It embeds the UTC timestamp and some javascript into the built HTML
  file.  When rendered, `dayjs` converts it to `HH:mm` or the format
  in parentheses.



## Installation

`pip install
https://github.com/coderefinery/sphinx-localtime/archive/main.zip`
(PyPI release to come later)

Add `sphinx_localtime` to extensions in conf.py



## Examples

Show time in `hh:mm`:
```rst
The meeting is at :localtime:`13 Aug 2024 10:00:00 +03:00`.
```

Show time as `hh:mm (on YYYY-MM-DD)`. `[]` is used to escape raw
text - this is dayjs syntax:

```rst
The course starts at :localtime:`13 Aug 2024 10:00:00
+03:00 (hh:mm [on ]YYYY-MM-DD[)])`
```

You can show the detected timezone at a certain time with the format
`zzz`:
```rst
The times on this page are automatically converted by your
browser into the timezone :localtime:`13 Aug 2024 (zzz)`.
```



## Usage

The time format can be anything parsed by `dateutil.parser.parse`.  A
parenthesized time format (in the form in
<https://day.js.org/docs/en/display/format>) is used for the output.
The default output format is `HH:mm`.  Note the escapes aren't
`printf` standard but what is used by `dayjs`.

ReST::
```rst
:localtime:`13 Aug 2024 10:00:00 +03:00`
:localtime:`13 Aug 2024 10:00:00 +03:00  (D MMM HH:mm)`

:localtime:`13 Aug 2024  (zzz)`
```

MyST:

```md
{localtime}`13 Aug 2024 10:00:00 +03:00`
{localtime}`13 Aug 2024 10:00:00 +03:00  (D MMM HH:mm)`

{localtime}`13 Aug 2024 (zzz)`
```

Rendered:
```
10:00
13 Aug 10:00

Eastern European Summer Time
```



## Specifying timezones in the source

Currently it is safest to use formats such as `+03:00`, for example
`13 Aug 2024 10:00 +03:00`.

In order for the conversion to work, you need to specify a timezone in
your original date in a format that `dateutil.parser.parse` can
understand.  This seems to be harder than it looks (if anyone can
help: please do!).  What we know:

* Using `+03:00` and similar seems safe.
* Using long names like `Europe/Helsinki` would be good but
  `dateutil.parser.parse` doesn't recognize them.
* Short abbreviations like `EDT`, `EEST` should work, but only for
  some common ones, and it seems that all the summer/daylight saving
  ones don't.  One could generate a list of all abbreviations, but
  they aren't necessarily unique. (Anything listed in
  `pytz.all_timezones_set` should work).
  * It *does* work for your local timezone.  So it'll act differently
    on different build hosts...
  * Short non-summer time names are wrong when used in summer time.

Currently it is safest to use formats such as `+03:00`.

In conf.py you can set a default, then you don't need to add a
timezone to every individual localtime role:

```python
import dateutil.tz
localtime_default_tz = dateutil.tz.gettz('Europe/Helsinki')
```



## Status and development

Beta but being used in our own production.  Contributions welcome.

Big issues:

* Non-HTML builders work but don't give the most useful output - but
  it does show something minimally useful so people know what the time
  is, without localtime conversion.
* Timezone abbreviation lookup could be improved.
* The name could be still changed.

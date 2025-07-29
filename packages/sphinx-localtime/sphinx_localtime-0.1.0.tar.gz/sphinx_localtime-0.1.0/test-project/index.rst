.. Test documentation master file, created by
   sphinx-quickstart on Tue Aug 13 23:27:54 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tests of sphinx-localtime
=========================

Tests of sphinx-localtime:


localtime
---------

The `localtime` role:

* ``13 Aug 2024 10:00:00 +03:00``: :localtime:`13 Aug 2024 10:00:00 +03:00`.
* ``13 Aug 2024 10:00:00 +03:00``: :localtime:`13 Aug 2024 10:00:00 +03:00`.
* ``13 Aug 2024 10:00:00 +03:00 (D MMM HH:mm)``: :localtime:`13 Aug
  2024 10:00:00 +03:00 (D MMM HH:mm)`
* ``13 Aug 2024 10:00:00 +03:00 (HH:mm z)``: :localtime:`13 Aug
  2024 10:00:00 +03:00 (HH:mm z)`
* ``13 Aug 2024 10:00:00 +03:00 (HH:mm zzz)``: :localtime:`13 Aug
  2024 10:00:00 +03:00 (HH:mm zzz)`


localtime2
----------

The `localtime2` role has a different hover text and is designed for
showing the timezone without a date.  The date (and maybe time) is
important since it gets the detected timezone at that date/time.

* ``13 Aug 2024 (zzz)``: Your detected timezone
  is :localtime2:`13 Aug 2024 (zzz)`
* ``13 Dec 2024 (zzz)``: Your detected timezone
  is :localtime2:`13 Dec 2024 (zzz)`
* ``13 Aug 2024 (z)``: Your detected timezone
  is :localtime2:`13 Aug 2024 (z)`
* ``13 Dec 2024 (z)``: Your detected timezone
  is :localtime2:`13 Dec 2024 (z)`


Test of invalid format
----------------------

* :localtime:`This is an invalid time`


Test of timezones detection
---------------------------

* ``+03:00``: :localtime:`10:00 +03+00`
* ``EET``: :localtime:`10:00 EET`
* ``CET``: :localtime:`10:00 CET`
* ``EST``: :localtime:`10:00 EST`
* ``UTC``: :localtime:`10:00 UTC`
* ``EEST``: :localtime:`10:00 EEST` (expected failure if you aren't in
  EEST)
* ``CEST``: :localtime:`10:00 CEST` (expected failure if you aren't in
  CEST)
* ``Europe/Helsinki``: :localtime:`10:00 Europe/Helsinki` (expected failure)


Repeat of one of the above
--------------------------
(for use in testing caching in non-HTML formats)

* ``13 Aug 2024 10:00:00 +03:00``: :localtime:`13 Aug 2024 10:00:00 +03:00`


Other pages
-----------

.. toctree::

   empty

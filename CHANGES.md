Changelog for Hatch Gettext
===========================

1.0.0 (2024-04-12)
------------------

 - Add options to use `intltool` to regenerate the .pot template, check for 
   left out files, and display a status report.
 - If LINGUAS file or environment variable is specified, only generate mo files
   for languages it specifies.

0.6.0 (2024-03-27)
------------------

- Use hyphens rather than underscores for TOML option names

0.5.0 (2024-03-26)
------------------

- Use Hatch's verbosity to determine console output
- Use rich for console output

0.0.2 (2024-03-22)
------------------

- Pass mypy validation

0.0.1 (2024-03-21)
------------------

- Initial release

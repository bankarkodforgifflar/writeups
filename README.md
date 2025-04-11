> IMPORTANT! All writeups MUST START with a metadata tag. No spaces, newlines or other BS before!

# Giffel writeups

Very serious writeups :neckbeard:

## Markdown Metadata Tag

To display metadata on our writeup site we include a metadata tag in every markdown writeup.

**NOTE: THIS TAG IS MANDATORY**

The tag is as following

```markdown
<!--BKFG
title="Fake"
author="TheGoat"
date="2024/03/07"
-->
```

It is a modified html comment and should be included in the start of every writeup.

The data included is in the **TOML** format because it's easy to use.

**_For metadata fields, please consult the table below_**

### Metadata fields

**NOTE: Since I (spamix) am a rust stan I've just used _rust-like_ types below. _VERY easy_ to understand tbh**

| name   | description                                                   | optional | type        |
| ------ | ------------------------------------------------------------- | -------- | ----------- |
| title  | Title of the writeup                                          | false    | String      |
| author | Author of the writeup                                         | true     | String      |
| date   | Date the writeup was written, needs to follow format YYYYMMDD | true     | String/Date |

More fields to come!

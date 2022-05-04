# CDB - Disk based Log Structured Hash Table Store

![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
[![build](https://github.com/avinassh/cdb/actions/workflows/build.yml/badge.svg)](https://github.com/avinassh/cdb/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/avinassh/cdb/branch/master/graph/badge.svg?token=9SA8Q4L7AZ)](https://codecov.io/gh/avinassh/cdb)
[![GitHub license](https://badgen.net/github/license/Naereen/Strapdown.js)](https://github.com/avinassh/cdb/blob/master/LICENSE)

![architecture](https://user-images.githubusercontent.com/640792/166490746-fb41709e-cdb5-4c9a-a58b-f4e6d530b5c7.png)

(educational) build your own disk based KV store

## What Next?

cdb has following the limitations, improving them would be a great challenge for the next step:

- single file
- add CRC check
- hint file 
- using a red-black tree instead of a map
- multi process 
- delete support
- garbage collector

## Line Count

```shell
$ tokei -f format.py disk_store.py

===============================================================================
 Language            Files        Lines         Code     Comments       Blanks
===============================================================================
 Python                  2          383          255          103           25
-------------------------------------------------------------------------------
 disk_store.py                      196          114           70           12
 format.py                          187          141           33           13
===============================================================================
 Total                   2          383          255          103           25
===============================================================================
```

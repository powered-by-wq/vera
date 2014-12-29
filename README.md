[![vera](https://raw.github.com/wq/wq/master/images/256/vera.png)](http://wq.io/vera)

[vera](http://wq.io/vera) is the reference implementation of the Entity-Record-Attribute-Value ([ERAV](http://wq.io/docs/erav)) data model. ERAV is an extension to Entity-Attribute-Value (EAV) that adds support for maintaining multiple versions of an entity with different provenance [^1].

[![Build Status](https://travis-ci.org/wq/vera.svg?branch=master)](https://travis-ci.org/wq/vera)
[![PyPI Package](https://pypip.in/version/vera/badge.svg?style=flat)](https://pypi.python.org/pypi/vera)

Tested on Python 2.7 and 3.4, with Django 1.6 and 1.7.

The implementation of ERAV provided by vera is optimized for storing and tracking changes to *time series data* as it is exchanged between disparate technical platforms (e.g. mobile devices, Excel spreadsheets, and third-party databases).  In this context, ERAV can be interpreted to mean Event-Report-Attribute-Value, as it represents a series of *events* being described by the *reports* submitted about them by various contributors in e.g. an environmental monitoring or citizen science project.

Getting Started
===============

```bash
pip3 install vera
```

vera is an extension to [wq.db](http://wq.io/wq.db), the database component of the [wq framework](http://wq.io).  See [the wq documentation](http://wq.io/docs/) for more information. See <https://github.com/wq/vera> to report any issues.

References
----------

[^1]: Sheppard, S. A., Wiggins, A., and Terveen, L. [Capturing Quality: Retaining Provenance for Curated Volunteer Monitoring Data](http://wq.io/research/provenance). To appear in Proceedings of the 17th ACM Conference on Computer Supported Cooperative Work and Social Computing (CSCW 2014). ACM. February 2014.

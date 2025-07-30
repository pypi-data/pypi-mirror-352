# Python log5
https://github.com/hailiang-wang/python-log5

```
pip install -U log5
```

Usage:

```
import log5
logger = log5.get_logger(log5.LN(__name__), output_mode=log5.OUTPUT_STDOUT)
logger.debug('bar')
logger.info('foo')

log5.set_log_level(log5.ERROR)
logger.info('foo2')
```

# License
[LICENSE](./LICENSE)
Python autodocumentation
=====================================

This module allows you to add call examples to your functions when you run tests.

Now supports only Flask docs with JSON response

Usage:
```

from autodocumentation import autodoc_dec

@app.route("/")
@autodoc_dec()
def index():
	"""
	Usage examples:

	<examples>
	"""
	return jsonify({"key": "value"})

```

Next, run your test with envvar AUTODOC_WRITE=1
Next, build docs with sphinx

And you'll get "<examples>" replaced with request info from tests.

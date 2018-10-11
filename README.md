# attrstance

Using [attrs], this project defines a callable validator dataclasses for:
* `isinstance(...)`
    * rework of `instance_of` for checking against whitelist
    * new validator for `all_instance_of` for an iterable value
* `issubclass(...)`
    * a new validator for `subclass_of` for checking against whitelist
    * a new validator for `all_subclass_of` for an iterable value


[attrs]: http://www.attrs.org/
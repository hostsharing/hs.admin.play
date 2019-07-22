Introduction
============

This package provides a generic interface between Ansible and the Hostsharing HSAdmin API package.
PROJEKT IST UMGEZOGEN: https://dev.hostsharing.net/repositories/

Example
-------

Please note that the ids argument will be removed from the Module class constructor
as soon as this information is provided by the backends theirselves.

In real world uses the argsfile will be populated by Ansible.

>>> from hs.admin.play import Module
>>> 
>>> module = Module(module='emailaddress',
...                 ids=['localpart', 'subdomain', 'domain'],
...                 argsfile='/tmp/argsfile')
>>>
>>> module()

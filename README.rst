======
picard
======
-----------
Make it so.
-----------

.. start-include

.. image:: https://travis-ci.org/thejohnfreeman/picard.svg?branch=master
   :target: https://travis-ci.org/thejohnfreeman/picard
   :alt: Build Status
.. image:: https://readthedocs.org/projects/picard/badge/?version=latest
   :target: https://picard.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

The idea of Ansible_ with the execution of Make_.

.. _Ansible: https://www.ansible.com/overview/how-ansible-works
.. _Make: https://www.gnu.org/software/make/manual/make.html

With Picard, you define a set of targets, each with a recipe that leaves it in
a desired state, e.g. a compiled executable or a running service. Targets may
depend on each other, e.g. "this executable depends on that source file" or
"this service depends on that host", in a directed acyclic graph. Like Make,
Picard executes the recipes for targets in dependency order.

Like Ansible, Picard comes with many sophisticated recipes out-of-the-box
that behave like rsync_: they find the differences between a target's present
state and its goal state, and execute just the changes necessary to transition
from the first to the second.

.. _rsync: https://linux.die.net/man/1/rsync

Make is limited to considering targets on the local filesystem, while Ansible
can consider more general targets and states, e.g. the existence and
configuration of remote machines. Ansible's input is a rigid declarative
template (based on Jinja_), while Make's input is an executable script that
builds the abstract definitions of the targets and gets to leverage functions
and variables. Picard tries to combine the best of both worlds in pure Python.

.. _Jinja: http://jinja.pocoo.org/

.. end-include

Help
====

Please see the documentation on `Read the Docs`_.

.. _`Read the Docs`: https://picard.readthedocs.io

If you have any questions, please ask me_ in the issues_, by email_, over
Twitter_, or however you want to reach me. I'll be happy to help you, because
it will help me make this documentation better for the next reader.

.. _me: https://github.com/thejohnfreeman
.. _issues: https://github.com/thejohnfreeman/picard/issues
.. _email: mailto:jfreeman08@gmail.com
.. _Twitter: https://twitter.com/thejohnfreeman

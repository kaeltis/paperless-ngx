*********
Paperless
*********

Paperless is a simple Django application running in two parts:
a *Consumer* (the thing that does the indexing) and
the *Web server* (the part that lets you search &
download already-indexed documents). If you want to learn more about its
functions keep on reading after the installation section.


Why This Exists
===============

Paper is a nightmare.  Environmental issues aside, there's no excuse for it in
the 21st century.  It takes up space, collects dust, doesn't support any form
of a search feature, indexing is tedious, it's heavy and prone to damage &
loss.

I wrote this to make "going paperless" easier.  I do not have to worry about
finding stuff again. I feed documents right from the post box into the scanner
and then shred them.  Perhaps you might find it useful too.


Paperless-ngx
=============

Paperless-ngx is a document management system that transforms your physical
documents into a searchable online archive so you can keep, well, *less paper*.

Paperless-ngx forked from paperless-ng to continue the great work and
distribute responsibility of supporting and advancing the project among a team
of people.

NG stands for both Angular (the framework used for the
Frontend) and next-gen. Publishing this project under a different name also
avoids confusion between paperless and paperless-ngx.

If you want to learn about what's different in paperless-ngx from Paperless, check out these
resources in the documentation:

*   :ref:`Some screenshots <screenshots>` of the new UI are available.
*   Read :ref:`this section <advanced-automatic_matching>` if you want to
    learn about how paperless automates all tagging using machine learning.
*   Paperless now comes with a :ref:`proper email consumer <usage-email>`
    that's fully tested and production ready.
*   Paperless creates searchable PDF/A documents from whatever you you put into
    the consumption directory. This means that you can select text in
    image-only documents coming from your scanner.
*   See :ref:`this note <utilities-encyption>` about GnuPG encryption in
    paperless-ngx.
*   Paperless is now integrated with a
    :ref:`task processing queue <setup-task_processor>` that tells you
    at a glance when and why something is not working.
*   The :ref:`changelog <paperless_changelog>` contains a detailed list of all changes
    in paperless-ngx.

Contents
========

.. toctree::
   :maxdepth: 1

   setup
   usage_overview
   advanced_usage
   administration
   configuration
   api
   faq
   troubleshooting
   extending
   contributing
   scanners
   screenshots
   changelog

Endtrz - Instagram Media Downloader
===================================

**Endtrz** is a powerful and modern command-line tool to download Instagram content — including photos, videos, reels, stories, IGTV, highlights, and more.

📦 Install: ``pip install Endtrz``  
🌐 Website: https://hasnainkk-07.vercel.app  
📧 Email: lord_izana@yahoo.com  
👤 Author: Endtrz  
🔗 GitHub: https://github.com/Endtrz/Endtrz

------------------

Features
--------

- 📸 Download posts (images/videos)
- 🎞️ Download reels and IGTV
- 📖 Download stories and highlights
- 👤 Download full profiles with profile pictures
- 🔒 Access private accounts with login
- 🧠 Avoid duplicates with smart caching
- 🔐 Supports Two-Factor Authentication (2FA)
- ⚡ Fast updates and resume support

------------------

Installation
------------

Install directly from PyPI:

.. code:: bash

   pip install Endtrz

------------------

Basic Usage
-----------

.. code:: bash

   endtrz <target>

Examples:

- Download a profile:

  .. code:: bash

     endtrz username

- Download a post:

  .. code:: bash

     endtrz https://www.instagram.com/p/POST_ID/

- Download a reel:

  .. code:: bash

     endtrz https://www.instagram.com/reel/REEL_ID/

- Download profile picture only:

  .. code:: bash

     endtrz --no-posts username

- Login for private data:

  .. code:: bash

     endtrz --login your_username

------------------

Advanced Commands
-----------------

- Download by hashtag:

  .. code:: bash

     endtrz "#hashtag"

- Download saved posts:

  .. code:: bash

     endtrz --login your_username :saved

- Download your feed:

  .. code:: bash

     endtrz :feed

- Fast update (skip existing):

  .. code:: bash

     endtrz --fast-update username

------------------

License
-------

This project is licensed under the MIT License.

------------------

Contact
-------

- 🧑 Author: Endtrz
- 📧 Email: lord_izana@yahoo.com
- 🌐 Website: https://hasnainkk-07.vercel.app
- 🔗 Source Code: https://github.com/Endtrz/Endtrz

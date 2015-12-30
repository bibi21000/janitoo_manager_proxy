#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of **janitoo** project https://github.com/bibi21000/janitoo.
    :platform: Unix, Windows, MacOS X

.. moduleauthor:: bibi21000 aka Sébastien GALLET <bibi21000@gmail.com>

License : GPL(v3)

**janitoo** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**janitoo** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with janitoo. If not, see http://www.gnu.org/licenses.

"""
from setuptools import setup, find_packages
import glob
import os
import sys
from _version import janitoo_version

DEBIAN_PACKAGE = False
filtered_args = []

for arg in sys.argv:
    if arg == "--debian-package":
        DEBIAN_PACKAGE = True
    else:
        filtered_args.append(arg)
sys.argv = filtered_args

def get_data_files(res, rsrc, src, pattern):
    for root, dirs, fils in os.walk(src):
        if src == root:
            sub = []
            for fil in fils:
                sub.append(os.path.join(root,fil))
            res.append((rsrc, sub))
            for dire in dirs:
                get_data_files(res, os.path.join(rsrc, dire), os.path.join(root, dire), pattern)
    return res

data_files = []
get_data_files(data_files, 'docs','src/docs/','*')
get_data_files(data_files, 'config','src/config','*.py')
get_data_files(data_files, 'config','src/config','*.conf')
get_data_files(data_files, 'config','src/config','*.cfg')
get_data_files(data_files, 'config','src/config','*.mako')
get_data_files(data_files, 'config','src/config','README')

def get_package_data(res, pkgdir, src, pattern):
    for root, dirs, fils in os.walk(os.path.join(pkgdir, src)):
        #~ print os.path.join(pkgdir, src), root, dirs, fils
        if os.path.join(pkgdir, src) == root:
            sub = []
            for fil in fils:
                sub.append(os.path.join(src,fil))
            res.extend(sub)
            for dire in dirs:
                get_package_data(res, pkgdir, os.path.join(src, dire), pattern)
    return res

package_data = []
get_package_data(package_data, 'src/janitoo_manager_proxy', 'templates','*')
get_package_data(package_data, 'src/janitoo_manager_proxy', 'themes','*')
get_package_data(package_data, 'src/janitoo_manager_proxy', 'static','*')

#You must define a variable like the one below.
#It will be used to collect entries without installing the package
janitoo_entry_points = {
    "janitoo_manager.blueprint": [
        "janitoo_manager_proxy = janitoo_manager_proxy.views:get_blueprint",
    ],
    "janitoo_manager.menu_left": [
        "janitoo_manager_proxy = janitoo_manager_proxy.views:get_leftmenu",
    ],
    'janitoo_manager.network': [
        'janitoo_manager_proxy = janitoo_manager_proxy.network:extend',
    ],
}

setup(
    name = 'janitoo_manager_proxy',
    description = "A proxy for the web manager",
    long_description = "Also a good example of how to write an extension for janitoo_manager",
    author='Sébastien GALLET aka bibi2100 <bibi21000@gmail.com>',
    author_email='bibi21000@gmail.com',
    url='http://bibi21000.gallet.info/',
    license = """
        This file is part of Janitoo.

        Janitoo is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        Janitoo is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with Janitoo. If not, see <http://www.gnu.org/licenses/>.
    """,
    version = janitoo_version,
    #scripts=['src-web/scripts/jnt_web'],
    keywords = "admin",
    zip_safe = False,
    package_dir = {'' : 'src' },
    packages = find_packages('src', exclude=["scripts", "libraries", "docs", "config"]),
    install_requires = [
                     'janitoo_manager >= %s'%"0.0.6",
                    ],
    dependency_links = [
      'https://github.com/bibi21000/janitoo_manager/archive/master.zip#egg=janitoo_manager-%s'%"0.0.7",
    ],
    #include_package_data=True,
    include_package_data=True,
    data_files = data_files,
    package_data={
            'janitoo_manager_proxy': package_data,
        },
    entry_points = janitoo_entry_points,
)

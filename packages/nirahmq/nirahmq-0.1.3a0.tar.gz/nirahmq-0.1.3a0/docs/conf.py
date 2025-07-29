#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

# Sphinx settings
project = 'NirahMQ'
author = 'Dionisis Toulatos'
copyright = '2025, Dionisis Toulatos'
# version = '0.0'
# release = '0.0.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_multiversion',
    'sphinx_copybutton',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.viewcode',
]
nitpicky = False
highlight_language = 'guess'
toc_object_entries_show_parents = 'hide'
templates_path = ['templates']

# Autodoc settings
autodoc_class_signature = 'separated'
autodoc_default_options = {
    'show-inheritance': True,
    'member-order': 'groupwise',
}
autodoc_inherit_docstrings = False

# Intersphinx settings
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pydantic': ('https://docs.pydantic.dev/latest/', None),
    'paho': ('https://eclipse.dev/paho/files/paho.mqtt.python/html/', None)
}

# Sphinx multiversion settings
smv_tag_whitelist = r'v\d+\.\d+\.\d+.*$'
smv_branch_whitelist = r'master|dev'
smv_remote_whitelist = r'origin'
smv_released_pattern = r'^refs/(tags/v\d+\.\d+\.\d+|heads/master)$'
smv_outputdir_format = '{ref.name}'
smv_prefer_remote_refs = False

# Graphviz settings
graphviz_output_format = 'png'

# Inheritance settings
inheritance_graph_attrs = {
    'dpi': 300,
    # 'rankdir': 'TB',
}
inheritance_node_attrs = {
    'colorscheme': 'blues9',
    'color': 5,
    'fillcolor': 3,
    'fontcolor': 9
}
inheritance_edge_attrs = {
    'colorscheme': 'blues9',
    'color': 7,
}

# Viewcode settings
viewcode_line_numbers = True

# Theme settings
html_theme = 'furo'
html_theme_options = {
    'footer_icons': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/dionisis2014/nirahmq/',
            'html': '''
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 496 512" height="200px" width="200px" xmlns="http://www.w3.org/2000/svg">
                    <path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"></path>
                </svg>
            ''',
        },
        {
            'name': 'PyPI',
            'url': 'https://pypi.org/project/nirahmq/',
            'html': '''
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" role="img" viewBox="0 0 24 24" height="200px" width="200px" xmlns="http://www.w3.org/2000/svg">
                    <path d="M23.922 13.58v3.912L20.55 18.72l-.078.055.052.037 3.45-1.256.026-.036v-3.997l-.053-.036-.025.092z M23.621 5.618l-3.04 1.107v3.912l3.339-1.215V5.509zM23.92 13.457V9.544l-3.336 1.215v3.913zM20.47 14.71V10.8L17.17 12v3.913zM17.034 19.996v-3.912l-3.313 1.206v3.912zM17.17 16.057v3.868l3.314-1.206V14.85l-3.314 1.206zm2.093 1.882c-.367.134-.663-.074-.663-.463s.296-.814.663-.947c.365-.133.662.075.662.464s-.297.814-.662.946z M13.225 9.315l.365-.132-3.285-1.197-3.323 1.21.102.037 3.184 1.16zM20.507 10.664V6.751L17.17 7.965v3.913zM17.058 11.918V8.005l-3.302 1.202v3.912zM13.643 9.246l-3.336 1.215v3.913l3.336-1.215zM6.907 13.165l3.322 1.209v-3.913L6.907 9.252z M10.34 7.873l3.281 1.193V5.198l-3.28-1.193zM20.507 2.715L17.19 3.922v3.913l3.317-1.207zM16.95 3.903L13.724 2.73l-3.269 1.19 3.225 1.174zM15.365 4.606l-1.624.592v3.868l3.317-1.207V3.991l-1.693.615zm-.391 2.778c-.367.134-.662-.074-.662-.464s.295-.813.662-.946c.366-.133.663.074.663.464s-.297.813-.663.946z M10.229 18.41v-3.914l-3.322-1.209V17.2zM13.678 17.182v-3.913l-3.371 1.227v3.913z M13.756 17.154l3.3-1.2V12.04l-3.3 1.2zM13.678 21.217l-3.371 1.227v-3.912h-.078v3.912l-3.322-1.209v-3.913l-.053-.058-.025-.06-3.336-1.21v-3.948l.034.013 3.287 1.196.015-.078-3.261-1.187 3.26-1.187v-.109L3.876 9.62l-.307-.112 3.26-1.188v.877l.079-.055V6.769l3.257 1.185.058-.061L7.084 6.75l-.102-.037 3.24-1.179v-.083L6.854 6.677v.018l-.025.018v1.523L3.44 9.47v.02l-.025.017v4.007l-3.39 1.233v.019L0 14.784v3.995l.025.037 3.4 1.237.008-.006.007.01 3.4 1.238.008-.006.006.01 3.4 1.237.014-.009.012.01 3.45-1.256.026-.037-.078-.027zM3.493 9.563l3.257 1.185-3.257 1.187V9.562zM3.4 19.96L.078 18.752v-3.913l2.361.86.96.349v3.913zm.015-3.99L.335 14.85l-.182-.066 3.262-1.187v2.374zm3.399 5.231l-3.321-1.209v-3.912l3.321 1.209v3.912zM23.791 5.434l-3.21-1.17v2.338zM20.387 2.643l-3.24-1.18-3.27 1.19 3.247 1.182z"></path>
                </svg>
            ''',
        }
    ]
}
html_title = "NirahMQ"
html_sidebars = {
    '**': [
        'sidebar/brand.html',
        'sidebar/search.html',
        'sidebar/scroll-start.html',
        'sidebar/navigation.html',
        'sidebar/scroll-end.html',
        'sidebar/versioning.html',
    ],
}

# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AMGD-Optimizer'
copyright = '2025, Ibrahim Bakari'
author = 'Ibrahim Bakari'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'myst_parser',
]
#templates path
templates_path = ['_templates']

# List of patterns, relative to source dire to ignore
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) o.
source_suffix = {
    '.rst': None,
    '.md': None,
}

#Master toctree document.
master_doc = 'index'

# --  HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}
# statics files
html_static_path = ['_static']

# Custom sidebar templates 
# to template names.
html_sidebars = {
    '**': [
        'relations.html',  
        'searchbox.html',
    ]
}


# --  autodoc ----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# --  autosummary ------------------------------------------------
autosummary_generate = True

# --  napoleon ----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# --  intersphinx ------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
}

# --  mathjax ----------------------------------------------------
mathjax3_config = {
    'tex': {
        'inlineMath': [['$', '$'], ['\\(', '\\)']],
        'displayMath': [['$$', '$$'], ['\\[', '\\]']],
    },
}

# -- Custom configuration ---------------------------------------------------

#  Pygments style
pygments_style = 'sphinx'

# If true, `todo` and `todoList`.
todo_include_todos = False


htmlhelp_basename = 'AMGDOptimizerdoc'

# --  LaTeX output -----------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',
    
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',
    
    # Additional  LaTeX preamble.
    'preamble': '',
    
    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'AMGDOptimizer.tex', 'AMGD-Optimizer Documentation',
     'Ibrahim Bakari', 'manual'),
]

# -- manual page output -----------------------------------------
man_pages = [
    (master_doc, 'amgdoptimizer', 'AMGD-Optimizer Documentation',
     [author], 1)
]

# -- Texinfo output ---------------------------------------------
texinfo_documents = [
    (master_doc, 'AMGDOptimizer', 'AMGD-Optimizer Documentation',
     author, 'AMGDOptimizer', 'Adaptive Momentum Gradient Descent for Regularized Poisson Regression.',
     'Miscellaneous'),
]

# --  Epub output ------------------------------------------------
epub_title = project
epub_exclude_files = ['search.html']

# -- Additional AMGD-Optimizer specific configuration -----------------------

# HTML title
html_title = f'{project} v{release} Documentation'

# HTML short title
html_short_title = f'{project} v{release}'

# html_logo = '_static/logo.png'

# html_favicon = '_static/favicon.ico'

# Edit on GitHub links
html_context = {
    'display_github': True,
    'github_user': 'elbakari01',
    'github_repo': 'amgd-optimizer',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}

# Custom CSS files
html_css_files = [
    'custom.css',
]

# Social media and external links
html_theme_options.update({
    'github_url': 'https://github.com/elbakari01/amgd-optimizer',
    'twitter_url': 'https://twitter.com/yourusername', 
})

# Version info 
html_theme_options['versions'] = {
    'latest': 'v1.0.0',
    'stable': 'v1.0.0',
}
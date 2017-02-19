response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Index'),URL('default','index')==URL(),URL('default','index'),[]),
(T('Review'),URL('default','review_manage')==URL(),URL('default','review_manage'),[]),
(T('Product'),URL('default','product_manage')==URL(),URL('default','product_manage'),[]),
]
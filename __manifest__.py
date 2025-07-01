{
    'name': "Intern Stock Task",
    'version': '1.0',
    'depends': ['stock', 'base'],
    'author': "Gana",
    'category': 'Inventory',
    'description': "Simple Stock Request for Intern Task",
    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/sequence.xml',
    'views/stock_request.xml',
    'views/menu.xml',
 ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
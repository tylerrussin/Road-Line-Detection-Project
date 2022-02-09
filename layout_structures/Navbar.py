from dash import dcc
import dash_bootstrap_components as dbc

# Creating navbar
navbar = dbc.NavbarSimple(
    brand='Road Line Detection OpenCV',
    brand_href='/', 
    children=[
        dbc.NavItem(dcc.Link('Process', href='/process', className='nav-link')), 
    ],
    sticky='top',
    color='light', 
    light=True, 
    dark=False
)
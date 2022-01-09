from dash import html
import dash_bootstrap_components as dbc

# Creating footer
footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.P(
                [
                    html.Span('Tyler Russin', className='mr-2'), 
                    html.A(html.I(className='fas fa-envelope-square mr-1'), href='mailto:tylerrussin2@gmail.com', style={
                                                                                                                        "padding-top": "2px",
                                                                                                                        "padding-right": "2px",
                                                                                                                        "padding-bottom": "2px",
                                                                                                                        "padding-left": "10px",
                                                                                                                        "color": "rgb(17,157,255)"
                                                                                                                        }), 
                    html.A(html.I(className='fab fa-github-square mr-1'), href='https://github.com/Tyler9937/Tanzanian-Ministry-of-Water-Dataset-App', style={
                                                                                                                        "padding-top": "2px",
                                                                                                                        "padding-right": "2px",
                                                                                                                        "padding-bottom": "2px",
                                                                                                                        "padding-left": "2px",
                                                                                                                        "color": "rgb(17,157,255)"
                                                                                                                        }), 
                    html.A(html.I(className='fab fa-linkedin mr-1'), href='https://www.linkedin.com/in/tyler-russin/', style={
                                                                                                                        "padding-top": "2px",
                                                                                                                        "padding-right": "2px",
                                                                                                                        "padding-bottom": "2px",
                                                                                                                        "padding-left": "2px",
                                                                                                                        "color": "rgb(17,157,255)"
                                                                                                                        }), 
                ], 
                className='lead'
            )
        )
    )
)
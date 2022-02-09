from dash import html
import dash_bootstrap_components as dbc

# Creating footer
# The footer at the bottom of the screen
footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.P(
                [
                    html.Span('Tyler Russin', className='mr-2'),

                    # Twitter URL
                    html.A(html.I(className='fab fa-twitter mr-1'), href='https://twitter.com/tyler_russin', style={
                                                                                                                    "padding-top": "2px",
                                                                                                                    "padding-right": "2px",
                                                                                                                    "padding-bottom": "2px",
                                                                                                                    "padding-left": "2px",
                                                                                                                    "color": "rgb(17,157,255)"
                                                                                                                    }),
                    # Linkedin URL
                    html.A(html.I(className='fab fa-linkedin mr-1'), href='https://www.linkedin.com/in/tyler-russin/', style={
                                                                                                                            "padding-top": "2px",
                                                                                                                            "padding-right": "2px",
                                                                                                                            "padding-bottom": "2px",
                                                                                                                            "padding-left": "2px",
                                                                                                                            "color": "rgb(17,157,255)"
                                                                                                                            }),
                    # GitHub URL
                    html.A(html.I(className='fab fa-github-square mr-1'), href='https://github.com/tylerrussin/Road-Line-Detection-Project', style={
                                                                                                                                                            "padding-top": "2px",
                                                                                                                                                            "padding-right": "2px",
                                                                                                                                                            "padding-bottom": "2px",
                                                                                                                                                            "padding-left": "2px",
                                                                                                                                                            "color": "rgb(17,157,255)"
                                                                                                                                                            }),
                    # Personal Email    
                    html.A(html.I(className='fas fa-envelope-square mr-1'), href='mailto:tylerrussin2@gmail.com', style={
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
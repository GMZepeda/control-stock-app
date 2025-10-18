import streamlit as st

def aplicar_estilos(config):
    """Aplica los estilos CSS según la configuración del tema."""
    
    if config.get("tema", "claro") == "oscuro":
        st.markdown("""
        <style>
        html, body, [class*="stAppViewContainer"] {
            background-color: #121212 !important;
            color: #e0e0e0 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {
            color: #e0e0e0 !important;
        }
        div[data-testid="stDataFrame"] table {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        div[data-testid="stDataFrame"] th {
            background-color: #2b2b2b !important;
            color: #f1f1f1 !important;
        }
        input, textarea, select {
            background-color: #2a2a2a !important;
            color: #f1f1f1 !important;
            border: 1px solid #555 !important;
        }
        button {
            background-color: #1976d2 !important;
            color: white !important;
            border-radius: 6px !important;
        }
        button:hover {
            background-color: #1565c0 !important;
        }
        button[data-baseweb="tab"] {
            background-color: #2a2a2a !important;
            color: #e0e0e0 !important;
            border: 1px solid #555 !important;
        }
        button[data-baseweb="tab"]:hover {
            background-color: #333333 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #111111 !important;
            background-color: #ffffff !important;
            border-bottom: 2px solid #1976d2 !important;
        }
        button[data-baseweb="tab"] *,
        button[data-baseweb="tab"] p,
        button[data-baseweb="tab"] span,
        button[data-baseweb="tab"] div {
            color: #e0e0e0 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] *,
        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] span,
        button[data-baseweb="tab"][aria-selected="true"] div {
            color: #111111 !important;
        }
        [data-testid="stMetric"] {
            background: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
        }
        label, p, span, div[data-testid="stMarkdownContainer"] h3 {
            color: #f1f1f1 !important;
        }
        h1, h2, h3, h4, h5 {
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
        html, body, [class*="stAppViewContainer"] {
            background-color: #f8f9fa !important;
            color: #000000 !important;
            font-size: 16px !important;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        label, label span, label p, label div {
            font-size: 1rem !important;
            color: #000000 !important;
            font-weight: 600 !important;
            line-height: 1.5 !important;
        }
        
        input, textarea, select {
            font-size: 1rem !important;
            color: #000000 !important;
            background-color: #ffffff !important;
            border: 2px solid #666666 !important;
            font-weight: 500 !important;
            padding: 0.5rem !important;
        }
        
        input[type="number"] {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
        
        div[data-baseweb="select"] div {
            color: #000000 !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
        }
        
        h1, h2, h3, h4, h5 {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        p, span, div {
            color: #000000 !important;
            font-size: 1rem !important;
        }
        
        button[data-baseweb="tab"] {
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #0066cc !important;
            font-weight: 700 !important;
        }
        
        thead tr th {
            background-color: #e8e8e8 !important;
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }
        
        tbody tr td {
            color: #000000 !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 1.6rem !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Estilos generales (aplican a ambos temas)
    st.markdown("""
    <style>
    html, body, [class*="stAppViewContainer"] {
        font-family: "Inter", "Segoe UI", "Roboto", sans-serif;
    }
    h1, h2, h3 {
        font-weight: 600;
        color: #1a1a1a;
        margin-top: 0.8em;
        margin-bottom: 0.6em;
    }
    h1 {
        border-bottom: 1px solid #e2e2e2;
        padding-bottom: 0.3em;
    }
    thead tr th {
        background-color: #f0f0f0 !important;
        color: #333 !important;
        font-weight: 600 !important;
    }
    tbody tr:nth-child(even) {
        background-color: #fafafa !important;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dddddd;
        border-radius: 10px;
        padding: 10px 6px;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] {
        color: #555 !important;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] {
        color: #111 !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        white-space: normal !important;
    }
    input, textarea {
        border-radius: 6px !important;
        border: 1px solid #cccccc !important;
    }
    button {
        border-radius: 6px !important;
        background-color: #0066cc !important;
        color: white !important;
        font-weight: 500 !important;
        border: none !important;
    }
    button:hover {
        background-color: #005bb5 !important;
    }
    div[data-testid="stTextInput"], div[data-testid="stButton"] {
        margin-top: 0.4rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stMarkdownContainer"] h3 {
        font-size: 1.2rem;
        font-weight: 600;
        color: #222;
        border-left: 4px solid #0a74da;
        padding-left: 10px;
        background-color: #f1f4f8;
        border-radius: 4px;
        padding-top: 6px;
        padding-bottom: 6px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    section.main {
        background-color: #f8f9fa !important;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border: 1px solid #cfd8dc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
        padding: 0 !important;
        height: 2.2rem !important;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.03);
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {
        border: 1px solid #0a74da !important;
        box-shadow: 0 0 0 1px #0a74da inset !important;
    }
    label {
        font-size: 0.9rem !important;
        color: #333 !important;
        font-weight: 500 !important;
        margin-bottom: 0.2rem !important;
    }
    button[data-baseweb="tab"] {
        background-color: #f2f5fa !important;
        color: #333 !important;
        border-radius: 6px 6px 0 0 !important;
        border: 1px solid #d9e1ec !important;
        border-bottom: none !important;
        font-weight: 500 !important;
        padding: 0.4rem 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0a74da !important;
        border-bottom: 2px solid white !important;
    }
    div[data-testid="stDataFrame"] {
        margin-top: 1rem !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        background-color: #fff !important;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stAlert"] {
        background-color: #f7f9fc !important;
        border: 1px solid #dbe5ef !important;
        color: #333 !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)
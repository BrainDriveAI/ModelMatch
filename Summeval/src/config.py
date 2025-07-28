MAX_TOKENS = {"OpenAI": 8000, "DeepSeek": 8000, "Claude": 4000}

PRESET = {
    "Twin-Lock":  dict(coverage=0.25, alignment=0.20, hallucination=0.15, relevance=0.15, bias_toxicity=0.05),
    "Judge-Lock": dict(coverage=0.35, alignment=0.15, hallucination=0.30, relevance=0.15, bias_toxicity=0.05)
}

CSS = """
body,.gradio-container{background:#f7f7f7!important;color:#1a1a1a!important}
textarea,textarea.gr-input{background:#f7f7f7!important;color:#1a1a1a!important}
textarea::placeholder,input::placeholder{color:#666!important}
input[type=radio]{accent-color:#000000}
input[type=checkbox]{accent-color:#000000}
#variant-group input[type=radio]{accent-color:#ffa500}
#backend-group input[type=checkbox]{accent-color:#0074d9}
.metric-slider input[type=range]::-webkit-slider-thumb,
.metric-slider input[type=range]::-moz-range-thumb{background:#21a366!important}
.metric-slider input[type=range]::-webkit-slider-runnable-track,
.metric-slider input[type=range]::-moz-range-track{background:#cfe8db!important}
#btn-twin,#btn-judge,#run-btn{background:#000000!important;color:#ffffff!important;border-radius:6px!important}
"""
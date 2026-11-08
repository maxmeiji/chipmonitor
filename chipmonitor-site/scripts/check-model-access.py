import ast,json,re
from pathlib import Path
source=Path('scripts/prepare-news.py').read_text();tree=ast.parse(source)
ns={'re':re}
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['has','model_access','classify']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),'routing','exec'),ns)
classify=ns['classify'];access=ns['model_access']
cases=[
 ({'title':"Google's Nano Banana 2.1 Takes #4 in Image Benchmarks at Half Cost",'summary':'Available via Google AI Studio, Vertex AI, OpenRouter and fal.'},False),
 ({'title':'OpenAI GPT-6 Beats Open-Weight DeepSeek at Coding','summary':'DeepSeek is an open-weight model served through OpenRouter.'},False),
 ({'title':'Google Releases Gemma Open-Weight Model','summary':'Gemma weights are available.'},True),
 ({'title':'Moonshot AI Releases Weights for Kimi Model','summary':'The model weights are available.'},True),
 ({'title':'Company Launches New Model on OpenRouter','summary':'API access is available on OpenRouter.'},False),
 ({'title':'Google Gemini Model Launches','summary':'It competes with open-source Qwen and DeepSeek models.'},False),
 ({'title':'New GPU Server Runs Open-Source Software','summary':'Its scheduler is open source.'},False)
]
for s,expected in cases:
 actual=any(b['id']=='C1' for b in classify(s));assert actual==expected,(s['title'],actual,expected)
print('PASS: subject-level access checks reject OpenRouter-only access, comparator leakage and open-source software; permit explicit Gemma/Kimi weight releases.')

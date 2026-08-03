#!/usr/bin/env python3
"""Apply a one-time replacement of the inaccessible Cromai validation source."""
from pathlib import Path

path = Path("scripts/validate_live_outputs.py")
text = path.read_text(encoding="utf-8")
old = '''            {"url": "https://www.cromai.com/", "type": "official_site", "anchors": ["visão computacional", "IA", "imagens"]},
            {"url": "https://www.cromai.com/a-cromai/", "type": "official_site", "anchors": ["inteligência artificial", "agricultura", "visão computacional"]},
            {"url": "https://polosebraeagro.sebrae.com.br/agritech-sebrae/cromai/", "type": "directory", "anchors": ["Cromai", "inteligência artificial", "imagens"]},
'''
new = '''            {"url": "https://www.cromai.com/", "type": "official_site", "anchors": ["inteligência artificial", "IA", "plantas daninhas"]},
            {"url": "https://agencia.fapesp.br/artificial-intelligence-applied-to-drone-imagery-helps-improve-agricultural-productivity/50441", "type": "news", "anchors": ["Cromai", "artificial intelligence", "drone"]},
            {"url": "https://impacto.google/historias/cromai", "type": "directory", "anchors": ["Cromai", "inteligência artificial", "plantas daninhas"]},
            {"url": "https://startups.com.br/negocios/sustentabilidade/cromai-com-tecnologia-agro-sustentavel-e-tambem-mais-lucrativo/", "type": "news", "anchors": ["Cromai", "IA", "plantas daninhas"]},
'''
if old not in text:
    raise RuntimeError("Cromai validation source block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
Path(__file__).unlink()
print("Cromai validation now uses accessible independent evidence sources")

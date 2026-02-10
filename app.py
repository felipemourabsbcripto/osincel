#!/usr/bin/env python3
"""
PhoneOsint API - Versão Web para Azure
"""

from flask import Flask, request, jsonify
import subprocess
import re
import json
import os

app = Flask(__name__)

def validate_phone(phone):
    """Valida número de telefone"""
    # Remove caracteres não numéricos exceto +
    cleaned = re.sub(r'[^\d+]', '', phone)
    return cleaned if len(cleaned) >= 8 else None

def get_phone_info(phone):
    """Obtém informações do número de telefone"""
    info = {
        "numero": phone,
        "valido": False,
        "pais": None,
        "operadora": None,
        "localizacao": None,
        "formatado": None
    }
    
    # Validação básica
    if not phone or len(phone) < 8:
        return info
    
    info["valido"] = True
    
    # Detecção de país pelo prefixo
    if phone.startswith('+55') or phone.startswith('55'):
        info["pais"] = "Brasil"
    elif phone.startswith('+1'):
        info["pais"] = "Estados Unidos/Canadá"
    elif phone.startswith('+44'):
        info["pais"] = "Reino Unido"
    elif phone.startswith('+49'):
        info["pais"] = "Alemanha"
    elif phone.startswith('+33'):
        info["pais"] = "França"
    elif phone.startswith('+34'):
        info["pais"] = "Espanha"
    elif phone.startswith('+39'):
        info["pais"] = "Itália"
    elif phone.startswith('+81'):
        info["pais"] = "Japão"
    elif phone.startswith('+86'):
        info["pais"] = "China"
    elif phone.startswith('+7'):
        info["pais"] = "Rússia"
    elif phone.startswith('+91'):
        info["pais"] = "Índia"
    
    # Detecção de operadora brasileira
    if info["pais"] == "Brasil":
        # Remove +55 ou 55 do início
        numero_limpo = phone.replace('+55', '').replace('55', '')
        if len(numero_limpo) >= 2:
            ddd = numero_limpo[:2]
            info["localizacao"] = f"DDD {ddd}"
            
        # Detecta operadora pelo prefixo (simplificado)
        prefixos_vivo = ['15', '25', '95', '96', '97', '98', '99']
        prefixos_claro = ['21', '22', '23', '24', '31', '32', '33', '34', '35', '36', '37', '38', '71', '72', '73', '74', '75', '76', '77', '78', '79']
        prefixos_tim = ['41', '42', '43', '44', '45', '46', '47', '48', '49', '91', '92', '93', '94']
        prefixos_oi = ['81', '82', '83', '84', '85', '86', '87', '88', '89']
        
        if len(numero_limpo) >= 9:
            nono_digito = numero_limpo[2] if len(numero_limpo) > 10 else numero_limpo[1]
            prefixo = numero_limpo[-9:-7] if len(numero_limpo) >= 9 else ""
            
            if prefixo in prefixos_vivo:
                info["operadora"] = "Vivo"
            elif prefixo in prefixos_claro:
                info["operadora"] = "Claro"
            elif prefixo in prefixos_tim:
                info["operadora"] = "TIM"
            elif prefixo in prefixos_oi:
                info["operadora"] = "Oi"
            else:
                info["operadora"] = "Desconhecida"
    
    info["formatado"] = phone
    return info

@app.route('/')
def index():
    """Página inicial com documentação"""
    return jsonify({
        "nome": "PhoneOsint API",
        "versao": "1.0",
        "endpoints": {
            "GET /": "Esta documentação",
            "GET /api/phone/<numero>": "Consulta informações de um número de telefone",
            "POST /api/phone": "Consulta informações via JSON {\"phone\": \"+5511999999999\"}"
        },
        "exemplo": "/api/phone/+5511999999999"
    })

@app.route('/api/phone/<phone>')
def get_phone(phone):
    """Consulta informações de um número de telefone"""
    phone_clean = validate_phone(phone)
    if not phone_clean:
        return jsonify({"erro": "Número de telefone inválido"}), 400
    
    info = get_phone_info(phone_clean)
    return jsonify(info)

@app.route('/api/phone', methods=['POST'])
def post_phone():
    """Consulta informações via POST"""
    data = request.get_json()
    if not data or 'phone' not in data:
        return jsonify({"erro": "Campo 'phone' é obrigatório"}), 400
    
    phone_clean = validate_phone(data['phone'])
    if not phone_clean:
        return jsonify({"erro": "Número de telefone inválido"}), 400
    
    info = get_phone_info(phone_clean)
    return jsonify(info)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

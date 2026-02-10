#!/usr/bin/env python3
"""
PhoneOsint API - Versão Web para Azure
"""

from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def validate_and_format_phone(phone):
    """Valida e formata número de telefone"""
    if not phone:
        return None
    
    # Remove caracteres não numéricos exceto +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Se não tem + e tem 11 dígitos (padrão BR com DDD + 9 dígitos)
    if not cleaned.startswith('+') and len(cleaned) == 11 and cleaned.startswith('1'):
        cleaned = '+55' + cleaned
    # Se não tem + e tem 10 dígitos (padrão BR antigo)
    elif not cleaned.startswith('+') and len(cleaned) == 10 and cleaned.startswith('1'):
        cleaned = '+55' + cleaned
    # Se não tem + e tem 13 dígitos começando com 55
    elif not cleaned.startswith('+') and len(cleaned) == 13 and cleaned.startswith('55'):
        cleaned = '+' + cleaned
    # Se começa com 55 mas não tem +
    elif cleaned.startswith('55') and len(cleaned) >= 12:
        cleaned = '+' + cleaned
    
    # Validação mínima
    if len(cleaned) < 8:
        return None
    
    return cleaned

def get_phone_info(phone):
    """Obtém informações do número de telefone"""
    info = {
        "numero_original": phone,
        "numero": None,
        "valido": False,
        "pais": None,
        "operadora": None,
        "localizacao": None,
        "formatado": None
    }
    
    # Valida e formata
    phone_clean = validate_and_format_phone(phone)
    if not phone_clean:
        return info
    
    info["numero"] = phone_clean
    info["valido"] = True
    info["formatado"] = phone_clean
    
    # Detecção de país pelo prefixo
    paises = {
        '+55': 'Brasil',
        '+1': 'Estados Unidos/Canadá',
        '+44': 'Reino Unido',
        '+49': 'Alemanha',
        '+33': 'França',
        '+34': 'Espanha',
        '+39': 'Itália',
        '+81': 'Japão',
        '+86': 'China',
        '+7': 'Rússia',
        '+91': 'Índia',
        '+54': 'Argentina',
        '+52': 'México',
        '+51': 'Peru',
        '+56': 'Chile',
        '+57': 'Colômbia',
        '+58': 'Venezuela'
    }
    
    for prefixo, pais in paises.items():
        if phone_clean.startswith(prefixo):
            info["pais"] = pais
            break
    
    # Detecção de DDD e operadora para Brasil
    if info["pais"] == "Brasil":
        # Remove +55 do início
        numero_limpo = phone_clean.replace('+55', '')
        
        if len(numero_limpo) >= 2:
            ddd = numero_limpo[:2]
            info["localizacao"] = f"DDD {ddd} - {get_cidade_ddd(ddd)}"
            
            # Detecta operadora pelo nono dígito e prefixo
            if len(numero_limpo) >= 9:
                nono_digito = numero_limpo[2] if len(numero_limpo) > 10 else numero_limpo[1]
                prefixo = numero_limpo[-9:-7] if len(numero_limpo) >= 9 else ""
                
                info["operadora"] = detectar_operadora(prefixo, nono_digito)
    
    return info

def get_cidade_ddd(ddd):
    """Retorna a cidade/região do DDD"""
    cidades = {
        '11': 'São Paulo/SP', '12': 'São José dos Campos/SP', '13': 'Santos/SP',
        '14': 'Bauru/SP', '15': 'Sorocaba/SP', '16': 'Ribeirão Preto/SP',
        '17': 'São José do Rio Preto/SP', '18': 'Presidente Prudente/SP', '19': 'Campinas/SP',
        '21': 'Rio de Janeiro/RJ', '22': 'Campos dos Goytacazes/RJ', '24': 'Volta Redonda/RJ',
        '27': 'Vitória/ES', '28': 'Cachoeiro de Itapemirim/ES',
        '31': 'Belo Horizonte/MG', '32': 'Juiz de Fora/MG', '33': 'Governador Valadares/MG',
        '34': 'Uberlândia/MG', '35': 'Poços de Caldas/MG', '37': 'Divinópolis/MG',
        '38': 'Montes Claros/MG',
        '41': 'Curitiba/PR', '42': 'Ponta Grossa/PR', '43': 'Londrina/PR',
        '44': 'Maringá/PR', '45': 'Foz do Iguaçu/PR', '46': 'Francisco Beltrão/PR',
        '47': 'Joinville/SC', '48': 'Florianópolis/SC', '49': 'Chapecó/SC',
        '51': 'Porto Alegre/RS', '53': 'Pelotas/RS', '54': 'Caxias do Sul/RS',
        '55': 'Santa Maria/RS',
        '61': 'Brasília/DF', '62': 'Goiânia/GO', '63': 'Palmas/TO',
        '64': 'Rio Verde/GO', '65': 'Cuiabá/MT', '66': 'Rondonópolis/MT',
        '67': 'Campo Grande/MS', '68': 'Rio Branco/AC', '69': 'Porto Velho/RO',
        '71': 'Salvador/BA', '73': 'Ilhéus/BA', '74': 'Juazeiro/BA',
        '75': 'Feira de Santana/BA', '77': 'Vitória da Conquista/BA',
        '79': 'Aracaju/SE',
        '81': 'Recife/PE', '82': 'Maceió/AL', '83': 'João Pessoa/PB',
        '84': 'Natal/RN', '85': 'Fortaleza/CE', '86': 'Teresina/PI',
        '87': 'Petrolina/PE', '88': 'Juazeiro do Norte/CE', '89': 'Picos/PI',
        '91': 'Belém/PA', '92': 'Manaus/AM', '93': 'Santarém/PA',
        '94': 'Marabá/PA', '95': 'Boa Vista/RR', '96': 'Macapá/AP',
        '97': 'Coari/AM', '98': 'São Luís/MA', '99': 'Imperatriz/MA'
    }
    return cidades.get(ddd, 'Desconhecida')

def detectar_operadora(prefixo, nono_digito):
    """Detecta operadora pelo prefixo"""
    # Prefixos atualizados (simplificado)
    prefixos_vivo = ['15', '25', '95', '96', '97', '98', '99']
    prefixos_claro = ['21', '22', '23', '24', '31', '32', '33', '34', '35', '36', '37', '38']
    prefixos_tim = ['41', '42', '43', '44', '45', '46', '47', '48', '49', '91', '92', '93', '94']
    prefixos_oi = ['81', '82', '83', '84', '85', '86', '87', '88', '89']
    
    if prefixo in prefixos_vivo:
        return "Vivo"
    elif prefixo in prefixos_claro:
        return "Claro"
    elif prefixo in prefixos_tim:
        return "TIM"
    elif prefixo in prefixos_oi:
        return "Oi"
    else:
        return "Não identificada"

@app.route('/')
def index():
    """Página inicial com documentação"""
    return jsonify({
        "nome": "PhoneOsint API",
        "versao": "1.1",
        "autor": "PhoneOsint",
        "endpoints": {
            "GET /": "Esta documentação",
            "GET /api/phone/<numero>": "Consulta informações de um número de telefone",
            "POST /api/phone": "Consulta informações via JSON {\"phone\": \"+5511999999999\"}",
            "GET /health": "Verifica se a API está funcionando"
        },
        "exemplos": [
            "/api/phone/+5511999999999",
            "/api/phone/11999999999",
            "/api/phone/(11) 99999-9999"
        ],
        "formatos_aceitos": [
            "+5511999999999",
            "5511999999999",
            "11999999999",
            "(11) 99999-9999",
            "11 99999-9999"
        ]
    })

@app.route('/api/phone/<path:phone>')
def get_phone(phone):
    """Consulta informações de um número de telefone"""
    # Decodifica URL encoding
    phone = phone.replace('%20', ' ').replace('%2B', '+')
    
    info = get_phone_info(phone)
    
    if not info["valido"]:
        return jsonify({"erro": "Número de telefone inválido", "numero_recebido": phone}), 400
    
    return jsonify(info)

@app.route('/api/phone', methods=['POST'])
def post_phone():
    """Consulta informações via POST"""
    data = request.get_json()
    if not data or 'phone' not in data:
        return jsonify({"erro": "Campo 'phone' é obrigatório"}), 400
    
    info = get_phone_info(data['phone'])
    
    if not info["valido"]:
        return jsonify({"erro": "Número de telefone inválido"}), 400
    
    return jsonify(info)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "ok", "servico": "PhoneOsint API"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"erro": "Endpoint não encontrado", "use": "/ para documentação"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"erro": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

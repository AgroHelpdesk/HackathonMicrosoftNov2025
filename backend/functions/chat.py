"""
Chat Functions - Processamento de mensagens de chat com Azure OpenAI
"""
import azure.functions as func
import logging
import json
import os
from datetime import datetime
from openai import AzureOpenAI

# Criar blueprint
bp = func.Blueprint()

# Configuração Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')

# Inicializar cliente OpenAI
client = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-15-preview"
    )


@bp.route(route="chat", methods=["POST"])
def process_chat(req: func.HttpRequest) -> func.HttpResponse:
    """Processa mensagem de chat"""
    logging.info('POST /api/chat')
    
    try:
        req_body = req.get_json()
        message = req_body.get('message', '')
        
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "Message is required"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Classificar intenção
        intent = classify_intent(message)
        
        # Gerar resposta baseada na intenção
        response_text = generate_response(message, intent)
        
        # Determinar agente responsável
        agent = determine_agent(intent)
        
        response = {
            "response": response_text,
            "agent": agent,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error processing chat: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


def classify_intent(message: str) -> str:
    """
    Classifica a intenção da mensagem usando Azure OpenAI
    
    Args:
        message: Mensagem do usuário
        
    Returns:
        Intenção classificada
    """
    if not client:
        # Fallback para classificação simples
        message_lower = message.lower()
        if any(word in message_lower for word in ['fungo', 'praga', 'doença', 'folha']):
            return "field_diagnosis"
        elif any(word in message_lower for word in ['vibração', 'alerta', 'sensor', 'telemetria']):
            return "equipment_alert"
        elif any(word in message_lower for word in ['como', 'quando', 'qual', 'onde']):
            return "knowledge_query"
        else:
            return "general"
    
    try:
        system_prompt = """Você é um assistente especializado em agricultura que classifica mensagens de usuários.
        
Classifique a mensagem em uma das seguintes categorias:
- field_diagnosis: Diagnóstico de problemas no campo (pragas, doenças, deficiências)
- equipment_alert: Alertas de equipamentos (sensores, máquinas, telemetria)
- knowledge_query: Perguntas sobre conhecimento agrícola
- general: Outros assuntos

Responda APENAS com a categoria, sem explicações."""
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        intent = response.choices[0].message.content.strip().lower()
        return intent
    
    except Exception as e:
        logging.error(f"Error classifying intent: {e}")
        return "general"


def generate_response(message: str, intent: str) -> str:
    """
    Gera resposta para a mensagem
    
    Args:
        message: Mensagem do usuário
        intent: Intenção classificada
        
    Returns:
        Resposta gerada
    """
    if not client:
        # Fallback para respostas mockadas
        responses = {
            "field_diagnosis": "Analisei a situação e parece ser um problema de campo. Estou criando um ticket e notificando o agrônomo.",
            "equipment_alert": "Detectei um alerta de equipamento. Verificando os dados de telemetria...",
            "knowledge_query": "Vou buscar essa informação na base de conhecimento.",
            "general": f"Recebi sua mensagem: '{message}'. Como posso ajudar?"
        }
        return responses.get(intent, responses["general"])
    
    try:
        system_prompt = """Você é um assistente agrícola inteligente chamado AgroBrain.
        
Você ajuda agricultores e técnicos com:
- Diagnóstico de problemas no campo
- Alertas de equipamentos
- Consultas sobre conhecimento agrícola
- Automação de processos

Seja conciso, técnico e prestativo. Use linguagem profissional mas acessível."""
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Intenção: {intent}\nMensagem: {message}"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."


def determine_agent(intent: str) -> str:
    """
    Determina qual agente deve processar a mensagem
    
    Args:
        intent: Intenção classificada
        
    Returns:
        Nome do agente
    """
    agent_mapping = {
        "field_diagnosis": "FieldSense",
        "equipment_alert": "FarmOps",
        "knowledge_query": "AgroBrain",
        "general": "FieldSense"
    }
    
    return agent_mapping.get(intent, "FieldSense")

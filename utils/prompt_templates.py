from langchain.prompts import PromptTemplate
from typing import Dict, List

class PromptTemplateManager:
    """
    Gestionnaire de templates de prompts optimisés pour différents cas d'usage
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialise les différents templates de prompts"""
        
        templates = {}
        
        # Template général (par défaut)
        templates['general'] = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""Tu es un assistant IA spécialisé dans l'analyse de documents. 
Réponds aux questions en te basant UNIQUEMENT sur le contexte fourni.

Contexte des documents:
{context}

Historique de la conversation:
{chat_history}

Question: {question}

Instructions:
- Réponds de manière précise et concise
- Si l'information n'est pas dans le contexte, dis clairement "Je ne trouve pas cette information dans le document fourni"
- Cite des passages spécifiques quand c'est pertinent
- Reste factuel et objectif

Réponse:"""
        )
        
        # Template pour documents académiques
        templates['academic'] = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""Tu es un assistant de recherche académique spécialisé dans l'analyse de publications scientifiques.
Analyse le contexte fourni pour répondre à la question de manière rigoureuse.

Contexte du document académique:
{context}

Historique de la conversation:
{chat_history}

Question: {question}

Instructions:
- Fournis une réponse académique rigoureuse
- Cite les auteurs et sections spécifiques si mentionnés
- Distingue clairement les faits des hypothèses
- Si des données ou statistiques sont présentes, inclus-les dans ta réponse
- Indique les limites de l'information disponible
- Si l'information n'est pas dans le document, dis "Cette information n'est pas présente dans le document analysé"

Réponse académique:"""
        )
        
        # Template pour documents techniques
        templates['technical'] = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""Tu es un assistant technique expert en documentation et manuels.
Analyse la documentation technique pour fournir une réponse précise et applicable.

Documentation technique:
{context}

Historique de la conversation:
{chat_history}

Question technique: {question}

Instructions:
- Fournis une réponse technique précise et actionnable
- Inclus les étapes, commandes ou configurations si pertinentes
- Mentionne les prérequis ou limitations
- Utilise la terminologie technique appropriée
- Si des exemples de code sont présents, inclus-les
- Si l'information technique n'est pas disponible, dis "Cette information technique n'est pas documentée dans ce manuel"

Réponse technique:"""
        )
        
        # Template pour documents légaux
        templates['legal'] = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""Tu es un assistant spécialisé dans l'analyse de documents juridiques.
Analyse le texte légal pour répondre de manière précise et structurée.

Texte légal:
{context}

Historique de la conversation:
{chat_history}

Question juridique: {question}

Instructions:
- Fournis une réponse structurée et précise
- Cite les articles, clauses ou sections spécifiques
- Respecte la terminologie juridique
- Distingue les obligations, droits et procédures
- Ne fournis pas de conseil juridique, seulement l'analyse du texte
- Si l'information n'est pas dans le document, dis "Cette disposition n'est pas couverte dans ce texte"

Analyse juridique:"""
        )
        
        # Template pour résumé
        templates['summary'] = PromptTemplate(
            input_variables=["context"],
            template="""Tu dois créer un résumé structuré et complet du document fourni.

Contenu du document:
{context}

Instructions:
- Crée un résumé structuré avec des sections claires
- Inclus les points clés et informations importantes
- Utilise des puces pour les listes d'éléments
- Maintiens l'objectivité et la précision
- Indique s'il s'agit d'un résumé partiel si le document semble incomplet

Structure suggérée:
## Résumé du document

### Points principaux
- [Point 1]
- [Point 2]
- [etc.]

### Informations clés
- [Information 1]
- [Information 2]
- [etc.]

### Conclusion
[Synthèse globale]

Résumé:"""
        )
        
        # Template pour extraction d'informations spécifiques
        templates['extraction'] = PromptTemplate(
            input_variables=["context", "question"],
            template="""Tu dois extraire des informations spécifiques du document selon la demande.

Document:
{context}

Demande d'extraction: {question}

Instructions:
- Extrais UNIQUEMENT les informations demandées
- Présente les résultats de manière structurée
- Si l'information n'est pas présente, indique "Information non trouvée"
- Utilise des listes ou tableaux si approprié
- Reste fidèle au texte original sans interpréter

Extraction:"""
        )
        
        return templates
    
    def get_template(self, template_type: str = 'general') -> PromptTemplate:
        """
        Retourne le template demandé
        """
        return self.templates.get(template_type, self.templates['general'])
    
    def get_available_templates(self) -> List[str]:
        """
        Retourne la liste des templates disponibles
        """
        return list(self.templates.keys())
    
    def create_custom_template(self, 
                             template_name: str,
                             template_content: str,
                             input_variables: List[str]) -> None:
        """
        Ajoute un template personnalisé
        """
        self.templates[template_name] = PromptTemplate(
            input_variables=input_variables,
            template=template_content
        )
    
    def get_optimized_template(self, document_type: str, query_type: str = 'general') -> PromptTemplate:
        """
        Retourne le template le mieux adapté selon le type de document et de requête
        """
        # Logique de sélection du template optimal
        if query_type == 'summary':
            return self.get_template('summary')
        elif query_type == 'extraction':
            return self.get_template('extraction')
        elif document_type in ['academic', 'technical', 'legal']:
            return self.get_template(document_type)
        else:
            return self.get_template('general')
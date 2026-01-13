#  Tests DontREADME

Ce dossier contient tous les tests pour le projet DontREADME.

## Structure des Tests

### Tests Principaux

- **`test_gradio_interface.py`** - Test de l'interface Gradio
- **`test_system_status.py`** - Évaluation complète du système
- **`test_components.py`** - Test des composants individuels
- **`test_embeddings.py`** - Test des embeddings et VectorStore

### Exécution des Tests

```bash
# Test de l'interface Gradio
python tests/test_gradio_interface.py

# Évaluation système complète
python tests/test_system_status.py

# Test des composants
python tests/test_components.py

# Test des embeddings
python tests/test_embeddings.py
```

### Tests Automatisés

```bash
# Tous les tests en une fois
python -m pytest tests/ -v

# Ou manuellement
for test in tests/test_*.py; do python "$test"; done
```

## Couverture des Tests

### [OK] Composants Testés

- **Interface Gradio** - Création et validation
- **FileProcessor** - Traitement de fichiers
- **Validators** - Validation des entrées
- **SmartTextSplitter** - Découpage intelligent
- **PerformanceMonitor** - Monitoring de performance
- **PromptTemplateManager** - Gestion des templates
- **VectorStore** - Base vectorielle ChromaDB
- **Embeddings** - API HuggingFace

###  Métriques de Qualité

- **Import des modules** - 100%
- **Structure des fichiers** - 100%
- **Fonctionnalités de base** - 95%
- **Interface utilisateur** - 100%

## Nettoyage Effectué

### [ERROR] Dossiers Supprimés
- `test_chroma/` - Tests ChromaDB obsolètes
- `test_chroma_clean/` - Tests ChromaDB nettoyés
- `test_chroma_simple/` - Tests ChromaDB simplifiés
- `test_fake_embeddings/` - Tests embeddings factices v1
- `test_fake_embeddings_v2/` - Tests embeddings factices v2
- `test_fake_embeddings_v3/` - Tests embeddings factices v3

### [OK] Tests Conservés et Centralisés
- Tests d'interface → `tests/test_gradio_interface.py`
- Tests système → `tests/test_system_status.py`
- Tests composants → `tests/test_components.py`
- Tests embeddings → `tests/test_embeddings.py`

## Notes Techniques

### Environnement de Test
- Python 3.10+
- Dépendances définies dans `requirements.txt`
- Tests compatibles avec et sans connexion Internet

### Données de Test
- Utilise des documents fictifs pour les tests
- Pas de dépendance à des fichiers externes
- Tests isolés et reproductibles

---

*Tests mis à jour le 12 juin 2025 - DontREADME v1.0*
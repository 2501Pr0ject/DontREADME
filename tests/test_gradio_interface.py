#!/usr/bin/env python3
"""
Test de l'interface Gradio sans instanciation complète
"""

import os
print("🧪 Test de l'interface Gradio DontREADME")
print("=" * 45)

# Créer les répertoires nécessaires
os.makedirs("./data/uploads", exist_ok=True)
os.makedirs("./data/vectorstore", exist_ok=True)

try:
    print("📦 Import de l'interface...")
    from app.main import create_enhanced_interface
    print("✅ Interface importée avec succès")
    
    print("🎨 Création de l'interface Gradio...")
    interface = create_enhanced_interface()
    print("✅ Interface créée avec succès")
    
    print(f"📊 Type d'interface: {type(interface)}")
    
    # Test si nous pouvons accéder aux composants
    if hasattr(interface, 'blocks'):
        print("✅ Interface Gradio valide avec blocks")
    else:
        print("⚠️ Interface créée mais structure inconnue")
    
    print("\n🎯 RÉSULTAT: Interface Gradio prête!")
    print("   Pour démarrer: interface.launch()")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Test terminé!")
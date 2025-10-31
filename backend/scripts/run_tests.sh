#!/bin/bash

echo "🧪 Exécution des tests unitaires..."

# Installer les dépendances de test
pip install -e .[test]

# Exécuter les tests avec couverture
pytest tests/ -v --cov=app --cov-report=html

echo "✅ Tests terminés!"
echo "📊 Rapport de couverture: file://$(pwd)/htmlcov/index.html"
# DEBT.md - Technical Debt Tracker

> **"Ne vivez pas avec des fenêtres brisées"**  
> Ce fichier suit la dette technique du projet pour éviter son accumulation.

---

## 🟡 Dette Mineure (Non-bloquante)

### STATIC-001: Pas de collectstatic configuré

- **Description:** Pour le moment, on sert les static files en mode dev sans collectstatic
- **Impact:** Faible en dev, mais nécessaire pour la prod
- **Solution:** Configurer STATIC_ROOT et ajouter collectstatic au workflow de déploiement
- **Date:** 2026-02-02

### TEST-001: Pas de tests unitaires

- **Description:** Aucun test n'a été écrit pour les modèles et vues
- **Impact:** Risque de régression lors des modifications futures
- **Solution:** Créer tests.py dans chaque app avec coverage minimale
- **Date:** 2026-02-02

---

## 🟢 Dette Résolue

***(Aucune pour le moment)**

---

## 📝 Notes

- Ajoutez une nouvelle entrée dès qu'un problème est identifié
- Marquez comme résolu avec la date de résolution
- Ne laissez pas la dette s'accumuler sans documentation

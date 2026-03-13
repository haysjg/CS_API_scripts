# Export Devices & Policies - Version 2.0

## 📋 Résumé

Le script `export_devices_policies.py` a été transformé d'un simple exporteur CSV en un **outil d'analyse et d'audit** complet avec export Excel, filtres intelligents, et détection automatique d'anomalies.

---

## ✅ Fonctionnalité 1: Export Multi-Format avec Excel

### Problème résolu
Le format CSV était difficile à exploiter pour les analyses complexes et ne permettait pas de présentation professionnelle.

### Solution implémentée
Export Excel avec plusieurs feuilles formatées :

#### Feuille "Summary"
- Vue d'ensemble de tous les CIDs
- Nombre de devices par CID
- Nombre d'anomalies par CID
- **Codage couleur sur le statut** :
  - 🟢 Vert : Aucune anomalie
  - 🟡 Jaune : Anomalies mineures (<10%)
  - 🔴 Rouge : Problèmes détectés

#### Feuilles par CID
- Une feuille par CID exporté
- **Auto-filters** sur toutes les colonnes
- **Freeze panes** (première ligne figée)
- **Codage couleur des politiques** :
  - 🟢 Vert : Applied
  - 🟡 Jaune : Assigned (en attente)
  - 🔴 Rouge : None
- **Colonnes auto-dimensionnées**

#### Feuille "Anomalies"
- Liste consolidée de toutes les anomalies détectées
- Organisée par CID et type d'anomalie
- Fond jaune pour visibilité

### Utilisation
```bash
# Excel par défaut
python export_devices_policies.py --config ../../config/credentials.json

# CSV uniquement
python export_devices_policies.py --config ../../config/credentials.json --format csv

# Les deux formats
python export_devices_policies.py --config ../../config/credentials.json --format both
```

---

## ✅ Fonctionnalité 2: Filtres de Sélection de Devices

### Problème résolu
Export massif de tous les devices, même ceux non pertinents, créant des fichiers énormes et difficiles à analyser.

### Solution implémentée
Système de filtres flexible pour cibler les exports :

#### Filtre par plateforme
```bash
--filter-platform "Windows,Linux,Mac"
```
Exporte uniquement les devices de la/les plateformes spécifiées.

#### Filtre par statut
```bash
--filter-status "normal,containment"
```
Exporte uniquement les devices avec le statut spécifié.

#### Filtre par host group
```bash
--filter-groups "Production,Critical"
```
Exporte uniquement les devices appartenant à des groupes contenant ces mots (match partiel).

#### Filtre par fraîcheur
```bash
--stale-threshold 30
```
Exclut les devices non vus depuis plus de X jours.

#### Combinaison de filtres
```bash
python export_devices_policies.py \
  --config ../../config/credentials.json \
  --filter-platform Windows \
  --filter-status normal \
  --filter-groups Production \
  --stale-threshold 90 \
  --format excel
```

### Implémentation technique
```python
class DeviceFilters:
    def __init__(self, platforms=None, statuses=None, groups=None, stale_days=None):
        # Configuration des filtres

    def should_include(self, device, host_groups) -> bool:
        # Vérifie si le device passe tous les filtres
```

### Avantages
- ✅ Réduit la taille des exports (ex: 10,000 → 2,000 devices)
- ✅ Accélère l'analyse (moins de données à traiter)
- ✅ Exports ciblés (ex: "Tous les Windows en production")
- ✅ Exclut automatiquement les devices obsolètes

---

## ✅ Fonctionnalité 3: Statistiques & Détection d'Anomalies

### Problème résolu
Impossible d'avoir une vue d'ensemble rapide ou d'identifier les problèmes de configuration sans analyse manuelle.

### Solution implémentée

#### Statistiques affichées en console
```
STATISTICS & ANOMALIES
================================================================================

Total Devices: 412

Platform Distribution:
  Windows              [████████████████████████████████████████░░] 358 (86.9%)
  Linux                [██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  47 (11.4%)
  Mac                  [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   7 ( 1.7%)

Status Distribution:
  normal                389 (94.4%)
  offline                21 ( 5.1%)
  containment             2 ( 0.5%)

Top 10 Host Groups:
  Production Servers                                42
  Development Workstations                          38
  Database Cluster                                  25
```

#### Anomalies détectées automatiquement
1. **No Prevention Policy** : Devices sans politique de prévention
2. **No Response Policy** : Devices sans politique de réponse
3. **No Sensor Policy** : Devices sans politique de mise à jour
4. **Policy Not Applied** : Politiques assignées mais pas encore appliquées
5. **No Host Group** : Devices n'appartenant à aucun groupe
6. **Stale Devices** : Devices non vus depuis >30 jours

#### Affichage des anomalies
```
ANOMALIES DETECTED
================================================================================

Found 47 anomaly/anomalies

  ⚠ No Prevention Policy            12 device(s)
  ⚠ Policy Not Applied               8 device(s)
  ⚠ No Host Group                   15 device(s)
  ⚠ Stale Devices (>30 days)       12 device(s)
```

### Implémentation technique
```python
def detect_anomalies(devices, policies):
    """Détecte les anomalies de configuration"""
    anomalies = {
        'no_prevention_policy': [],
        'no_response_policy': [],
        'no_sensor_policy': [],
        'policy_not_applied': [],
        'no_host_group': [],
        'stale_devices': [],
    }
    # ... logique de détection
    return anomalies

def calculate_statistics(devices, host_groups, policies):
    """Calcule les statistiques avec Counter"""
    stats = {
        'total_devices': len(devices),
        'by_platform': Counter(),
        'by_status': Counter(),
        'by_host_group': Counter(),
        # ...
    }
    return stats
```

### Avantages
- ✅ **Identification proactive** des problèmes de configuration
- ✅ **Vue d'ensemble instantanée** de l'environnement
- ✅ **Audit automatisé** sans analyse manuelle
- ✅ **Export Excel** avec feuille Anomalies dédiée

---

## 🔧 Modifications Techniques

### Nouvelles classes et fonctions
```python
class DeviceFilters:
    """Configuration des filtres de devices"""

def detect_anomalies(devices, policies) -> Dict[str, List]:
    """Détection automatique d'anomalies"""

def calculate_statistics(devices, host_groups, policies) -> Dict:
    """Calcul des statistiques avec Counter"""

def print_statistics(stats, anomalies):
    """Affichage formaté en console"""

def export_to_excel(output_file, all_data, all_stats, all_anomalies):
    """Export Excel avec openpyxl et formatage"""
```

### Fonction modifiée
```python
def export_cid_to_csv(..., filters: Optional[DeviceFilters] = None):
    """Ajout du support des filtres"""
```

### Fonction main() refactorisée
- Support des nouveaux arguments CLI
- Création et application des filtres
- Calcul des statistiques par CID
- Détection d'anomalies par CID
- Fusion des stats globales
- Export multi-format

### Nouveaux arguments CLI
```bash
--format {csv,excel,both}        # Format de sortie (défaut: excel)
--filter-platform PLATFORMS      # Filtre par plateforme
--filter-status STATUSES         # Filtre par statut
--filter-groups GROUPS           # Filtre par host groups
--stale-threshold DAYS           # Exclut devices non vus depuis X jours
```

### Dépendances
- `openpyxl>=3.1.0` : Export Excel avec formatage
- `collections.Counter` : Statistiques efficaces

---

## 📊 Métriques d'Amélioration

| Aspect | Avant | Après |
|--------|-------|-------|
| **Formats** | CSV uniquement | CSV + Excel formaté |
| **Filtrage** | Aucun | 4 types de filtres combinables |
| **Analyse** | Manuelle | Automatique (stats + anomalies) |
| **Visualisation** | Texte brut | Excel avec couleurs + filtres |
| **Détection de problèmes** | Manuelle | Automatique (6 types d'anomalies) |
| **Présentation** | Basique | Professionnelle (Excel formaté) |

---

## 📈 Cas d'Usage Améliorés

### Avant v2.0
```bash
# Export basique
python export_devices_policies.py --config credentials.json

# Résultat : Un gros fichier CSV
# Analyse : Manuelle dans Excel
# Problèmes : Détectés manuellement
```

### Après v2.0

#### Export ciblé Windows Production
```bash
python export_devices_policies.py \
  --config credentials.json \
  --filter-platform Windows \
  --filter-groups Production \
  --format excel
```

**Résultat :**
- Excel avec feuilles par CID
- Statistiques affichées en console
- Anomalies détectées automatiquement
- Export réduit et ciblé

#### Audit de compliance
```bash
python export_devices_policies.py \
  --config credentials.json \
  --stale-threshold 30 \
  --format excel
```

**Résultat :**
- Exclusion des devices obsolètes
- Feuille "Anomalies" avec tous les problèmes
- Statistiques pour rapport de compliance

#### Export rapide pour analyse
```bash
python export_devices_policies.py \
  --config credentials.json \
  --filter-status normal \
  --non-interactive \
  --format excel
```

**Résultat :**
- Export rapide (devices actifs uniquement)
- Statistiques de distribution
- Prêt pour présentation

---

## 🎯 Impact

### Pour l'administrateur
- ✅ **Gain de temps** : Statistiques automatiques vs analyse manuelle
- ✅ **Meilleure visibilité** : Vue d'ensemble immédiate
- ✅ **Détection proactive** : Anomalies trouvées automatiquement
- ✅ **Exports ciblés** : Filtres réduisent la taille

### Pour l'équipe SOC
- ✅ **Audit facilité** : Feuille Anomalies dédiée
- ✅ **Rapports pro** : Excel formaté prêt à partager
- ✅ **Analyse rapide** : Statistiques visuelles

### Pour la compliance
- ✅ **Traçabilité** : Anomalies documentées
- ✅ **Audit régulier** : Export automatisé
- ✅ **Preuve de conformité** : Rapports formatés

---

## 🔄 Compatibilité

### Rétrocompatibilité
- ✅ Toutes les anciennes options fonctionnent
- ✅ CSV toujours disponible (`--format csv`)
- ✅ Comportement par défaut : Excel (au lieu de CSV)

### Migration depuis v1.0
```bash
# Avant (v1.0)
python export_devices_policies.py --config creds.json --output export.csv

# Équivalent v2.0 (CSV)
python export_devices_policies.py --config creds.json --output export.csv --format csv

# Recommandé v2.0 (Excel)
python export_devices_policies.py --config creds.json --output export.xlsx
```

---

## 📝 Documentation

### README mis à jour
- Section "What's New in v2.0"
- Documentation complète des filtres
- Exemples d'utilisation Excel
- Explication des anomalies

### Exemples ajoutés
- Export ciblé par plateforme
- Audit de compliance
- Détection de problèmes

---

## ✨ Conclusion

Le script `export_devices_policies` est passé d'un **simple exporteur CSV** à un **outil d'analyse et d'audit complet** avec :

1. **Export professionnel** : Excel formaté avec couleurs et filtres
2. **Filtrage intelligent** : Exports ciblés et réduits
3. **Analyse automatique** : Statistiques + détection d'anomalies

**Valeur ajoutée immédiate :**
- Identification proactive des problèmes de configuration
- Exports plus petits et plus rapides
- Présentation professionnelle pour reporting

---

Date d'implémentation : 2026-03-13
Version : 2.0 (Enhanced Edition)
Commit : 54a13e9

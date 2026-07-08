# ATLAS VICE — Business Plan (v1)

> Compagnon interactif pour mondes ouverts : cartes, trackers et planificateurs
> pour Los Santos (GTA V) aujourd'hui, Leonida (GTA VI) demain.
> **Projet fan, indépendant, non affilié à Rockstar Games / Take-Two Interactive.**

---

## 1. Le problème

Finir un GTA à 100 % aujourd'hui, c'est jongler entre un wiki à onglets, trois
vidéos YouTube, une carte communautaire de 2014 et un carnet de notes. Les
outils existants sont :

- **éclatés** — un site pour les collectibles, un autre pour les braquages ;
- **moches et lents** — publicité intrusive, pas de mobile, pas de sync ;
- **sans progression** — aucun ne retient où vous en êtes.

Au lancement de GTA VI, des dizaines de millions de joueurs vont refaire
exactement ce parcours du combattant, sur une carte annoncée comme la plus
grande de l'histoire de la série.

## 2. La solution

Un seul produit, trois usages :

| Usage | Ce qu'on offre |
|---|---|
| **Explorer** | Cartes vectorielles « néon blueprint » originales, filtres, recherche, fiches sourcées |
| **Progresser** | Trackers de collectibles synchronisés, itinéraires optimisés, mode sans spoiler |
| **Jouer à plusieurs** | Planificateur de braquages partagé, progression de crew, overlay streamer |

Positionnement : **le Strava du monde ouvert** — l'outil que l'on garde ouvert
sur second écran pendant qu'on joue.

## 3. Marché

- GTA V : plus de 200 M de copies vendues, communauté toujours active 12 ans après.
- GTA VI : lancement le plus attendu de l'histoire du jeu vidéo ; chaque trailer
  bat des records d'audience. La fenêtre « pré-lancement → 12 mois post-lancement »
  est le moment où la demande de guides explose (pic historique observé sur les
  wikis/soluces à chaque sortie Rockstar).
- Marché adjacent prouvé : les companion apps/map trackers tiers (ex. pour Zelda,
  Elden Ring, Genshin) génèrent des millions de visites mensuelles, monétisées
  par publicité — presque aucun n'a de vraie offre premium soignée. C'est le trou
  dans la raquette.

**Personas** : le complétionniste (25-40 ans, finit tout à 100 %), le crew leader
(joue en ligne à 4-5, organise), le streamer (veut du contenu d'écran propre).

## 4. Modèle de revenus

1. **Freemium B2C** (cœur) :
   - *Touriste* — gratuit : cartes + 200 lieux/monde. Acquisition et SEO.
   - *Vice Pass* — 4,99 €/mois ou 39 €/an : tout le contenu, trackers, itinéraires.
   - *Crew* — 9,99 €/mois : 5 sièges, planification partagée, overlay streamer.
2. **Founder packs** (pré-lancement GTA VI) : paiement unique 29 € = 1 an de Vice
   Pass + badge fondateur + vote sur la roadmap. Génère la trésorerie avant le pic.
3. **B2B léger** : widgets de carte embarquables pour créateurs de contenu et
   médias gaming (licence mensuelle), API de données de lieux.
4. **Pas de publicité** au lancement : c'est l'argument différenciant n°1 face
   aux map-sites existants.

**Hypothèses prudentes 12 mois post-lancement GTA VI** : 300 k visiteurs uniques/mois
(SEO + communauté), 1,5 % de conversion payante → ~4 500 abonnés → ~22 k€ MRR.
Le levier principal est le timing : être *déjà* la référence sur la carte Leonida
au jour J (d'où l'early access construit en public).

## 5. Aller au marché (GTM)

1. **Phase 1 — maintenant → sortie GTA VI** : la carte Leonida « early access »
   se construit en public à chaque trailer (contenu hautement partageable sur
   X/TikTok/Reddit : « on a cartographié le trailer 2 image par image »). SEO sur
   les requêtes « carte GTA 5 collectibles », « map GTA 6 Leonida ».
2. **Phase 2 — jour J** : couverture de lancement en continu, founder packs,
   partenariats avec 10-15 streamers FR/EN (overlay gratuit contre visibilité).
3. **Phase 3 — 6 mois+** : extension multi-jeux (le moteur est générique) pour
   lisser la saisonnalité : Red Dead, Cyberpunk, Elden Ring.

## 6. Réalité juridique (à traiter sérieusement)

- Les **faits ne sont pas protégeables** (noms de lieux, positions) mais les
  **assets du jeu le sont** : nos cartes sont des créations vectorielles
  originales stylisées, aucun asset extrait des jeux, aucune capture d'écran
  monétisée.
- Respect des guidelines fan content de Take-Two : mention « non affilié »
  systématique, pas d'usage des logos officiels, marque propre (« Atlas Vice »
  ne reprend pas « GTA » dans le nom).
- **Risque principal** : durcissement de la politique IP autour du lancement
  GTA VI. Mitigation : (a) le moteur et la marque sont indépendants du contenu
  GTA — pivot multi-jeux possible en semaines ; (b) canal de contact proactif
  avec Take-Two si le produit décolle ; (c) le contenu communautaire est sourcé
  et retirable par item.

## 7. Roadmap produit

| Trimestre | Jalon |
|---|---|
| T1 | MVP web (fait) : 2 cartes, filtres, fiches, offre 3 plans |
| T2 | Comptes + trackers synchronisés, mode sans spoiler, founder packs |
| T3 | Contribution communautaire (soumission + modération), app mobile PWA |
| Sortie GTA VI | Carte Leonida jour J, overlay OBS, couverture en continu |
| +6 mois | API/widgets B2B, 3ᵉ monde ouvert, offre annuelle |

## 8. KPIs

- Visiteurs uniques/mois, part SEO vs communauté
- Taux d'inscription (compte gratuit) et conversion → Vice Pass (cible 1,5-3 %)
- Rétention M1/M3 des abonnés (cible > 70 % / > 50 %)
- Lieux vérifiés sur la carte Leonida avant le jour J (cible : 300+)
- MRR, churn mensuel (< 8 %)

## 9. Prochaines actions concrètes

1. Déployer le MVP sur un domaine (Netlify/Vercel, coût ~0).
2. Poster la carte Leonida early access sur r/GTA6 + X avec le breakdown du trailer.
3. Mettre en place la liste d'attente e-mail (founder pack) dès 1 000 visites/jour.
4. Implémenter les comptes + trackers (T2) — première brique réellement payante.

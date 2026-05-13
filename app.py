"""
DIAT — Diagnostic d'Inspection et d'Audit de Terrain
Application Web — Streamlit
Mode lecture seule pour visiteurs / mode admin avec mot de passe
"""
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import streamlit as st
import json
import os
import datetime
import hashlib
from pathlib import Path

st.set_page_config(
    page_title="DIAT — Inspection & Audit",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR  = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "chantiers.json"
IMG_DIR   = BASE_DIR / "images"
for d in [BASE_DIR / "data", IMG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Mot de passe admin (hash SHA256) ────────────────────────────────────────
# Pour changer le mot de passe : python3 -c "import hashlib; print(hashlib.sha256(b'VotreMotDePasse').hexdigest())"
MOT_DE_PASSE_HASH = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
# ↑ correspond au mot de passe : "123"  — changez-le avant de déployer !

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --accent:#00c8aa; --accent2:#0096ff; --bg-card:#1e2d40;
    --bg-panel:#172030; --border:#2a3f58; --danger:#ff4d6d;
    --warning:#ffb347; --success:#00c8aa; --text-sub:#7a9bbf;
}
.card { background:var(--bg-card); border:1px solid var(--border);
        border-radius:12px; padding:16px 20px; margin-bottom:12px; }
.card:hover { border-color:var(--accent); }
.badge { display:inline-block; padding:3px 10px; border-radius:20px;
         font-size:12px; font-weight:600; }
.badge-bon      { background:#0d3d2e; color:#00c8aa; }
.badge-moyen    { background:#3d2b0d; color:#ffb347; }
.badge-mauvais  { background:#3d0d1a; color:#ff4d6d; }
.badge-encours  { background:#0d2d3d; color:#0096ff; }
.badge-termine  { background:#0d3d2e; color:#00c8aa; }
.badge-suspendu { background:#3d2b0d; color:#ffb347; }
.badge-nondmarre{ background:#2a2a2a; color:#888; }
.badge-ro       { background:#1a1a2e; color:#7a9bbf; font-size:11px; padding:2px 8px; }
.info-row { display:flex; gap:28px; flex-wrap:wrap;
            background:var(--bg-card); border-radius:10px;
            padding:14px 18px; margin-bottom:12px;
            border:1px solid var(--border); }
.info-item label { font-size:11px; color:var(--text-sub); display:block; }
.info-item span  { font-size:14px; }
.metric-card { background:var(--bg-card); border:1px solid var(--border);
               border-radius:12px; padding:20px; text-align:center; }
.metric-value { font-size:2.4em; font-weight:700; color:var(--accent); line-height:1.1; }
.metric-label { font-size:0.85em; color:var(--text-sub); margin-top:4px; }
.progress-bar-bg   { background:var(--border); border-radius:4px; height:8px;
                     width:100%; overflow:hidden; margin:4px 0; }
.progress-bar-fill { height:100%; border-radius:4px; }
.readonly-banner { background:#1a1a2e; border:1px solid #2a3f58;
                   border-radius:10px; padding:10px 18px; margin-bottom:16px;
                   color:#7a9bbf; font-size:13px; }
section[data-testid="stSidebar"] { background:var(--bg-panel) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════

def check_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest() == MOT_DE_PASSE_HASH

def est_admin():
    return st.session_state.get("admin", False)

def login_sidebar():
    """Panneau de connexion admin dans la sidebar."""
    with st.sidebar.expander("🔒 Connexion admin", expanded=False):
        if est_admin():
            st.success("Connecté en mode admin")
            if st.button("Se déconnecter", use_container_width=True):
                st.session_state.admin = False
                st.rerun()
        else:
            pwd = st.text_input("Mot de passe", type="password", key="pwd_input")
            if st.button("Connexion", use_container_width=True, type="primary"):
                if check_password(pwd):
                    st.session_state.admin = True
                    st.success("Connecté ✓")
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")

def bandeau_lecture_seule():
    if not est_admin():
        st.markdown("""
        <div class="readonly-banner">
            👁 <strong>Mode consultation</strong> — Vous visualisez les données en lecture seule.
            Les modifications sont réservées à l'administrateur.
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DONNÉES
# ═══════════════════════════════════════════════════════════════

def charger():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"chantiers": []}

def sauvegarder(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_data():
    if "data" not in st.session_state:
        st.session_state.data = charger()
    return st.session_state.data

def save_data():
    sauvegarder(st.session_state.data)

def nouveau_id(p="ID"):
    return f"{p}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def badge_statut(s):
    cls = {"En cours":"encours","Terminé":"termine",
           "Suspendu":"suspendu","Non démarré":"nondmarre"}.get(s,"nondmarre")
    return f'<span class="badge badge-{cls}">{s}</span>'

def badge_etat(e):
    cls = {"Bon":"bon","Moyen":"moyen","Mauvais":"mauvais"}.get(e,"moyen")
    return f'<span class="badge badge-{cls}">{e}</span>'

# ═══════════════════════════════════════════════════════════════
# PAGE DASHBOARD
# ═══════════════════════════════════════════════════════════════

def page_dashboard():
    data = get_data()
    chantiers = data.get("chantiers", [])
    bandeau_lecture_seule()
    st.title("📊 Tableau de bord")
    st.caption(f"Mis à jour le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    st.markdown("---")

    total_v = sum(len(c.get("visites",[])) for c in chantiers)
    total_i = sum(len(v.get("images",[])) for c in chantiers for v in c.get("visites",[]))
    notes   = [float(v["note"]) for c in chantiers for v in c.get("visites",[])
               if v.get("note","").replace(".","",1).isdigit()]
    moy = f"{sum(notes)/len(notes):.1f}" if notes else "—"

    c1,c2,c3,c4 = st.columns(4)
    for col,icon,val,label,color in [
        (c1,"🏗",len(chantiers),"Chantiers","#00c8aa"),
        (c2,"🔍",total_v,"Visites","#0096ff"),
        (c3,"🖼",total_i,"Images","#ffb347"),
        (c4,"⭐",moy,"Note moyenne","#00c8aa"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size:2em">{icon}</div>
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([1,2])

    with cl:
        st.subheader("Répartition par statut")
        statuts = {}
        for c in chantiers:
            s = c.get("statut","Inconnu"); statuts[s] = statuts.get(s,0)+1
        colors = {"En cours":"#0096ff","Terminé":"#00c8aa",
                  "Suspendu":"#ffb347","Non démarré":"#7a9bbf"}
        for s,n in statuts.items():
            pct = int(n/len(chantiers)*100) if chantiers else 0
            col = colors.get(s,"#7a9bbf")
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;font-size:13px">
                    <span>{s}</span><span style="color:{col}">{n}</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{pct}%;background:{col}"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with cr:
        st.subheader("Dernières visites")
        all_v = [(c.get("nom",""),v) for c in chantiers for v in c.get("visites",[])]
        all_v.sort(key=lambda x: x[1].get("date",""), reverse=True)
        if not all_v:
            st.info("Aucune visite enregistrée.")
        for nom_c,v in all_v[:8]:
            nb_i = len(v.get("images",[]))
            st.markdown(f"""
            <div class="card" style="padding:10px 16px;margin-bottom:8px">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                    <span style="font-weight:600">📅 {v.get('date','—')}</span>
                    <span style="color:#7a9bbf;font-size:13px">{nom_c[:40]}</span>
                    {badge_etat(v.get('etat','—'))}
                    <span style="color:#7a9bbf;font-size:12px">👷 {v.get('inspecteur','—')}</span>
                    {"<span style='color:#0096ff;font-size:12px;margin-left:auto'>🖼 "+str(nb_i)+"</span>" if nb_i else ""}
                </div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE CHANTIERS
# ═══════════════════════════════════════════════════════════════

def page_chantiers():
    data = get_data()
    bandeau_lecture_seule()
    st.title("🏗 Chantiers")

    col_s, col_b = st.columns([3,1])
    with col_s:
        rech = st.text_input("🔍", placeholder="Rechercher…", label_visibility="collapsed")
    with col_b:
        if est_admin():
            if st.button("➕ Nouveau chantier", use_container_width=True, type="primary"):
                st.session_state.modal = "nouveau_chantier"
                st.session_state.chantier_edit = None

    st.markdown("---")
    chantiers = data.get("chantiers",[])
    filtres = [c for c in chantiers if
               rech.lower() in c.get("nom","").lower() or
               rech.lower() in c.get("localisation","").lower() or
               rech.lower() in c.get("entreprise","").lower()] if rech else chantiers

    if not filtres:
        st.info("Aucun chantier trouvé.")
        return

    for c in filtres:
        nb_v = len(c.get("visites",[]))
        nb_i = sum(len(v.get("images",[])) for v in c.get("visites",[]))
        st.markdown(f"""
        <div class="card">
            <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                <span style="font-size:1.1em;font-weight:700">{c.get('nom','—')}</span>
                {badge_statut(c.get('statut','—'))}
            </div>
            <div class="info-row" style="margin-top:10px">
                <div class="info-item"><label>📍 Localisation</label><span>{c.get('localisation','—')}</span></div>
                <div class="info-item"><label>🏢 Entreprise</label><span>{c.get('entreprise','—') or '—'}</span></div>
                <div class="info-item"><label>👷 Responsable</label><span>{c.get('responsable','—') or '—'}</span></div>
                <div class="info-item"><label>📅 Début</label><span>{c.get('date_debut','—') or '—'}</span></div>
                <div class="info-item"><label>🔍 Visites</label><span style="color:#0096ff;font-weight:600">{nb_v}</span></div>
                <div class="info-item"><label>🖼 Images</label><span style="color:#ffb347;font-weight:600">{nb_i}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if est_admin():
            bc1,bc2,bc3 = st.columns([2,1,1])
            with bc1:
                if st.button(f"📂 Ouvrir", key=f"open_{c['id']}", use_container_width=True):
                    st.session_state.chantier_actif = c["id"]
                    st.session_state.page = "detail"; st.rerun()
            with bc2:
                if st.button("✏ Modifier", key=f"mod_{c['id']}", use_container_width=True):
                    st.session_state.modal = "edit_chantier"
                    st.session_state.chantier_edit = c["id"]; st.rerun()
            with bc3:
                if st.button("🗑 Supprimer", key=f"del_{c['id']}", use_container_width=True):
                    st.session_state.modal = "confirm_del_chantier"
                    st.session_state.chantier_edit = c["id"]; st.rerun()
        else:
            if st.button(f"📂 Voir le détail", key=f"open_{c['id']}", use_container_width=False):
                st.session_state.chantier_actif = c["id"]
                st.session_state.page = "detail"; st.rerun()

    # ── Formulaires admin uniquement ──────────────────────────────────────────
    if not est_admin(): return
    modal = st.session_state.get("modal")

    if modal in ("nouveau_chantier","edit_chantier"):
        cid    = st.session_state.get("chantier_edit")
        edit_c = next((c for c in chantiers if c["id"]==cid),{}) if cid else {}
        titre  = "Modifier le chantier" if edit_c else "Nouveau chantier"
        with st.expander(f"📝 {titre}", expanded=True):
            with st.form("form_ch"):
                nom    = st.text_input("Nom du chantier *",    value=edit_c.get("nom",""))
                loc    = st.text_input("Localisation *",       value=edit_c.get("localisation",""))
                entr   = st.text_input("Entreprise",           value=edit_c.get("entreprise",""))
                resp   = st.text_input("Responsable",          value=edit_c.get("responsable",""))
                trav   = st.text_input("Type de travaux",      value=edit_c.get("type_travaux",""))
                grp    = st.text_input("Groupe / Site",        value=edit_c.get("groupe",""))
                col1,col2 = st.columns(2)
                dd     = col1.text_input("Date début",         value=edit_c.get("date_debut",""))
                df     = col2.text_input("Date fin prévue",    value=edit_c.get("date_fin",""))
                statut = st.selectbox("Statut *",
                    ["En cours","Terminé","Suspendu","Non démarré"],
                    index=["En cours","Terminé","Suspendu","Non démarré"].index(
                        edit_c.get("statut","Non démarré") if edit_c.get("statut","Non démarré")
                        in ["En cours","Terminé","Suspendu","Non démarré"] else "Non démarré"))
                obs    = st.text_area("Observations", value=edit_c.get("observations",""), height=80)
                ok,ann = st.columns(2)
                submit = ok.form_submit_button("✔ Enregistrer", type="primary", use_container_width=True)
                annul  = ann.form_submit_button("Annuler", use_container_width=True)
            if submit:
                if not nom.strip() or not loc.strip():
                    st.error("Nom et Localisation sont obligatoires.")
                else:
                    obj = {"nom":nom,"localisation":loc,"entreprise":entr,
                           "responsable":resp,"type_travaux":trav,"groupe":grp,
                           "date_debut":dd,"date_fin":df,"statut":statut,"observations":obs}
                    if edit_c:
                        for c in data["chantiers"]:
                            if c["id"]==edit_c["id"]: c.update(obj)
                    else:
                        obj.update({"id":nouveau_id("CH"),"visites":[]})
                        data["chantiers"].append(obj)
                    save_data(); st.session_state.modal=None
                    st.success("Enregistré ✓"); st.rerun()
            if annul: st.session_state.modal=None; st.rerun()

    if modal=="confirm_del_chantier":
        cid = st.session_state.get("chantier_edit")
        ch  = next((c for c in chantiers if c["id"]==cid),None)
        if ch:
            with st.expander(f"⚠️ Supprimer « {ch['nom']} » ?", expanded=True):
                st.warning("Action irréversible — toutes les visites seront supprimées.")
                y,n = st.columns(2)
                if y.button("✔ Confirmer", type="primary", use_container_width=True):
                    data["chantiers"]=[c for c in data["chantiers"] if c["id"]!=cid]
                    save_data(); st.session_state.modal=None; st.rerun()
                if n.button("Annuler", use_container_width=True):
                    st.session_state.modal=None; st.rerun()

# ═══════════════════════════════════════════════════════════════
# PAGE DÉTAIL
# ═══════════════════════════════════════════════════════════════

def page_detail():
    data     = get_data()
    cid      = st.session_state.get("chantier_actif")
    chantier = next((c for c in data.get("chantiers",[]) if c["id"]==cid), None)
    if not chantier:
        st.error("Chantier introuvable.")
        if st.button("← Retour"): st.session_state.page="chantiers"; st.rerun()
        return

    bandeau_lecture_seule()
    if st.button("← Retour à la liste"): st.session_state.page="chantiers"; st.rerun()

    st.markdown(f"""
    <h1 style="margin-top:0">{chantier.get('nom','—')}
    <span style="margin-left:12px">{badge_statut(chantier.get('statut','—'))}</span></h1>""",
    unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-row">
        <div class="info-item"><label>📍 Localisation</label><span>{chantier.get('localisation','—')}</span></div>
        <div class="info-item"><label>🏢 Entreprise</label><span>{chantier.get('entreprise','—') or '—'}</span></div>
        <div class="info-item"><label>👷 Responsable</label><span>{chantier.get('responsable','—') or '—'}</span></div>
        <div class="info-item"><label>🔧 Travaux</label><span>{chantier.get('type_travaux','—') or '—'}</span></div>
        <div class="info-item"><label>📅 Début</label><span>{chantier.get('date_debut','—') or '—'}</span></div>
        <div class="info-item"><label>🏁 Fin prévue</label><span>{chantier.get('date_fin','—') or '—'}</span></div>
    </div>""", unsafe_allow_html=True)

    # Boutons admin
    if est_admin():
        ca, cb = st.columns(2)
        if ca.button("✏ Modifier ce chantier"):
            st.session_state.modal="edit_chantier"
            st.session_state.chantier_edit=chantier["id"]; st.rerun()
        if cb.button("🗑 Supprimer ce chantier"):
            st.session_state.modal="confirm_del_chantier"
            st.session_state.chantier_edit=chantier["id"]; st.rerun()

    tab_v, tab_i = st.tabs(["🔍 Visites d'inspection","🖼 Bibliothèque d'images"])

    # ── ONGLET VISITES ────────────────────────────────────────────────────────
    with tab_v:
        st.markdown("---")
        if est_admin():
            if st.button("➕ Nouvelle visite", type="primary"):
                st.session_state.modal="nouvelle_visite"
                st.session_state.visite_edit=None

        visites = sorted(chantier.get("visites",[]), key=lambda v: v.get("date",""), reverse=True)
        if not visites:
            st.info("Aucune visite." + (" Ajoutez-en une ci-dessus." if est_admin() else ""))
        for v in visites:
            nb_i = len(v.get("images",[]))
            obs  = v.get("observations","")
            st.markdown(f"""
            <div class="card">
                <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                    <span style="font-weight:700">📅 {v.get('date','—')}</span>
                    {badge_etat(v.get('etat','—'))}
                    <span style="color:#7a9bbf;font-size:13px">⭐ {v.get('note','—')}/10</span>
                    <span style="color:#7a9bbf;font-size:13px">👷 {v.get('inspecteur','—')}</span>
                    <span style="color:{'#0096ff' if nb_i else '#445566'};font-size:13px;margin-left:auto">🖼 {nb_i} image(s)</span>
                </div>
                {"<p style='margin:8px 0 0;color:#7a9bbf;font-size:13px'>"+obs[:160]+("…" if len(obs)>160 else "")+"</p>" if obs else ""}
            </div>""", unsafe_allow_html=True)

            if est_admin():
                bv1,bv2,bv3 = st.columns([2,1,1])
                with bv1:
                    if st.button(f"🖼 Images ({nb_i})", key=f"imgs_{v['id']}", use_container_width=True):
                        st.session_state.visite_images=v["id"]; st.rerun()
                with bv2:
                    if st.button("✏", key=f"modv_{v['id']}", use_container_width=True):
                        st.session_state.modal="edit_visite"
                        st.session_state.visite_edit=v["id"]; st.rerun()
                with bv3:
                    if st.button("🗑", key=f"delv_{v['id']}", use_container_width=True):
                        st.session_state.modal="confirm_del_visite"
                        st.session_state.visite_edit=v["id"]; st.rerun()
            else:
                if st.button(f"🖼 Voir images ({nb_i})", key=f"imgs_{v['id']}"):
                    st.session_state.visite_images=v["id"]; st.rerun()

        # Formulaires visite (admin)
        if est_admin():
            modal = st.session_state.get("modal")
            if modal in ("nouvelle_visite","edit_visite"):
                vid    = st.session_state.get("visite_edit")
                edit_v = next((v for v in chantier.get("visites",[]) if v["id"]==vid),{}) if vid else {}
                titre  = "Modifier la visite" if edit_v else "Nouvelle visite"
                with st.expander(f"📝 {titre}", expanded=True):
                    with st.form("form_v"):
                        co1,co2 = st.columns(2)
                        date_v  = co1.text_input("Date *  (JJ/MM/AAAA)",
                                    value=edit_v.get("date",datetime.date.today().strftime("%d/%m/%Y")))
                        insp    = co2.text_input("Inspecteur *", value=edit_v.get("inspecteur",""))
                        co3,co4 = st.columns(2)
                        etat_v  = co3.selectbox("État général *",["Bon","Moyen","Mauvais"],
                                    index=["Bon","Moyen","Mauvais"].index(edit_v.get("etat","Moyen")))
                        note_v  = co4.text_input("Note (/10)", value=edit_v.get("note",""))
                        obs_v   = st.text_area("Observations", value=edit_v.get("observations",""), height=120)
                        ok,ann  = st.columns(2)
                        submit  = ok.form_submit_button("✔ Enregistrer", type="primary", use_container_width=True)
                        annul   = ann.form_submit_button("Annuler", use_container_width=True)
                    if submit:
                        if not date_v.strip() or not insp.strip():
                            st.error("Date et Inspecteur sont obligatoires.")
                        else:
                            new_v = {"id":edit_v.get("id",nouveau_id("V")),
                                     "date":date_v,"inspecteur":insp,"etat":etat_v,
                                     "note":note_v,"observations":obs_v,
                                     "images":edit_v.get("images",[])}
                            if edit_v:
                                chantier["visites"]=[new_v if v["id"]==edit_v["id"] else v
                                                     for v in chantier["visites"]]
                            else:
                                chantier.setdefault("visites",[]).append(new_v)
                            save_data(); st.session_state.modal=None; st.rerun()
                    if annul: st.session_state.modal=None; st.rerun()

            if modal=="confirm_del_visite":
                vid = st.session_state.get("visite_edit")
                v   = next((v for v in chantier.get("visites",[]) if v["id"]==vid),None)
                if v:
                    with st.expander(f"⚠️ Supprimer la visite du {v.get('date','—')} ?", expanded=True):
                        y,n = st.columns(2)
                        if y.button("✔ Supprimer", type="primary", use_container_width=True):
                            chantier["visites"]=[x for x in chantier["visites"] if x["id"]!=vid]
                            save_data(); st.session_state.modal=None; st.rerun()
                        if n.button("Annuler", use_container_width=True):
                            st.session_state.modal=None; st.rerun()

    # ── ONGLET IMAGES ─────────────────────────────────────────────────────────
    with tab_i:
        st.markdown("---")
        visites = chantier.get("visites",[])
        if not visites:
            st.info("Créez d'abord une visite pour y ajouter des images.")
            return

        options = {f"📅 {v.get('date','—')} — {v.get('inspecteur','—')}": v["id"]
                   for v in sorted(visites, key=lambda x: x.get("date",""), reverse=True)}
        default_vid = st.session_state.get("visite_images")
        default_key = next((k for k,val in options.items() if val==default_vid),
                           list(options.keys())[0]) if default_vid else list(options.keys())[0]

        sel = st.selectbox("Sélectionner une visite", list(options.keys()),
                           index=list(options.keys()).index(default_key))
        vid    = options[sel]
        visite = next(v for v in visites if v["id"]==vid)

        st.markdown(f"""
        <div class="info-row">
            <div class="info-item"><label>📅 Date</label><span>{visite.get('date','—')}</span></div>
            <div class="info-item"><label>👷 Inspecteur</label><span>{visite.get('inspecteur','—')}</span></div>
            <div class="info-item"><label>État</label><span>{badge_etat(visite.get('etat','—'))}</span></div>
            <div class="info-item"><label>🖼 Images</label>
                <span style="color:#ffb347;font-weight:700">{len(visite.get('images',[]))}</span></div>
        </div>""", unsafe_allow_html=True)

        # Upload images (admin seulement)
        if est_admin():
            with st.expander("➕ Ajouter des images", expanded=False):
                uploaded = st.file_uploader("Choisir des photos",
                    type=["jpg","jpeg","png","bmp","gif","webp","tiff"],
                    accept_multiple_files=True, key=f"up_{vid}")
                if st.button("📤 Enregistrer", type="primary") and uploaded:
                    dossier = IMG_DIR / vid; dossier.mkdir(parents=True, exist_ok=True)
                    ajouts = []
                    for f in uploaded:
                        dest = dossier/f.name
                        stem,ext = os.path.splitext(f.name); k=1
                        while dest.exists(): dest=dossier/f"{stem}_{k}{ext}"; k+=1
                        with open(dest,"wb") as out: out.write(f.read())
                        ajouts.append(f"images/{vid}/{dest.name}")
                    visite.setdefault("images",[]).extend(ajouts)
                    save_data(); st.success(f"{len(ajouts)} image(s) ajoutée(s) ✓"); st.rerun()

        # Galerie
        imgs = visite.get("images",[])
        if not imgs:
            msg = "Aucune image pour cette visite."
            msg += " Ajoutez-en ci-dessus." if est_admin() else ""
            st.info(msg)
        else:
            st.markdown(f"**{len(imgs)} image(s)**")
            cols = st.columns(4)
            for idx,chemin in enumerate(imgs):
                path = BASE_DIR/chemin
                with cols[idx%4]:
                    if path.exists():
                        st.image(str(path), use_container_width=True, caption=Path(chemin).name)
                        if est_admin():
                            if st.button("🗑", key=f"dimg_{vid}_{idx}", use_container_width=True):
                                visite["images"].pop(idx); save_data(); st.rerun()
                    else:
                        st.markdown(f"<span style='color:#ff4d6d'>❌ Introuvable</span>",
                                    unsafe_allow_html=True)
            if est_admin():
                st.markdown("---")
                if st.button("🗑 Vider la galerie", type="secondary"):
                    visite["images"]=[]; save_data(); st.rerun()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR + MAIN
# ═══════════════════════════════════════════════════════════════

def sidebar():
    data = get_data()
    ch   = data.get("chantiers",[])
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 8px">
            <div style="font-size:2.2em;font-weight:800;color:#00c8aa">DIAT</div>
            <div style="font-size:11px;color:#7a9bbf;margin-top:2px">
                Diagnostic & Inspection<br>Audit de Terrain</div>
        </div>
        <hr style="border-color:#2a3f58;margin:8px 0 16px">""", unsafe_allow_html=True)

        # Badge rôle
        if est_admin():
            st.markdown('<span class="badge badge-encours">🔑 Admin</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-nondmarre">👁 Lecture seule</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        page = st.session_state.get("page","dashboard")
        if st.button("📊 Tableau de bord", use_container_width=True,
                     type="primary" if page=="dashboard" else "secondary"):
            st.session_state.page="dashboard"; st.rerun()
        if st.button("🏗 Chantiers", use_container_width=True,
                     type="primary" if page=="chantiers" else "secondary"):
            st.session_state.page="chantiers"; st.rerun()

        st.markdown("---"); st.caption("CHANTIERS")
        for c in ch:
            ico = "🟢" if c.get("statut")=="En cours" else "✅" if c.get("statut")=="Terminé" else "⏸"
            if st.button(f"{ico} {c.get('nom','—')[:30]}", key=f"sb_{c['id']}", use_container_width=True):
                st.session_state.chantier_actif=c["id"]
                st.session_state.page="detail"; st.rerun()

        st.markdown("---")
        tv = sum(len(c.get("visites",[])) for c in ch)
        ti = sum(len(v.get("images",[])) for c in ch for v in c.get("visites",[]))
        st.markdown(f"""
        <div style="padding:10px;background:#172030;border-radius:8px;
                    border:1px solid #2a3f58;font-size:12px;color:#7a9bbf">
            🏗 {len(ch)} chantier(s)<br>🔍 {tv} visite(s)<br>🖼 {ti} image(s)
        </div>""", unsafe_allow_html=True)

        # Connexion admin
        st.markdown("---")
        login_sidebar()

def main():
    if "page"  not in st.session_state: st.session_state.page  = "dashboard"
    if "modal" not in st.session_state: st.session_state.modal = None
    if "admin" not in st.session_state: st.session_state.admin = False
    sidebar()
    page = st.session_state.get("page","dashboard")
    if   page=="dashboard": page_dashboard()
    elif page=="chantiers": page_chantiers()
    elif page=="detail":    page_detail()
    else:                   page_dashboard()

if __name__=="__main__":
    main()

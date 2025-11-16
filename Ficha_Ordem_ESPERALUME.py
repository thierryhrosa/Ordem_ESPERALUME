# Ordo_Fichas_v7_Final.py
# Ordo Realitas — Sistema local de fichas (v7 final, com melhorias de D20 e Mestre)

import streamlit as st
import json, os, random
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Ordem ESPERALUME", page_icon="🔆", layout="centered")
DATA_DIR = "fichas"
LOG_PATH = "roll_log.json"
os.makedirs(DATA_DIR, exist_ok=True)
MASTER_PASSWORD = "ordo2025"

# ---------------- HELPERS ----------------
def ficha_path(name: str):
    return os.path.join(DATA_DIR, f"{name.lower()}.json")

def save_ficha(name: str, data: dict):
    with open(ficha_path(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_ficha(name: str):
    p = ficha_path(name)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def list_fichas():
    return sorted([fn.replace(".json", "") for fn in os.listdir(DATA_DIR) if fn.endswith(".json")])

def delete_ficha(name: str):
    p = ficha_path(name)
    if os.path.exists(p):
        os.remove(p)
        log = load_log()
        new = [e for e in log if e.get("who") != name]
        save_log(new)
        return True
    return False

def load_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_log(arr):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False, indent=4)

def append_log(entry):
    log = load_log()
    log.append(entry)
    save_log(log)
def clear_log():
    """Limpa todo o histórico de rolagens"""
    save_log([])

# ---------------- GAME RULES ----------------
ATTRIBUTES = ["Força","Agilidade","Intelecto","Percepção","Presença","Vigor"]
DICE_TYPES = ["d4","d6","d8","d10","d12","d20","d100"]
SKILLS = ["Luta","Pontaria","Investigação","Ocultismo","Social","Furtividade","Medicina"]
# ---------------- ITENS DO RPG ----------------
ITEM_DATABASE = {
    "Canivete": {
        "Descrição": "Dano: 1d6 + Força."
    },
    "Chave Inglesa enferrujada": {
        "Descrição": "Dano: 1d4 + Força."
    },
    "Taser (Arma de Choque)": {
        "Descrição": "Acerto: 1d20 + Agilidade.\nDano: 1d4 + Efeito.\nEfeito: alvo perde o próximo turno.",
        "Alcance": "6 metros"
    },
    "Arco": {
        "Alcance": "1 a 50 metros",
        "Descrição": "Acerto: 1d20 + Agilidade + Força\nDano: 1d12\nDesastre: erra ou acerta aliado\nFracasso: 10–20m\nNormal: 30m\nBom: 40m\nExtremo: acerto perfeito"
    },
    "Sinalizador": {
        "Alcance": "50 metros",
        "Descrição": "Acerto: 1d20 + Agilidade\nDano: 1d6 + efeito\nEfeito: 1–3 queimadura leve • 4–6 fogo crescente"
    },
    "Taser de Mão": {
        "Descrição": "Acerto: 1d20 + Agilidade\nDano: 1d4 + efeito\nEfeito: alvo perde o próximo turno."
    },
    "Kit Medico Basico": {
        "Descrição": "Rola 1d12.\n1–6 = +3 vida\n7–12 = +6 vida"
    },
    "Frascos de Remédio": {
        "Descrição": "Rola 1d6.\n1–2 = +1 vida\n3–4 = +2 vida\n5–6 = +3 vida"
    },
    "Mochila": {
        "Descrição": "Adiciona +3 espaços no inventário enquanto estiver no inventário do jogador."
    },

}

# ---------------- STYLE ----------------
st.markdown("""
<style>
html,body{background-color:black;color:#f2f2f2;font-family:'Courier New',monospace;}
.card{background:#111111;border:1px solid #b71c1c;padding:12px;border-radius:8px;margin-bottom:12px;}
.header-title{color:#b71c1c;font-size:20px;font-weight:700;}
.stButton>button{background:linear-gradient(180deg,#8b0000,#b71c1c);color:white;border-radius:8px;}
.roll-box{background:#222222;padding:12px;border-radius:8px;margin:6px 0;}
.desastre{color:#ff6b6b;font-weight:700;}
.fracasso{color:#ff7f50;font-weight:700;}
.normal{color:#ffffff;}
.bom{color:#00ff7f;font-weight:700;}
.extremo{color:#ffd24d;font-weight:800;}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🔆 Ordem ESPERALUME")

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'Login'

# Tabs
tabs = st.columns([1,1,1,1,1])
tab_names = ["Login","Ficha","Rolador","Mestre","Itens"]
for i, t in enumerate(tab_names):
    if st.button(t, key=f"tab_{t}"):
        st.session_state['active_tab'] = t
active = st.session_state['active_tab']

# ---------------- LOGIN ----------------
if active == "Login":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>Login</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("Nome", key="login_player_name")
        p_pwd = st.text_input("Senha", type="password", key="login_player_pwd")
        if st.button("Entrar como Jogador"):
            f = load_ficha(p_name)
            if f and f.get("senha") == p_pwd:
                st.session_state['current_user'] = {'name':p_name,'is_master':False}
                st.session_state['active_tab'] = 'Ficha'
                st.success(f"Bem-vindo {p_name}")
            elif not f:
                ficha = {
                    'nome':p_name,'senha':p_pwd,'apelido':'','idade':18,'classe':'','o_que_faz':'','historia':'',
                    'atributos':{a:1 for a in ATTRIBUTES},'pv':25,'ps':25,'pm':0,'pe':5,'itens':['']*8
                }
                save_ficha(p_name,ficha)
                st.session_state['current_user'] = {'name':p_name,'is_master':False}
                st.session_state['active_tab'] = 'Ficha'
                st.success(f"Conta criada para {p_name}")
    with col2:
        m_pwd = st.text_input("Senha Mestre", type="password", key="login_master_pwd")
        if st.button("Entrar como Mestre"):
            if m_pwd == MASTER_PASSWORD:
                st.session_state['current_user'] = {'name':'MESTRE','is_master':True}
                st.session_state['active_tab'] = 'Mestre'
                st.success("Acesso Mestre concedido")
            else:
                st.error("Senha do Mestre incorreta")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FICHA TAB ----------------
elif active == "Ficha":
    cu = st.session_state.get("current_user")
    if not cu or cu.get("is_master"):
        st.warning("Entre como jogador para editar sua ficha.")
    else:
        player = cu.get("name")
        ficha = load_ficha(player) or {}
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='header-title'>Ficha do Agente — {player}</div>", unsafe_allow_html=True)
        st.write("")

        # Dados pessoais
        col1, col2 = st.columns([1,1])
        with col1:
            nome = st.text_input("Nome", value=ficha.get("nome", player))
            apelido = st.text_input("Apelido", value=ficha.get("apelido",""))
            idade = st.number_input("Idade", min_value=0, max_value=120, value=ficha.get("idade",18))
            classe = st.text_input("Classe", value=ficha.get("classe",""))
            o_que = st.text_area("O que ela faz", value=ficha.get("o_que_faz",""), height=80)
        with col2:
            historia = st.text_area("História do personagem", value=ficha.get("historia",""), height=220)
            descricao = st.text_area("Descrição do Personagem",value=ficha.get("descricao", ""),height=150,key=f"descricao_{player}")
            
        st.write("")
        st.markdown("**Atributos** (1–5) — cada um pode editar; mínimo 1, máximo 5", unsafe_allow_html=True)
        cols = st.columns(6)
        new_attrs = {}
        for i, a in enumerate(ATTRIBUTES):
            with cols[i]:
                v = st.number_input(a, min_value=1, max_value=5, value=ficha.get("atributos", {}).get(a, 1), key=f"attr_{a}_{player}")
                new_attrs[a] = int(v)

        st.write("")
        st.markdown("**Pontos**")
        # Pontos com barras estilizadas
        pv = st.number_input("PV (0–25)", min_value=0, max_value=25, value=ficha.get("pv",25))
        ps = st.number_input("PS (0–25)", min_value=0, max_value=25, value=ficha.get("ps",25))
        pm = st.number_input("PM (0–3)", min_value=0, max_value=3, value=ficha.get("pm",0))
        pe = st.number_input("PE (0–5)", min_value=0, max_value=5, value=ficha.get("pe",5))

        # NEX como percentual
        nex_options = [str(x)+"%" for x in [0,5,10,15,20,25,30,35,40,45,50,60,70,80,90,100]]
        nex_str = st.selectbox("NEX", options=nex_options, index=nex_options.index(f"{ficha.get('nex',0)}%" if ficha.get('nex',0) else "0%"))
        nex_val = int(nex_str.replace("%",""))

        # Renderizando barras
        pontos = {
            "PV": {"val": pv,"color":"#ff4d4d"},
            "PS": {"val": ps,"color":"#3399ff"},
            "PM": {"val": pm,"color":"#000000"},
            "PE": {"val": pe,"color":"#ffffff"},
            "NEX": {"val": nex_val,"color":"#9933ff"}
        }
        for key,p in pontos.items():
            max_val = 25 if key in ["PV","PS"] else 3 if key=="PM" else 5 if key=="PE" else 100
            width_pct = int((p['val']/max_val)*100) if max_val>0 else 0
            st.markdown(f"<div style='margin-bottom:4px'>{key}: {p['val']} <div style='background:#222;border-radius:6px;width:100%;height:18px'><div style='width:{width_pct}%;background:{p['color']};height:100%;border-radius:6px'></div></div></div>", unsafe_allow_html=True)


        # --- INVENTÁRIO COM SISTEMA DE MOCHILA ---
st.write("")
st.markdown("**Inventário**", unsafe_allow_html=True)

# Número base de slots
base_slots = 8

# Verifica se a ficha já tem itens
items = ficha.get("itens", [""] * base_slots)

# Detecta se há Mochila
has_mochila = "Mochila" in items

# Bônus de +3 slots se tiver Mochila
bonus_slots = 3 if has_mochila else 0

# Total de slots
total_slots = base_slots + bonus_slots

st.markdown(f"Slots disponíveis: **{total_slots}** (Mochila: {'Sim' if has_mochila else 'Não'})")

# Expandindo a lista se necessário
if len(items) < total_slots:
    items += [""] * (total_slots - len(items))

# Renderizando inputs de inventário
new_items = []
for i in range(total_slots):
    val = st.text_input(
        f"Item {i+1}",
        value=items[i],
        key=f"inv_{player}_{i}"
    )
    new_items.append(val)
    
st.write("")
if st.button("💾 Salvar Ficha"):
    new_f = {
        "nome": nome,
        "senha": ficha.get("senha", ""),
        "apelido": apelido,
        "idade": int(idade),
        "classe": classe,
        "o_que_faz": o_que,
        "historia": historia,
        "atributos": new_attrs,
        "pv": int(pv),
        "ps": int(ps),
        "pm": int(pm),
        "pe": int(pe),
        "nex": nex_val,
        "itens": new_items
    }
        st.write("")
        if st.button("💾 Salvar Ficha"):
            new_f = {
                "nome": nome,
                "senha": ficha.get("senha", ""),
                "apelido": apelido,
                "idade": int(idade),
                "classe": classe,
                "o_que_faz": o_que,
                "historia": historia,
                "atributos": new_attrs,
                "pv": int(pv),
                "ps": int(ps),
                "pm": int(pm),
                "pe": int(pe),
                "nex": nex_val,
                "itens": new_items
            }
            save_ficha(player, new_f)
            st.success("Ficha salva com sucesso.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ROLADOR TAB ----------------
elif active == "Rolador":
    cu = st.session_state.get("current_user")
    if not cu:
        st.warning("Faça login como Jogador ou Mestre para rolar.")
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='header-title'>Rolador de Dados</div>", unsafe_allow_html=True)
        st.write("")

        col1, col2 = st.columns([1,1])
        with col1:
            qty = st.number_input("Quantidade de dados", min_value=1, max_value=50, value=1, key="roll_qty")
        with col2:
            dtype = st.selectbox("Tipo de dado", DICE_TYPES, index=5, key="roll_type")

        st.write("")
        attr_choice = st.selectbox("Atributo (adiciona bônus)", options=["(nenhum)"] + ATTRIBUTES, index=0, key="roll_attr")

        do_roll = st.button("🔁 Rolar")
        if do_roll:
            faces = int(dtype.replace("d",""))
            results = [random.randint(1,faces) for _ in range(qty)]
            subtotal = sum(results)

            # bônus do atributo = valor do atributo
            attr_bonus = 0
            if attr_choice != "(nenhum)" and not cu.get("is_master"):
                f = load_ficha(cu["name"])
                if f:
                    attr_bonus = f.get("atributos", {}).get(attr_choice, 0)

            total = subtotal + attr_bonus
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # determinar nível
            if qty == 1 and dtype == "d20":
                raw = results[0]
                if raw == 1:
                    level = "Desastre"
                elif 2 <= total <= 9:
                    level = "Fracasso"
                elif 10 <= total <= 14:
                    level = "Normal"
                elif 15 <= total <= 19:
                    level = "Bom"
                else:
                    level = "Extremo"
            else:
                level = None  # para múltiplos dados ou outros tipos

            entry = {
                "who": "MESTRE" if cu.get("is_master") else cu.get("name"),
                "time": ts,
                "qty": qty,
                "type": dtype,
                "results": results,
                "subtotal": subtotal,
                "attr": attr_choice if attr_choice != "(nenhum)" else None,
                "attr_bonus": attr_bonus,
                "total": total,
                "level": level
            }
            append_log(entry)

            # mostrar resultado
            if level:
                colors = {
                    "Desastre":"#ff6b6b",
                    "Fracasso":"#ff4d4d",
                    "Normal":"#cfcfcf",
                    "Bom":"#ffd88a",
                    "Extremo":"#ffd24d"
                }
                st.markdown(f"<div style='font-size:20px; font-weight:700; color:{colors.get(level,'white')}'>{level} → Total: {total} (dado: {results[0]} + bônus: {attr_bonus})</div>", unsafe_allow_html=True)
            else:
                st.write(f"Total final (dados + bônus): {total} → {results} + bônus {attr_bonus}")

        # últimas 15 roladas do jogador
        log = load_log()
        if not cu.get("is_master"):
            last_entries = [e for e in reversed(log) if e["who"]==cu["name"]][:15]
        else:
            last_entries = [e for e in reversed(log) if e["who"]!="MESTRE"][:15]  # Mestre vê todas

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("Últimas 15 roladas")
        if not last_entries:
            st.info("Nenhuma rolagem ainda.")
        else:
            colors = {
                "Desastre":"#ff6b6b",
                "Fracasso":"#ff4d4d",
                "Normal":"#cfcfcf",
                "Bom":"#ffd88a",
                "Extremo":"#ffd24d"
            }
            for e in last_entries:
                who=e['who']; total=e['total']; results=e['results']; level=e.get('level','')
                color = colors.get(level,'white')
                st.markdown(f"<div style='padding:5px; color:{color};'>{e['time']} — {who} → {total} (dados: {results}) {f'[{level}]' if level else ''}</div>", unsafe_allow_html=True)
# ---------------- ITENS TAB ----------------
elif active == "Itens":
    cu = st.session_state.get("current_user")
    if not cu:
        st.warning("Faça login para ver seus itens.")
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='header-title'>🎒 Itens do Inventário</div>", unsafe_allow_html=True)
        st.write("")

        # Se for mestre → escolhe qual ficha ver itens
        if cu.get("is_master"):
            fichas = list_fichas()
            sel = st.selectbox("Escolher ficha", ["(selecione)"] + fichas)
            if sel != "(selecione)":
                ficha = load_ficha(sel)
                itens = ficha.get("itens", [])
                st.subheader(f"Inventário de {sel}")
        else:
            ficha = load_ficha(cu["name"])
            itens = ficha.get("itens", [])
            st.subheader("Seus itens")

        itens_validos = [i for i in itens if i and i.strip()]

        if not itens_validos:
            st.info("Nenhum item no inventário.")
        else:
            for it in itens_validos:
                st.markdown(f"<hr/><h3>🔹 {it}</h3>", unsafe_allow_html=True)

                if it in ITEM_DATABASE:
                    data = ITEM_DATABASE[it]
                    for k, v in data.items():
                        st.markdown(f"**{k}:** {v}")
                else:
                    st.markdown("*Item não registrado na base de dados.*")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- HISTÓRICO TAB ----------------
elif active == "Historico":
    cu = st.session_state.get("current_user")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='header-title'>Histórico de Rolagens</div>", unsafe_allow_html=True)

    log = load_log()
    if not log:
        st.info("Nenhuma rolagem registrada.")
    else:
        colors = {
            "Desastre":"#ff6b6b",
            "Fracasso":"#ff4d4d",
            "Normal":"#cfcfcf",
            "Bom":"#ffd88a",
            "Extremo":"#ffd24d"
        }
        for e in reversed(log[-200:]):  # até 200 últimas roladas
            who=e['who']; total=e['total']; results=e['results']; level=e.get('level','')
            color = colors.get(level,'white')
            st.markdown(f"<div style='padding:5px; color:{color};'>{e['time']} — {who} → {total} (dados: {results}) {f'[{level}]' if level else ''}</div>", unsafe_allow_html=True)

    if st.button("🧹 Limpar histórico"):
        clear_log()
        st.success("Histórico limpo.")
        st.experimental_set_query_params(tab="Historico")  # mantém aba aberta
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MESTRE TAB ----------------
elif active == "Mestre":
    cu = st.session_state.get("current_user")
    if not cu or not cu.get("is_master"):
        st.warning("Aba Mestre restrita. Faça login como Mestre.")
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='header-title'>Painel do Mestre</div>", unsafe_allow_html=True)
        st.write("")

        col1, col2 = st.columns([0.35,0.65])
        with col1:
            st.subheader("Fichas existentes")
            fichas = list_fichas()
            sel = st.selectbox("Selecionar ficha", options=["(escolha)"] + fichas)
            if st.button("Ver ficha (Mestre)"):
                if sel and sel != "(escolha)":
                    f = load_ficha(sel)
                    if f:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        alias = f.get("apelido","")
                        st.markdown(f"<div style='font-weight:700;color:#f2f2f2;font-size:20px'>{f.get('nome')}{(' ('+alias+')') if alias else ''}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='small muted'>Classe: {f.get('classe','—')} • Idade: {f.get('idade','—')}</div>", unsafe_allow_html=True)
                        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.03)'/>", unsafe_allow_html=True)

                        # O que faz
                        st.markdown("<div class='small-muted'>🧠 O que ela faz</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='hist-box'>{(f.get('o_que_faz','—') or '—').replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

                        # Atributos
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='small-muted'>Atributos</div>", unsafe_allow_html=True)
                        attr_html = " ".join([f"<span class='badge'>{a}: {f.get('atributos',{}).get(a,1)}</span>" for a in ATTRIBUTES])
                        st.markdown(attr_html, unsafe_allow_html=True)

                        # Pontos + NEX com barras
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='small-muted'>📊 Pontos e NEX</div>", unsafe_allow_html=True)
                        pontos = {
                            "PV": {"val": f.get("pv",0),"color":"#ff4d4d","max":25},
                            "PS": {"val": f.get("ps",0),"color":"#3399ff","max":25},
                            "PM": {"val": f.get("pm",0),"color":"#000000","max":3},
                            "PE": {"val": f.get("pe",0),"color":"#ffffff","max":5},
                            "NEX": {"val": f.get("nex",0),"color":"#9933ff","max":100}
                        }
                        for key,p in pontos.items():
                            width_pct = int((p['val']/p['max'])*100) if p['max']>0 else 0
                            st.markdown(f"<div style='margin-bottom:4px'>{key}: {p['val']} <div style='background:#222;border-radius:6px;width:100%;height:18px'><div style='width:{width_pct}%;background:{p['color']};height:100%;border-radius:6px'></div></div></div>", unsafe_allow_html=True)

                        # Inventário
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='small-muted'>🎒 Inventário</div>", unsafe_allow_html=True)
                        if f.get("itens"):
                            for it in f.get("itens", []):
                                st.markdown(f"<div class='inv-item'><div class='inv-icon'>🎒</div><div style='flex:1'><strong>{it or '—'}</strong></div></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='muted'>Vazio</div>", unsafe_allow_html=True)

                        # História
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='small-muted'>📜 História</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='hist-box'>{(f.get('historia','—') or '—').replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.subheader("Últimas 15 rolagens dos jogadores")
            log = load_log()
            if not log:
                st.info("Nenhuma rolagem registrada.")
            else:
                # pega apenas últimas 15
                last_entries = list(reversed(log[-15:]))
                for e in last_entries:
                    who = e.get("who")
                    total = e.get("total")
                    results = e.get("results")
                    level = e.get("level", "Normal")  # fallback se não existir
                    # cores
                    color_map = {
                        "Desastre":"#ff6b6b",
                        "Fracasso":"#ffb4b4",
                        "Normal":"#9a9a9a",
                        "Bom":"#ffd88a",
                        "Extremo":"#ffd24d"
                    }
                    col = color_map.get(level,"#ffffff")
                    st.markdown(f"<div class='roll-line'><strong>{who}</strong> → Total: {total} <span style='color:{col}'>{level}</span> (dados: {results})</div>", unsafe_allow_html=True)

        if st.button("🧹 Limpar histórico"):
            clear_log()
            st.session_state["active_tab"] = "Historico"  # ou qualquer aba 
            st.experimental_set_query_paramsst.query_params()  # força atualização do estado

        st.markdown("</div>", unsafe_allow_html=True)












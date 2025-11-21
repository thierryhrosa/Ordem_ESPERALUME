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
        "Descrição": "Acerto: 1d20 + Agilidade + Força\\\\nDano: 1d12\\\\nDesastre: erra ou acerta aliado\\\\nFracasso: 10–20m\\\\nNormal: 30m\\\\nBom: 40m\\\\nExtremo: acerto perfeito"
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
    "Caderninho Velho": {
        "Descrição": "Desenho do Colt com seu pai logo atras."
    },
    "Livros de Sobrevivência Básica, Intermediário, Avançada": {
        "Descrição": "Ganha +Intelecto na rolagem: Básica: +1, Intermedíario: +2, Avançada: +3."
    },
    "Rádio de Comunicação": {
        "Descrição": "Serve para acessar alguma torre de comunicação."
    },
    "Garrafa de Água": {
        "Descrição": "Recupera +1 Pontos de Sanidade ao tomar."
    },
    "Corda": {
        "Descrição": "Uso multíplo."
    },
    "Câmera Fotografica": {
        "Descrição": "Serve para registrar momentos."
    },
    "Lanterna": {
        "Descrição": "Concede poder enxergar no escuro."
    },
    "Fones Bluetooth": {
        "Descrição": "Se você escutar musica, recupera +3 Pontos de Sanidade."
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
tab_names = ["Login","Ficha","Rolador","Mestre","Itens","Guia","???"]
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
            
             # --- DEFESA E MOVIMENTO ---
        st.write("")
        st.markdown("**Combate**", unsafe_allow_html=True)

        col_def, col_mov = st.columns(2)

        with col_def:
            defesa = st.number_input(
                "🛡️ Defesa (1–15)",
                min_value=1,
                max_value=15,
                value=ficha.get("defesa", 10),
                step=1,
                key=f"defesa_{player}"
            )

        with col_mov:
            movimento = st.number_input(
                "🏃‍♂️ Movimento (0–10 m)",
                min_value=0,
                max_value=10,
                value=ficha.get("movimento", 6),
                step=1,
                key=f"movimento_{player}"
            )

        # --- ESTADOS DO PERSONAGEM ---
        st.write("")
        st.markdown("**Estados do Personagem**", unsafe_allow_html=True)

        lesao_grave = st.checkbox(
            "🤕 Lesão Grave",
            value=ficha.get("lesao_grave", False),
            key=f"lesao_{player}"
        )

        inconsciente = st.checkbox(
            "😵‍💫 Inconsciente",
            value=ficha.get("inconsciente", False),
            key=f"inconsciente_{player}"
        )

        morrendo = st.checkbox(
            "💀 Morrendo",
            value=ficha.get("morrendo", False),
            key=f"morrendo_{player}"
        )


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
                "descricao": descricao,
                "atributos": new_attrs,
                "pv": int(pv),
                "ps": int(ps),
                "pm": int(pm),
                "pe": int(pe),
                "nex": nex_val,
                "itens": new_items,
                "lesao_grave": lesao_grave,
                "inconsciente": inconsciente,
                "morrendo": morrendo,
                "defesa": int(defesa),
                "movimento": int(movimento),
            }
            save_ficha(player, new_f)
            st.success("Ficha salva com sucesso.")

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
                st.markdown(f"<div style='padding:5px; color:{color};'>{e['time']} — {who} → {total} (dados: {results}) {f'[{level}]' if level else ''}</div>", unsafe_allow_html=
               
# ───────────────────────────────────────────
# ABA SECRETA DO ASSASSINO (aparece só com senha)
# ───────────────────────────────────────────

with st.sidebar.expander("Acesso do Mestre"):
    senha_mestre = st.text_input("Senha do Mestre", type="password")

if senha_mestre == "ordo2025":
    aba_assassino = st.tabs(["???"])[0]

    with aba_assassino:
        st.title("Ficha do Assassino")

        st.subheader("Identidade")
        nome_assassino = st.text_input("Nome do Assassino")
        apelido_assassino = st.text_input("Apelido")
        idade_assassino = st.number_input("Idade", min_value=0, max_value=200, step=1)

        st.subheader("História")
        historia_assassino = st.text_area("História Completa")

        st.subheader("Outro Lado")
        classe_outro_lado = st.text_input("Classe do Outro Lado")
        explicacao_classe = st.text_area("Explicação da Classe")

        st.subheader("Aparência")
        aparencia_assassino = st.text_area("Descrição da Aparência do Assassino")

        st.subheader("Atributos")
        colA1, colA2, colA3, colA4 = st.columns(4)
        forca_a = colA1.number_input("Força", 1, 5, 1)
        agilidade_a = colA2.number_input("Agilidade", 1, 5, 1)
        intelecto_a = colA3.number_input("Intelecto", 1, 5, 1)
        presenca_a = colA4.number_input("Presença", 1, 5, 1)

        st.subheader("Status")
        pv_assassino = st.number_input("PV", 1, 999, 10)
        ps_assassino = st.number_input("PS", 1, 999, 10)
        defesa_assassino = st.number_input("Defesa", 0, 50, 10)
        movimento_assassino = st.number_input("Movimento", 0, 20, 6)

        st.subheader("Estados do Personagem")
        lesao_grave_a = st.checkbox("🤕 Lesão Grave")
        inconsciente_a = st.checkbox("😵‍💫 Inconsciente")
        morrendo_a = st.checkbox("💀 Morrendo")

        st.subheader("Inventário")
        inventario_assassino = st.text_area("Itens, armas, equipamentos...")

else:
    st.warning("Área restrita ao Mestre. Insira a senha correta para acessar.")
            
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
    
# ---------------- GUIA ----------------
elif active == "Guia":
    st.markdown("<div class='header-title'>📘 Guia da Ficha</div>", unsafe_allow_html=True)
    st.write("")

    sub1, sub2, sub3, sub4, sub5, sub6, sub7, sub8 = st.tabs(["Atributos", "Pontos de Medo (PM)", "Pontos de Esperança (PE)", "NEX", "Condições do Personagem", "Pontos de Sanidade (PS)", "Pontos de Vida (PV)", "Combate", ])

    with sub1:
        st.markdown("""
### 💪 **1. FORÇA**
**✔ O que representa:**  
Poder físico bruto: levantar peso, causar dano físico, romper barreiras, resistir em quedas ou agarradas.

**✔ Exemplos de uso:**  
- Arrombar uma porta velha.  
- Segurar um inimigo para impedir que ele fuja.  
- Levantar um móvel pesado para alguém passar por baixo.  
- Saltar um vão grande usando pura potência muscular.  
- Golpear com mais impacto (em sistemas que usam Força para dano).

---

### ⚡ **2. AGILIDADE**
**✔ O que representa:**  
Coordenação, reflexo, velocidade, destreza com armas leves e precisão de movimentos.

**✔ Exemplos de uso:**  
- Desviar de um golpe ou esquiva em combate.  
- Correr por um corredor fugindo do assassino.  
- Fazer parkour ou escalar rapidamente uma parede.  
- Acertar um tiro mais difícil ou manipular ferramentas delicadas.  
- Furtar algo discretamente do bolso de alguém.

---

### 🧠 **3. INTELECTO**
**✔ O que representa:**  
Raciocínio lógico, conhecimento técnico, investigação complexa e capacidade de resolver problemas.

**✔ Exemplos de uso:**  
- Resolver um enigma antigo ou decifrar um código.  
- Analisar uma pista e entender o que ela significa.  
- Criar um plano estratégico para invadir um local.  
- Identificar uma substância desconhecida.  
- Realizar cálculos ou montar máquinas improvisadas.

---

### 👁 **4. PERCEPÇÃO**
**✔ O que representa:**  
Atenção aos detalhes, sentidos aguçados, intuição sobre o ambiente ou sobre pessoas.

**✔ Exemplos de uso:**  
- Ouvir passos atrás de você.  
- Ver algo se movendo na floresta no meio da neblina.  
- Sentir cheiro de sangue antes de abrir uma porta.  
- Perceber que alguém está mentindo através de expressões sutis.  
- Encontrar uma pista escondida no cenário.

---

### 😼 **5. PRESENÇA**
**✔ O que representa:**  
Carisma, liderança, intimidação, manipulação social e magnetismo pessoal.

**✔ Exemplos de uso:**  
- Convencer um policial a deixar vocês passarem.  
- Intimidar um cultista para que ele revele algo.  
- Fazer um discurso emocionante para motivar o grupo.  
- Enganar alguém com lábia rápida.  
- Seduzir, persuadir, negociar preciosamente.

---

### ❤️‍🔥 **6. VIGOR**
**✔ O que representa:**  
Resistência física, resistência mental, imunidade, fôlego e capacidade de aguentar dor.

**✔ Exemplos de uso:**  
- Resistir a venenos, gases, medo extremo.  
- Continuar correndo mesmo já exausto.  
- Não desmaiar após levar um golpe pesado.  
- Suportar um ritual que drena energia vital.  
- Agüentar frio, calor, fome ou privação de sono.
        """)
    with sub2:
        st.markdown("""
## 😱 **Pontos de Medo (PM)**

### O que são Pontos de Medo?
Os Pontos de Medo representam o quanto o personagem consegue lidar com terror, pressão psicológica, traumas e fenômenos sobrenaturais.  
Eles funcionam como uma **barra mental**, do mesmo jeito que os PV são uma barra física.  

Quanto mais PM o personagem acumula, mais o medo domina seu comportamento.

---

## 🔧 **Como funcionam os PM**
✔ Cada personagem começa com **0 PM**.  
✔ PM aumenta quando o personagem passa por algo aterrorizante.  
✔ PM nunca é algo “positivo”: cada ponto recebido empurra o personagem para o limite mental.

---

## 🎲 **Teste de Medo**
Sempre que o personagem precisa resistir ao medo, ele faz um:

### 👉 **Teste de VIGOR ou PRESENÇA**  
*(depende da origem do medo)*

- **Falhou?** → ganha PM (quantidade definida pela cena).  
- **Passou?** → não ganha PM, mas ainda sente medo narrativamente.

---

# 🧪 **Efeitos conforme a quantidade de PM**

A barra de PM funciona em “estágios” que representam o estado mental do personagem.

---

## 🟠 **1. Estágio de Tensão — (1 PM)**  
O personagem está abalado, mas ainda funcional.

### Efeitos:
- Mãos tremendo  
- Respiração pesada  
- Desvantagem em ações que exigem calma (ex.: abrir fechaduras, atirar com precisão)  
- Percepção mais ativa, porém **menos precisa**  

---

## 🔴 **2. Estágio de Pânico — (2 PM)**  
Agora o personagem está **realmente perturbado**.

### Efeitos:
- Pequenas alucinações  
- Se assusta com sons simples  
- Falta de foco  
- Chance de travar em momentos críticos  

### Mecânica adicional:
A cada cena tensa → **Teste de VIGOR** para não entrar em pânico.

---

## ☠️ **3. Colapso Mental — (3 PM)**  
O personagem chega ao limite psicológico.

### O jogador rola **1d6** para determinar o tipo de colapso:

1. **Fuga desesperada**  
2. **Travado em choque**  
3. **Gritando histérico**  
4. **Agressivo sem controle**  
5. **Chorando, incapaz de agir**  
6. **Apagão / desmaio mental**

### Recuperação:
O personagem só retorna ao normal com:
- descanso  
- apoio emocional  
- terapia  
- momentos seguros e estáveis  

    """)
    with sub3: 
        st.markdown("""
## ✨ **Pontos de Esperança (PE)**

### O que são Pontos de Esperança?
Os Pontos de Esperança representam a **força interior**, a **vontade de sobreviver**, o **apoio emocional do grupo** e a **capacidade de superar traumas**.

Enquanto os **PM** mostram a queda mental…  
Os **PE** representam **coragem, recuperação e superação**.

---

# 🔧 **Como funcionam os PE**
✔ Cada personagem começa com **5 PE**  

Os PE podem ser gastos de várias maneiras poderosas e narrativas.

---

# 🟢 **Para que servem os Pontos de Esperança?**

---

## ✔ 1. Reduzir ou evitar ganhos de PM
Uma das funções mais importantes:

### 👉 Gaste **1 PE** → cancela **1 PM** que o personagem ganharia.

Representa o personagem encontrando forças internas:  
lembranças, coragem, apoio do grupo, determinação.

---

## ✔ 2. Rerrolar um teste importante
Ao gastar PE, o jogador pode:

- Rerrolar **testes de Medo**
- Rerrolar **tiros decisivos**
- Rerrolar **ações heroicas**

O Mestre decide:
- se pode rerrolar apenas **1 vez por cena**, ou  
- se pode repetir até conseguir sucessos.

---

## ✔ 3. Ganhar vantagem temporária
Exemplo narrativo:

> “Você respira fundo, lembra por que está lutando e se concentra totalmente.”

### Efeito mecânico:
✔ Ganha **vantagem** em **1 teste**.

---

## ✔ 4. Reforçar outro personagem
Você pode **doar 1 PE** para um aliado próximo, simbolizando apoio emocional.

Exemplo narrativo:

> “Eu tô com você. Levanta. A gente vai sair dessa.”

---

## ✔ 5. Evitar 1 PM ganhado
Funciona como um “escudo emocional”.

Se a cena permitir, o jogador pode gastar PE para evitar trauma psicológico.

---

# 🚨 **E se os PE chegarem a 0?**
Não causa colapso mental como o PM, mas deixa o personagem vulnerável.

### Efeitos:
- Não pode **rerrolar testes**
- Não pode **evitar PM**
- Fica emocionalmente fragilizado
- Qualquer **falha crítica em Testes de Medo** causa **+2 PM adicional**

O personagem está **desesperançado** e no limite emocional.

    """)
    with sub4:
        st.markdown("""
## **NEX**
??????????
    """)
    with sub5:
        st.markdown("""
## **Condições do Personagem**

As condições representam estados físicos ou mentais que afetam diretamente o personagem durante o jogo.  
Elas podem ser causadas por ataques, medo, ambientes hostis ou efeitos sobrenaturais.

---

### 🤕 **Lesão Grave**
O personagem sofreu um dano sério, como fraturas, perfurações profundas ou hemorragia (se perder 9+ de dano).

**Efeitos comuns:**
- Desvantagem em testes de Força e Agilidade (correr, lutar, escalar, depende de onde foi o ferimento).
- Redução na movimentação.
- Difícil realizar testes de Força ou Agilidade.
- Se não tratada, pode evoluir para **estado Morrendo**.

---

### 😵‍💫 **Inconsciente**
O personagem apaga totalmente — por trauma, falta de ar, choque ou medo extremo.

**Efeitos:**
- Não pode agir.
- Não pode falar, atacar ou usar itens.
- Só pode ser carregado por aliados.
- Dependendo da causa, pode acordar após:
  - Teste de VIGOR,
  - Tratamento,
  - Passar 1 cena,
  - Ou intervenção sobrenatural (caso narrativo).

---

### 💀 **Morrendo**
O personagem está à beira da morte, perdendo sangue, sufocando, envenenado ou com ferimentos fatais.

**Regra sugerida:**
O jogador rola **1d20 + Vigor por turno**:

- **1–10** → piora (pode morrer em 3 falhas).
- **11–19** → permanece estável.
- **20** → consegue fazer uma ação impossível nesse estado por um turno.

**Efeitos:**
- Não age.
- Requer tratamento imediato (Kit Médico, primeiros socorros, PE narrativo, etc.).
- Se o grupo ignorar, o personagem pode morrer em poucos turnos.

---

### 📘 Observação
Estas condições podem ser ativadas pelos botões da sua ficha:

- 🤕 **Lesão Grave**
- 😵‍💫 **Inconsciente**
- 💀 **Morrendo**

E o mestre pode usar narrativamente para criar cenas dramáticas, perigosas e cinematográficas.
    """)
    with sub6:
        st.markdown("""
## 🧩 Pontos de Sanidade (PS)

Os **Pontos de Sanidade** representam a estabilidade mental do personagem diante do horror, do sobrenatural e de eventos traumáticos.  
Enquanto os **PM** mostram o medo crescente, os **PS** mostram o quanto da mente do personagem ainda permanece intacta.

---

## 🔍 O que os PS representam?

- Equilíbrio mental  
- Capacidade de interpretar a realidade corretamente  
- Resistência a choques psicológicos  
- Controle emocional  
- Ancoragem na própria identidade  

Baixos PS = a mente começa a se fragmentar.

---

## 🎲 Quando testar Sanidade?

Sempre que o personagem presencia algo perturbador, como:

- Cadáveres dilacerados  
- Criaturas sobrenaturais  
- Revelações traumáticas  
- Morte de um aliado  
- Ritual demoníaco  
- Vozes dentro da própria cabeça  

O jogador faz um:

👉 **Teste de Vigor**  
(O mestre define qual faz mais sentido para o evento.)

Se falhar → perde PS.  
Se passar → reduz a perda ou não perde nada (dependendo da cena).

---

## 🚨 Efeitos por níveis de PS

### 🟢 **PS Alto (15–25) — Mente Estável**
- Raciocínio claro  
- Menos chance de ganhar PM  
- Melhor foco  
- Maior resistência a manipulação mental  

### 🟡 **PS Médio (7–14) — Mente Abalada**
- Pesadelos  
- Dificuldades de concentração  
- Pequenas alucinações periféricas  
- Vontade fraca  
- Desvantagem em testes de investigação prolongada  

### 🔴 **PS Baixo (1–6) — À Beira da Ruptura**
- Alucinações vívidas  
- Perda temporária de controle  
- Confusão mental  
- Episódios de paranoia  
- Pode atacar amigos achando que são monstros  
- Testes de Medo ficam mais difíceis  

### ☠️ **PS 0 — Queda Total**
O personagem **entra em colapso mental e quem controla o personagem é o Mestre (temporario)** de forma irreversível…  
Pode virar um NPC, fugir da cena, entrar em coma ou simplesmente “quebrar”.

(O mestre decide o impacto narrativo.)  

---

## ❤️‍🩹 Como recuperar PS?

- Terapia (longa duração)  
- Descanso profundo  
- Ajuda emocional do grupo  
- Ambientes seguros  
- PE usados de forma narrativa  
- Sair de ambientes traumáticos  

---

## 📘 Observação Importante

PS não é apenas um número —  
É **a história mental do personagem** sendo afetada pelo mundo ao redor.

Quando usada bem, a Sanidade cria:

- tensão,  
- imersão,  
- cenas dramáticas,  
- evolução psicológica real.

    """)
        
    with sub7:
        st.markdown("""
## ❤️ Pontos de Vida (PV)

Os **Pontos de Vida** representam a condição física do personagem — sua resistência, vitalidade e capacidade de continuar lutando, correndo e sobrevivendo após ferimentos.

Enquanto PS é mente, **PV é o corpo**.

---

## 🔍 O que PV representa?

- Saúde física
- Força vital
- Resistência a ferimentos
- Capacidade de continuar lutando
- Energia do corpo em situações extremas

Quando os PV caem, o corpo começa a falhar.

---

## 🎯 Como os PV são usados?

O personagem perde PV ao sofrer:

- Ataques físicos  
- Armas cortantes, perfurantes ou contundentes  
- Explosões  
- Quedas  
- Acidentes graves  
- Armas improvisadas  
- Ataques do assassino  

---

## 📉 Efeitos conforme o PV diminui

### 🟢 **PV Alto (15–25) — Saudável**
- Movimentos firmes  
- Reação rápida  
- Pode correr, lutar e atuar no máximo desempenho  
- Sem penalidades  

---

### 🟡 **PV Médio (7–14) — Ferido**
- Dores constantes  
- Movimentos lentos  
- Sangramento leve ou cansaço extremo  
- Desvantagem em testes de esforço físico (Força / Agilidade)  
- Qualquer tropeço pode piorar  

---

### 🔴 **PV Baixo (1–6) — À Beira de Cair**
- Hemorragia  
- Falta de ar  
- Dores severas  
- Tremor muscular  
- Testes físicos ficam muito difíceis  
- Menor chance de esquiva  
- O personagem pode desmaiar a qualquer momento  

---

### ☠️ **PV = 0 — Condição Crítica**
O personagem não morre imediatamente, mas entra em **estado crítico**:

- Não age até receber ajuda  
- Se não for tratado, caminha para “Morrendo”  
- Perde 1 PV por cena/sequência tensa, caso a situação esteja perigosa  
- Dependendo da história, pode precisar de hospital urgente  

---

## 🩹 Como recuperar PV?

✔ **Primeiros socorros** (testes específicos)  
✔ **Kit Médico Básico**  
✔ **Remédios**  
✔ **Descanso** (leve ou profundo)  
✔ **Tratamento especializado** (hospital, ambulância)  
✔ **Ações narrativas de cuidado feitas por aliados**

---

## ⚠️ Lesões

Mesmo recuperando PV, um personagem pode continuar com:

- Ossos quebrados  
- Hemorragias  
- Cortes profundos  
- Choque  
- Desgaste físico extremo  

Lesões graves podem aplicar desvantagens até serem tratadas.

---

## 🎭 Importância narrativa

PV não mede apenas “vida”, mas **o que o personagem aguenta antes de quebrar fisicamente**.

Permite cenas de:

- heroísmo,  
- sacrifício,  
- desespero,  
- sobrevivência,  
- e tensão real.

Quando bem usado, transforma ferimentos em narrativa viva, não só números.

    """)
        
    with sub8:
        st.markdown("""
## **⚔️ COMBATE — ORDEM ESPERALUME**

O combate em ESPERALUME é intenso, rápido e mortal.  
Personagens são humanos enfrentando forças além da realidade — então qualquer erro pode ser o último.

Aqui está o guia adaptado ao sistema, respeitando PV, PM, PE, Condições e o estilo paranormal de jogo.

---

### **🕒 Estrutura de um Turno**

#### **1. Início do Turno**
O Mestre verifica:

- Condições ativas (Sangramento, Terror, Tremor, Exaustão…)
- Penalidades de PM

#### **2. Ação do Personagem**
Cada personagem pode fazer:

**✔ 1 AÇÃO  
✔ 1 MOVIMENTO**

**Ações possíveis:**
- Atacar corpo a corpo
- Atirar
- Usar itens
- Proteger um aliado
- Furtividade, percepção, testes rápidos
- Gastar PE para rerrolar testes ou cancelar PM
- Confronto psicológico

**Movimentos possíveis:**
- Correr / recuar / avançar
- Buscar cobertura
- Se esconder
- Fugir em pânico
- Proteger alguém

#### **3. Reações**
Permitidas apenas em momentos específicos:

- Bloquear ataque
- Se jogar atrás de cobertura
- Proteger aliado
- Usar PE rapidamente

---

### **🎯 Ataques**

**Corpo a Corpo → usa LUTA**  
**À Distância → usa PONTARIA**

O alvo pode tentar esquivar ou se proteger.

---

### **🔫 Dano**

O dano da arma/ataque pode causar:

- Redução de PV
- Ganho de PM por trauma
- Condições (Terror, Sussurros, Desorientação)

**Acerto Crítico:**
- Dano dobrado  
- Pode causar Lesão Grave 🤕

**Falha Crítica:**
- Arma emperra
- Faz barulho perigoso
- Perde a ação
- Ganha +1 PM pelo estresse

---

### **🛡️ Defesa e Cobertura**

**Coberturas:**
- Leve (mesas, armários): +1 Defesa  
- Média (carros, paredes baixas): +2 Defesa  
- Pesada (paredes sólidas, pilares): +5 Defesa, ataques quase não acertam  


---

### **🏃‍♂️ Movimento**

O ambiente é parte do combate:

- Correr para abrigo
- Se jogar no chão
- Sair da linha de visão
- Trocar posição com aliado
- Subir em objetos
- Passar por portas e brechas
- Esconder-se nas sombras

---

### **❤️ Estados Críticos**

Se PV chegar a **0**, o personagem pode entrar em:

**🤕 Lesão Grave**  
- Penalidades pesadas  
- Movimentos limitados  

**😵‍💫 Inconsciente**  
- Não age  
- Cai no chão  

**💀 Morrendo**  
- Contagem de turnos  
- Testes para sobreviver  
- Falhou → morte  
- Aliado pode estabilizar

---

### **🎲 Modificadores**

**Vantagem** → rola 2 dados e fica com o maior  
Concedido por: PE, apoio ou ambiente.

**Desvantagem** → rola 2 dados e usa o menor  
Causado por: medo, escuridão, condições ruins.

---

### **🔥 Ações Especiais**

- Golpe preciso  
- Distrair Assassino  
- Investida desesperada    
- Selar portas/janelas    

---

### **🧠 O Combate é Emocional**

O sistema incentiva ações criativas:

- Gastar PE para salvar um aliado
- Cancelar PM
- Apoiar emocionalmente outro personagem
- Derrubar objetos para bloquear assassino
- Sacrifícios heroicos
- Falas que aumentem a moral

---
    """)

# ----------------------- MESTRE TAB -----------------------
elif active == "Mestre":
    cu = st.session_state.get("current_user")

    # Se não for mestre, bloqueia
    if not cu or not cu.get("is_master"):
        st.warning("Aba Mestre restrita. Faça login como Mestre.")
    
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='header-title'>Painel do Mestre</div>", unsafe_allow_html=True)
        st.write("")

        # Criando sub-abas
        tab_ficha, tab_rolagens, tab_anotacoes, = st.tabs([
            "Ficha dos Jogadores",
            "Rolagens dos Jogadores",
            "Anotações",
        ])

        # ==========================================================
        # 1) FICHA DOS JOGADORES
        # ==========================================================
        with tab_ficha:
            st.subheader("Fichas dos Jogadores")

            fichas = list_fichas()
            sel = st.selectbox("Selecionar Ficha", ["(escolha)"] + fichas)

            if sel != "(escolha)":
                f = load_ficha(sel)

                if f:
                    st.markdown(f"### {f.get('nome','—')} ({f.get('apelido','')})")
                    st.markdown(f"**Classe:** {f.get('classe','—')} | **Idade:** {f.get('idade','—')}")
                    st.markdown("---")

                    st.markdown("### O que ele(a) faz")
                    st.write(f.get("o_que_faz", "—"))

                    st.markdown("### Atributos")
                    for a, v in f.get("atributos", {}).items():
                        st.write(f"**{a}:** {v}")

                    st.markdown("### Pontos")
                    st.write(f"PV: {f.get('pv',0)}")
                    st.write(f"PS: {f.get('ps',0)}")
                    st.write(f"PM: {f.get('pm',0)}")
                    st.write(f"PE: {f.get('pe',0)}")
                    st.write(f"NEX: {f.get('nex',0)}%")

                    st.markdown("### Condições")
                    st.write(f"🤕 **Lesão Grave:** {f.get('lesao_grave','Não')}")
                    st.write(f"😵‍💫 **Inconsciente:** {f.get('inconsciente','Não')}")
                    st.write(f"💀 **Morrendo:** {f.get('morrendo','Não')}")

                    st.markdown("### Inventário")
                    itens = f.get("itens", [])
                    if itens:
                        for i in itens:
                            st.write(f"- {i}")
                    else:
                        st.write("— Nenhum item —")

                    st.markdown("### História")
                    st.write(f.get("historia", "—"))

        # ==========================================================
        # 2) ROLAGENS DOS JOGADORES
        # ==========================================================
        with tab_rolagens:
            st.subheader("Últimas 15 rolagens")

            log = load_log()

            if not log:
                st.info("Nenhuma rolagem registrada.")
            else:
                ultimas = reversed(log[-15:])

                for e in ultimas:
                    who = e.get("who")
                    total = e.get("total")
                    dados = e.get("results")
                    level = e.get("level", "Normal")

                    st.markdown(
                        f"<div class='roll-line'><strong>{who}</strong> → {total} "
                        f"<span style='color:white'>({level})</span> "
                        f"dados: {dados}</div>",
                        unsafe_allow_html=True
                    )

            if st.button("🧹 Limpar histórico"):
                clear_log()
                st.success("Histórico apagado!")

        # ==========================================================
        # 3) ANOTAÇÕES DO MESTRE
        # ==========================================================
        with tab_anotacoes:
            st.subheader("Anotações do Mestre")

            notas = st.text_area(
                "Digite suas anotações:",
                value=st.session_state.get("notas_mestre", ""),
                height=300
            )

            st.session_state["notas_mestre"] = notas

            if st.button("💾 Salvar Anotações"):
                st.success("Anotações salvas!")













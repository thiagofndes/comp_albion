from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
DATA_PATH = "data"

ROLE_COLORS = {
    "TANK": "#1E3A8A",
    "HEALER": "#047857",
    "DPS": "#7F1D1D",
    "SUPORTE": "#78350F"
}

roles = ["TANK", "HEALER", "DPS", "SUPORTE"]

texts = {
    "pt": {
        "title": "🌹 Gerenciador de COMPS - Albion Online",
        "create": "➕ Criar Nova Comp",
        "edit": "✏️ Editar / Visualizar COMPs",
        "comp_name": "Nome da Comp",
        "num_players": "Quantidade de Jogadores",
        "role": "Função do Jogador",
        "create_btn": "✅ Criar Comp",
        "success": "Comp '{comp}' criada com sucesso!",
        "error": "Você precisa dar um nome para a Comp.",
        "edit_select": "Escolha uma COMP para editar",
        "edit_title": "Editando: {comp} ({num} jogadores)",
        "save": "💾 Salvar Alterações",
        "delete": "🗑️ Excluir COMP",
        "edit_success": "Comp '{comp}' atualizada com sucesso!",
        "delete_success": "Comp '{comp}' excluída com sucesso!",
        "no_comp": "Nenhuma comp criada ainda."
    },
    "en": {
        "title": "🌹 COMPS Manager - Albion Online",
        "create": "➕ Create New Comp",
        "edit": "✏️ Edit / View COMPs",
        "comp_name": "Comp Name",
        "num_players": "Number of Players",
        "role": "Role of Player",
        "create_btn": "✅ Create Comp",
        "success": "Comp '{comp}' successfully created!",
        "error": "You must name your comp.",
        "edit_select": "Choose a COMP to edit",
        "edit_title": "Editing: {comp} ({num} players)",
        "save": "💾 Save Changes",
        "delete": "🗑️ Delete COMP",
        "edit_success": "Comp '{comp}' successfully updated!",
        "delete_success": "Comp '{comp}' successfully deleted!",
        "no_comp": "No comps created yet."
    },
    "es": {
        "title": "🌹 Gestor de COMPS - Albion Online",
        "create": "➕ Crear Nueva Comp",
        "edit": "✏️ Editar / Ver COMPs",
        "comp_name": "Nombre de la Comp",
        "num_players": "Cantidad de Jugadores",
        "role": "Función del Jugador",
        "create_btn": "✅ Crear Comp",
        "success": "¡Comp '{comp}' creada con éxito!",
        "error": "Necesitas dar un nombre a la Comp.",
        "edit_select": "Elige una COMP para editar",
        "edit_title": "Editando: {comp} ({num} jugadores)",
        "save": "💾 Guardar Cambios",
        "delete": "🗑️ Eliminar COMP",
        "edit_success": "¡Comp '{comp}' actualizada con éxito!",
        "delete_success": "¡Comp '{comp}' eliminada con éxito!",
        "no_comp": "No hay comps creadas todavía."
    }
}

def get_idioma():
    return session.get("idioma", "pt")

def load_comps():
    try:
        with open(os.path.join(DATA_PATH, "comps.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_comps(comps):
    with open(os.path.join(DATA_PATH, "comps.json"), "w", encoding="utf-8") as f:
        json.dump(comps, f, ensure_ascii=False, indent=4)

def load_itens(idioma):
    with open(os.path.join(DATA_PATH, "itens_db_t8_completo.json"), "r", encoding="utf-8") as f:
        all_itens = json.load(f)
    return all_itens.get(idioma, {})

@app.route('/')
def index():
    idioma = get_idioma()
    comps = load_comps()
    return render_template("index.html", idioma=idioma, texts=texts[idioma], comps=comps)

@app.route('/set_language/<lang>')
def set_language(lang):
    session["idioma"] = lang
    return redirect(url_for("index"))

@app.route("/create", methods=["GET", "POST"])
def create():
    idioma = get_idioma()
    texts_lang = texts[idioma]
    comps = load_comps()
    itens = load_itens(idioma)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        qtde = request.form.get("qtde")

        # Etapa 1: gerar campos
        if nome and qtde and not request.form.get("arma_0"):
            try:
                qtde = int(qtde)
            except:
                flash(texts_lang["error"], "error")
                return redirect(url_for("create"))

            return render_template("create.html",
                idioma=idioma,
                texts=texts_lang,
                roles=roles,
                itens=itens,
                nome=nome,
                qtde=qtde
            )

        # Etapa 2: salvar COMP
        if not nome:
            flash(texts_lang["error"], "error")
            return redirect(url_for("create"))

        qtde = int(request.form.get("qtde"))
        jogadores = []
        for i in range(qtde):
            jogadores.append({
                "Role": request.form.get(f"role_{i}"),
                "Arma": request.form.get(f"arma_{i}"),
                "Capuz": request.form.get(f"capuz_{i}"),
                "Peito": request.form.get(f"peito_{i}"),
                "Bota": request.form.get(f"bota_{i}"),
                "Capa": request.form.get(f"capa_{i}"),
                "Comida": request.form.get(f"comida_{i}"),
                "Poção": request.form.get(f"pocao_{i}")
            })

        comps[nome] = {
            "qtde_jogadores": qtde,
            "players": jogadores
        }

        save_comps(comps)
        flash(texts_lang["success"].format(comp=nome), "success")
        return redirect(url_for("index"))

    return render_template("create.html", idioma=idioma, texts=texts_lang, roles=roles, itens=load_itens(idioma))

@app.route("/edit/<comp_name>", methods=["GET", "POST"])
def edit_comp(comp_name):
    idioma = get_idioma()
    texts_lang = texts[idioma]
    comps = load_comps()

    if comp_name not in comps:
        flash("Comp não encontrada", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        if "delete" in request.form:
            del comps[comp_name]
            save_comps(comps)
            flash(texts_lang["delete_success"].format(comp=comp_name), "success")
            return redirect(url_for("index"))

        qtde = comps[comp_name]["qtde_jogadores"]
        jogadores = []
        for i in range(qtde):
            jogadores.append({
                "Role": request.form.get(f"role_{i}"),
                "Arma": request.form.get(f"arma_{i}"),
                "Capuz": request.form.get(f"capuz_{i}"),
                "Peito": request.form.get(f"peito_{i}"),
                "Bota": request.form.get(f"bota_{i}"),
                "Capa": request.form.get(f"capa_{i}"),
                "Comida": request.form.get(f"comida_{i}"),
                "Poção": request.form.get(f"pocao_{i}")
            })

        comps[comp_name]["players"] = jogadores
        save_comps(comps)
        flash(texts_lang["edit_success"].format(comp=comp_name), "success")
        return redirect(url_for("index"))

    comp = comps[comp_name]
    itens = load_itens(idioma)

    return render_template("edit.html", nome=comp_name, comp=comp, roles=roles, texts=texts_lang, itens=itens, colors=ROLE_COLORS, idioma=idioma)

@app.route("/view/<comp_name>")
def view_comp(comp_name):
    idioma = get_idioma()
    texts_lang = texts[idioma]
    comps = load_comps()

    if comp_name not in comps:
        flash("Comp não encontrada", "error")
        return redirect(url_for("index"))

    comp = comps[comp_name]
    itens = load_itens(idioma)

    return render_template("view.html", nome=comp_name, comp=comp, roles=roles, texts=texts_lang, itens=itens, colors=ROLE_COLORS, idioma=idioma)

@app.route("/delete", methods=["POST"])
def delete_comp():
    comp_name = request.form.get("comp_name")
    comps = load_comps()
    idioma = get_idioma()

    if comp_name in comps:
        del comps[comp_name]
        save_comps(comps)
        flash(texts[idioma]["delete_success"].format(comp=comp_name), "success")
    else:
        flash("COMP não encontrada.", "error")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

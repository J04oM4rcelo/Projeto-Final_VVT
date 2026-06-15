// ============================================================
//  frontend/js/app.js
//  Apenas uma observação importante: nos templates literals abaixo,
//  use a CRASE como delimitador — aqui no arquivo a gente
//  substituiu por aspas apenas para a exibição no material.
//  No SEU arquivo, use crase normalmente.
// ============================================================
const API = "/api";

const Noticias = {
  usuarioAtual: null,

  // ----- helpers -----
  async json(url, method = "GET", body = null, isForm = false) {
    const opts = {
      method,
      credentials: "include",   // envia cookies de sessão
      headers: {},
    };
    if (body) {
      if (isForm) {
        opts.body = body;  // deixa browser definir Content-Type
      } else {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(body);
      }
    }
    const res = await fetch(API + url, opts);
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  },

  msg(el, texto, erro = true) {
    if (!el) return;
    el.hidden = false;
    el.textContent = texto;
    el.className = erro ? "msg-err" : "msg-ok";
  },

  // ----- página pública -----
  async carregarPublicas() {
    const { data } = await this.json("/noticias/publicas");
    const lista = document.getElementById("lista");
    if (!data || data.length === 0) {
      lista.innerHTML = '<p class="muted">Nenhuma notícia publicada.</p>';
      return;
    }
    lista.innerHTML = data.map(n => {
      const img = n.imagem
        ? '<img src="http://localhost:5000/uploads/' + n.imagem + '" alt="">'
        : '<div style="height:160px;background:#e2e8f0;display:flex;'
        + 'align-items:center;justify-content:center;color:#94a3b8;">sem imagem</div>';
      return (
        '<article class="card-noticia">' + img +
        '<div class="corpo">' +
          '<h3>' + n.titulo + '</h3>' +
          '<div class="data">' + n.data_noticia + ' · ' + (n.autor_nome || "—") + '</div>' +
          '<p class="texto">' + n.texto.slice(0, 140) + (n.texto.length > 140 ? "…" : "") + '</p>' +
        '</div></article>'
      );
    }).join("");
  },

  // ----- login -----
  async fazerLogin(e) {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value;
    const m = document.getElementById("msg");
    const { ok, data } = await Noticias.json("/login", "POST", { email, senha });
    if (ok) {
      Noticias.msg(m, "Login realizado! Redirecionando...", false);
      setTimeout(() => (window.location.href = "admin.html"), 600);
    } else {
      Noticias.msg(m, data.erro || "Credenciais inválidas");
    }
  },

  // ----- admin -----
  async iniciarAdmin() {
    const { ok, data } = await this.json("/me");
    if (!ok) { window.location.href = "login.html"; return; }
    this.usuarioAtual = data;
    document.getElementById("usuario-info").textContent =
      data.nome + " · " + (data.tipo === "admin" ? "Administrador" : "Usuário");

    if (data.tipo === "admin") {
      document.getElementById("aba-usuarios").hidden = false;
      this.carregarUsuarios();
    }

    document.getElementById("btn-sair").onclick = async (e) => {
      e.preventDefault();
      await this.json("/logout", "POST");
      window.location.href = "login.html";
    };

    document.getElementById("btn-nova-noticia").onclick = () => this.abrirModalNoticia();
    document.getElementById("btn-novo-usuario").onclick = () => this.abrirModalUsuario();
    document.getElementById("form-noticia").onsubmit = (e) => this.salvarNoticia(e);
    document.getElementById("form-usuario").onsubmit = (e) => this.salvarUsuario(e);

    this.carregarNoticias();
  },

  // ===== NOTÍCIAS =====
  _idNoticiaEditando: null,

  async carregarNoticias() {
    const { data } = await this.json("/noticias");
    const lista = document.getElementById("lista-noticias");
    if (!data || data.length === 0) {
      lista.innerHTML = '<p class="muted">Nenhuma notícia cadastrada.</p>';
      return;
    }
    lista.innerHTML = data.map(n => {
      const img = n.imagem
        ? '<img src="http://localhost:5000/uploads/' + n.imagem + '" alt="">'
        : '<div style="height:160px;background:#e2e8f0;display:flex;'
        + 'align-items:center;justify-content:center;color:#94a3b8;">sem imagem</div>';
      const status = n.ativo
        ? '<span class="badge-ativo">ativa</span>'
        : '<span class="badge-off">desativada</span>';
      const acao = n.ativo
        ? '<button class="btn-mini btn-danger" data-desativar="' + n.id + '">Desativar</button>'
        : '<span class="muted" style="font-size:12px;">já desativada</span>';
      return (
        '<article class="card-noticia">' + img +
        '<div class="corpo">' +
          '<div style="display:flex;justify-content:space-between;align-items:center;">' +
            '<h3 style="margin:0;font-size:16px;">' + n.titulo + '</h3>' + status +
          '</div>' +
          '<div class="data">' + n.data_noticia + '</div>' +
          '<p class="texto">' + n.texto.slice(0,120) + (n.texto.length>120?"…":"") + '</p>' +
          '<div style="display:flex;gap:6px;margin-top:8px;">' +
            '<button class="btn-mini" data-edit="' + n.id + '">Editar</button>' + acao +
          '</div>' +
        '</div></article>'
      );
    }).join("");

    lista.querySelectorAll("[data-edit]").forEach(b =>
      b.onclick = () => this.abrirModalNoticia(+b.dataset.edit));
    lista.querySelectorAll("[data-desativar]").forEach(b =>
      b.onclick = () => this.desativarNoticia(+b.dataset.desativar));
  },

  async abrirModalNoticia(id = null) {
    this._idNoticiaEditando = id;
    const form = document.getElementById("form-noticia");
    form.reset();
    document.getElementById("modal-noticia-tit").textContent =
      id ? "Editar notícia" : "Nova notícia";
    if (id) {
      const { data } = await this.json("/noticias/" + id);
      form.titulo.value = data.titulo;
      form.data_noticia.value = data.data_noticia;
      form.texto.value = data.texto;
    }
    document.getElementById("modal-noticia").showModal();
  },

  async salvarNoticia(e) {
    e.preventDefault();
    const form = e.target;
    const fd = new FormData(form);
    const id = this._idNoticiaEditando;
    const res = id
      ? await this.json("/noticias/" + id, "PUT", fd, true)
      : await this.json("/noticias", "POST", fd, true);
    if (res.ok) {
      form.closest("dialog").close();
      this.carregarNoticias();
    } else {
      alert(res.data.erro || "Erro ao salvar");
    }
  },

  async desativarNoticia(id) {
    const msg = "Desativar esta notícia? Ela continuará no banco,"
              + " mas deixará de aparecer no portal.";
    if (!confirm(msg)) return;
    await this.json("/noticias/" + id + "/desativar", "POST");
    this.carregarNoticias();
  },

  // ===== USUÁRIOS =====
  _idUsuarioEditando: null,

  _renderTabelaUsuarios(data) {
    const rows = data.map(u => {
      const tipo = u.tipo === "admin"
        ? '<span class="badge-admin">admin</span>' : 'comum';
      const status = u.ativo
        ? '<span class="badge-ativo">ativo</span>'
        : '<span class="badge-off">desativado</span>';
      const acao = u.ativo
        ? '<button class="btn-mini btn-danger" data-u-des="' + u.id + '">Desativar</button>'
        : '';
      return (
        '<tr>' +
          '<td>' + u.nome + '</td>' +
          '<td>' + u.email + '</td>' +
          '<td>' + tipo + '</td>' +
          '<td>' + status + '</td>' +
          '<td><button class="btn-mini" data-u-edit="' + u.id + '">Editar</button>' + acao + '</td>' +
        '</tr>'
      );
    }).join("");
    return (
      '<table class="tbl">' +
        '<thead><tr><th>Nome</th><th>Email</th><th>Tipo</th><th>Status</th><th></th></tr></thead>' +
        '<tbody>' + rows + '</tbody>' +
      '</table>'
    );
  },

  async carregarUsuarios() {
    const { data } = await this.json("/usuarios");
    const lista = document.getElementById("lista-usuarios");
    if (!data || data.length === 0) {
      lista.innerHTML = '<p class="muted">Nenhum usuário cadastrado.</p>';
      return;
    }
    lista.innerHTML = this._renderTabelaUsuarios(data);

    lista.querySelectorAll("[data-u-edit]").forEach(b =>
      b.onclick = () => this.abrirModalUsuario(+b.dataset.uEdit));
    lista.querySelectorAll("[data-u-des]").forEach(b =>
      b.onclick = () => this.desativarUsuario(+b.dataset.uDes));
  },

  async abrirModalUsuario(id = null) {
    this._idUsuarioEditando = id;
    const form = document.getElementById("form-usuario");
    form.reset();
    document.getElementById("modal-usuario-tit").textContent =
      id ? "Editar usuário" : "Novo usuário";
    document.getElementById("senha-usuario").required = !id;
    if (id) {
      const { data } = await this.json("/usuarios");
      const u = data.find(x => x.id === id);
      form.nome.value = u.nome;
      form.email.value = u.email;
      form.tipo.value = u.tipo;
    }
    document.getElementById("modal-usuario").showModal();
  },

  async salvarUsuario(e) {
    e.preventDefault();
    const form = e.target;
    const body = {
      nome: form.nome.value.trim(),
      email: form.email.value.trim().toLowerCase(),
      tipo: form.tipo.value,
    };
    if (form.senha.value) body.senha = form.senha.value;

    const id = this._idUsuarioEditando;
    const res = id
      ? await this.json("/usuarios/" + id, "PUT", body)
      : await this.json("/usuarios", "POST", body);
    if (res.ok) {
      form.closest("dialog").close();
      this.carregarUsuarios();
    } else {
      alert(res.data.erro || "Erro ao salvar usuário");
    }
  },

  async desativarUsuario(id) {
    if (!confirm("Desativar este usuário? Ele não poderá mais fazer login.")) return;
    await this.json("/usuarios/" + id + "/desativar", "POST");
    this.carregarUsuarios();
  },
};
from flask import render_template, abort
from app.extensions import kata_loader


@web_bp.get("/")
def index():
    katas = kata_loader.load_all()
    return render_template("index.html", katas=katas)


@web_bp.get("/katas/<kata_id>")
def kata_detail(kata_id: str):
    kata = kata_loader.get(kata_id)
    if not kata:
        abort(404)
    return render_template("kata_detail.html", kata=kata)


@web_bp.post("/register")
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("web.index"))
    return render_template("register.html", form=form)

from flask import render_template, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from app.extensions import db, kata_loader
from app.models.submission import Submission
from app.models.user import User
from app.web.forms import LoginForm, RegistrationForm
from app.web import web_bp


@web_bp.get("/")
def index():
    katas = kata_loader.load_all()
    return render_template("index.html", katas=katas)


@web_bp.get("/katas/<kata_id>")
def kata_detail(kata_id: str):
    kata = kata_loader.get(kata_id)
    if not kata:
        abort(404)

    recent_submissions = []
    if current_user.is_authenticated:
        recent_submissions = (
            Submission.query.filter_by(kata_id=kata_id, user_id=current_user.id)
            .order_by(Submission.created_at.desc())
            .limit(20)
            .all()
        )

    return render_template(
        "kata_detail.html",
        kata=kata,
        recent_submissions=recent_submissions,
    )


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("web.index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html", form=form)


@web_bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.index"))


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("web.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created. Welcome!", "success")
        return redirect(url_for("web.index"))
    return render_template("register.html", form=form)


@web_bp.get("/profile")
@login_required
def profile():
    page = request.args.get("page", 1, type=int)
    submissions = (
        Submission.query.filter_by(user_id=current_user.id)
        .order_by(Submission.created_at.desc())
        .paginate(page=page, per_page=25, error_out=False)
    )

    # Aggregate stats
    all_subs = Submission.query.filter_by(user_id=current_user.id).all()
    stats = {
        "total": len(all_subs),
        "passed": sum(1 for s in all_subs if s.status.value == "passed"),
        "failed": sum(1 for s in all_subs if s.status.value == "failed"),
        "katas_attempted": len({s.kata_id for s in all_subs}),
    }

    return render_template("profile.html", submissions=submissions, stats=stats)

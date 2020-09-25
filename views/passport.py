from flask import jsonify, request, session, redirect, url_for, make_response

from models.index import User
from models import db

from . import passport_blu


@passport_blu.route("/passport/register", methods=["GET", "POST"])
def register():
    # 想要实现注册，大体的流程
    # 1. 获取浏览器提交的数据
    # 2. 创建SQLAlchemy对象
    # 3. 保存到数据库
    # 4. 返回响应的json给浏览器

    # 1. 获取参数
    # request.args.get()  # 获取URL中?后面的参数，例如 http://127.0.0.1:5000/login?name=laowang&password=123456
    # request.form.get()  # 获取form表单的数据
    # request.json.get()  # 获取json的数据
    image_code = request.json.get("image_code")
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    smscode = request.json.get("smscode")

    # 判断验证码是否正确，如果不正确，直接返回对应的提示
    print("=====>", image_code, session['image_code'])
    if image_code.lower() != session['image_code'].lower():
        return jsonify({
            "errno": 1003,
            "errmsg": "验证码不正确..."
        })

    # 2. 创建User模型类对象，添加属性
    # 2.1 判断是否存在相同的手机号
    if db.session.query(User).filter(User.mobile == mobile).first():
        ret = {
            "errno": 1001,
            "errmsg": "手机号已经注册过..."
        }

        return jsonify(ret)

    user = User()
    user.nick_name = mobile
    user.password_hash = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
        ret = {
            "errno": 0,
            "errmsg": "登录成功..."
        }
    except Exception as ret:
        db.session.rollback()

        ret = {
            "errno": 1002,
            "errmsg": "注册失败..."
        }

    return jsonify(ret)


@passport_blu.route("/passport/login", methods=["POST"])
def login():
    # 实现登录的大体逻辑
    # 1. 获取手机号、密码
    mobile = request.json.get("mobile")
    password = request.json.get("password")

    # 2. 查询
    user = db.session.query(User).filter(User.mobile == mobile, User.password_hash == password).first()
    if user:
        ret = {
            "errno": 0,
            "errmsg": "登录成功"
        }

        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
    else:
        ret = {
            "errno": 1003,
            "errmsg": "登录失败..."
        }

    # 3. 根据查询的结果返回对应的数据
    return jsonify(ret)


@passport_blu.route("/passport/logout")
def logout():
    session.clear()

    return redirect(url_for("index.index"))


@passport_blu.route("/passport/image_code")
def image_code():
    # with open("./yanzhengma.png", "rb") as f:
    #     image_content = f.read()

    # 调用第三方的包，生成一个随机数的验证码
    # 真正的生成一张图片数据
    from utils.captcha.captcha import captcha

    # 生成验证码
    # hash值  验证码值  图片内容
    name, text, image_content = captcha.generate_captcha()

    print("刚刚生成的验证码：", text)

    session['image_code'] = text  # 存储到session中，也就是说只要是这个用户访问，此时image_code就是整个值，不用的同行得到的是自己需要的值

    return "这里是要返回的图片数据，请实现功能...."
